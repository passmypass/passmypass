# PassMyPass API - Implementation Specification

> Feature: Public API Access for Programmatic Secret Sharing

## Overview

This document outlines the implementation plan for adding a public API to PassMyPass, enabling developers to programmatically create and retrieve one-time secrets.

---

## API Design

### Authentication

Two modes of operation:

1. **Anonymous (rate-limited)**: Same as web UI, strict rate limits
2. **API Key (higher limits)**: Authenticated requests with registered API keys

### Endpoints

#### Create Secret

```
POST /api/v1/secrets
Content-Type: application/json
Authorization: Bearer <api_key>  (optional)

{
  "content": "my-secret-password",
  "ttl_minutes": 60,
  "password": "optional-password"  // Optional
}

Response 201:
{
  "id": "abc123",
  "url": "https://passmypass.com/s/abc123#<key>",
  "expires_at": "2026-01-20T12:00:00Z",
  "password_protected": false
}
```

#### Check Secret Status

```
GET /api/v1/secrets/{id}/status
Authorization: Bearer <api_key>  (optional)

Response 200:
{
  "exists": true,
  "consumed": false,
  "expires_at": "2026-01-20T12:00:00Z",
  "password_protected": true
}
```

#### Retrieve Secret (One-time)

```
POST /api/v1/secrets/{id}/claim
Content-Type: application/json

{
  "claim_token": "<token-from-url-fragment>",
  "password": "optional-password"  // If password protected
}

Response 200:
{
  "content": "my-secret-password",
  "claimed_at": "2026-01-20T11:30:00Z"
}
```

---

## Database Changes

### New Table: `api_keys`

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 of the API key
    name VARCHAR(100) NOT NULL,             -- User-friendly name
    email VARCHAR(255),                      -- Contact email (optional)
    rate_limit_per_minute INTEGER DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,

    -- Usage tracking
    total_secrets_created INTEGER DEFAULT 0,
    total_secrets_claimed INTEGER DEFAULT 0
);

CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
```

### Changes to `secrets` Table

```sql
-- Add column to track which API key created the secret (optional, for analytics)
ALTER TABLE secrets ADD COLUMN created_by_api_key UUID REFERENCES api_keys(id);
```

---

## Implementation Details

### 1. API Key Generation & Storage

```python
# server/app/api_keys.py

import secrets
import hashlib
from datetime import datetime

def generate_api_key() -> tuple[str, str]:
    """Generate an API key and its hash.

    Returns:
        (plain_key, key_hash) - plain_key shown once to user, hash stored in DB
    """
    # Format: pmp_<32 random hex chars>
    plain_key = f"pmp_{secrets.token_hex(16)}"
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()
    return plain_key, key_hash

def verify_api_key(plain_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash."""
    computed_hash = hashlib.sha256(plain_key.encode()).hexdigest()
    return secrets.compare_digest(computed_hash, stored_hash)
```

### 2. Rate Limiting by API Key

```python
# server/app/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address

def get_rate_limit_key(request):
    """Get rate limit key - API key if present, otherwise IP."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        api_key = auth_header[7:]
        # Return API key hash for rate limiting
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    return get_remote_address(request)

limiter = Limiter(key_func=get_rate_limit_key)
```

### 3. Authentication Middleware

```python
# server/app/middleware.py

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[APIKey]:
    """Validate API key if provided."""
    if not credentials:
        return None  # Anonymous access

    key_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()

    result = await db.execute(
        select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Update last used timestamp
    api_key.last_used_at = datetime.utcnow()
    await db.commit()

    return api_key
```

### 4. API Routes

```python
# server/app/routes_v1.py

from fastapi import APIRouter, Depends, HTTPException
from .middleware import get_api_key
from .schemas import SecretCreateAPI, SecretResponse

router = APIRouter(prefix="/api/v1", tags=["API v1"])

@router.post("/secrets", response_model=SecretResponse)
@limiter.limit("100/minute")  # Higher limit for API
async def create_secret_api(
    request: Request,
    data: SecretCreateAPI,
    api_key: Optional[APIKey] = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new secret via API.

    Unlike the web UI, this endpoint handles encryption server-side
    for convenience. For maximum security, use client-side encryption.
    """
    # Generate encryption key and claim token
    encryption_key = secrets.token_bytes(32)
    claim_token = secrets.token_urlsafe(32)

    # Encrypt the content
    ciphertext, nonce, aad = encrypt_content(
        data.content.encode(),
        encryption_key,
        data.password
    )

    # Store in database
    secret = Secret(
        ciphertext=ciphertext,
        nonce=nonce,
        aad=aad,
        claim_hash=hashlib.sha256(claim_token.encode()).hexdigest(),
        expires_at=datetime.utcnow() + timedelta(minutes=data.ttl_minutes),
        created_by_api_key=api_key.id if api_key else None
    )
    db.add(secret)
    await db.commit()

    # Build shareable URL
    key_b64 = base64.urlsafe_b64encode(encryption_key).decode()
    fragment = f"{key_b64}.{claim_token}"
    url = f"https://passmypass.com/s/{secret.id}#{fragment}"

    return SecretResponse(
        id=str(secret.id),
        url=url,
        expires_at=secret.expires_at,
        password_protected=bool(data.password)
    )
```

---

## CLI Tool

A command-line tool for easy secret sharing:

```bash
# Install globally
npm install -g passmypass-cli

# Or use with npx
npx passmypass "my-secret-password"
```

### CLI Implementation

```typescript
// packages/cli/src/index.ts

#!/usr/bin/env node

import { program } from 'commander';
import { encrypt } from './crypto';

const API_URL = 'https://passmypass.com/api/v1';

program
  .name('passmypass')
  .description('Share one-time secrets securely')
  .version('1.0.0');

program
  .argument('[secret]', 'Secret to share (or pipe from stdin)')
  .option('-t, --ttl <minutes>', 'Time to live in minutes', '60')
  .option('-p, --password <password>', 'Password protect the secret')
  .option('-k, --api-key <key>', 'API key for higher rate limits')
  .action(async (secret, options) => {
    // Read from stdin if no argument
    if (!secret) {
      secret = await readStdin();
    }

    const response = await fetch(`${API_URL}/secrets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(options.apiKey && { 'Authorization': `Bearer ${options.apiKey}` })
      },
      body: JSON.stringify({
        content: secret,
        ttl_minutes: parseInt(options.ttl),
        password: options.password
      })
    });

    const data = await response.json();
    console.log(`\n🔐 Secret created!\n`);
    console.log(`URL: ${data.url}`);
    console.log(`Expires: ${new Date(data.expires_at).toLocaleString()}`);
    if (data.password_protected) {
      console.log(`⚠️  Password protected`);
    }
  });

program.parse();
```

### Usage Examples

```bash
# Simple secret
passmypass "my-api-key-123"

# With password protection
passmypass -p "hunter2" "database-password"

# Custom TTL (24 hours)
passmypass -t 1440 "temporary-token"

# From stdin (useful for piping)
echo "secret" | passmypass

# With API key
passmypass -k "pmp_abc123..." "high-volume-secret"

# From file
cat credentials.json | passmypass -t 60
```

---

## Security Considerations

### Server-Side vs Client-Side Encryption

The API offers **server-side encryption** for convenience:
- Easier for developers to integrate
- Secret content is briefly in server memory during encryption
- Still zero-knowledge after encryption (server can't decrypt)

For **maximum security**, provide client-side encryption option:

```bash
# Client-side encryption mode (key never leaves client)
passmypass --client-encrypt "super-secret"
```

This would:
1. Generate encryption key locally
2. Encrypt content locally
3. Send only ciphertext to server
4. Return URL with key in fragment

### Rate Limits

| Mode | Create | Claim |
|------|--------|-------|
| Anonymous (IP) | 10/min | 30/min |
| API Key (default) | 100/min | 300/min |
| API Key (premium) | 1000/min | 3000/min |

### API Key Security

- Keys are hashed (SHA-256) before storage
- Plain key shown only once at creation
- Keys can be revoked instantly
- Usage logging for abuse detection

---

## Pydantic Schemas

```python
# server/app/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SecretCreateAPI(BaseModel):
    content: str = Field(..., min_length=1, max_length=100_000)
    ttl_minutes: int = Field(60, ge=5, le=10080)  # 5 min to 7 days
    password: Optional[str] = Field(None, min_length=1, max_length=100)

class SecretResponse(BaseModel):
    id: str
    url: str
    expires_at: datetime
    password_protected: bool

class SecretStatusResponse(BaseModel):
    exists: bool
    consumed: bool
    expires_at: Optional[datetime]
    password_protected: bool

class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None)

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # Plain key, shown only once
    created_at: datetime
```

---

## Future Enhancements

1. **Webhooks**: Notify when secret is claimed
2. **Usage Dashboard**: View API key usage statistics
3. **SDKs**: Python, JavaScript, Go client libraries
4. **Batch Operations**: Create multiple secrets in one call

---

## Implementation Priority

1. **Phase 1**: Basic API endpoints (create, status, claim)
2. **Phase 2**: API key authentication and rate limits
3. **Phase 3**: CLI tool
4. **Phase 4**: Documentation site and SDKs

---

*Last updated: January 2026*
