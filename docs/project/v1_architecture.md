# One-Time Secret (OTP) Sharing — v1 Architecture

## Short description

Secure one-time secret sharing for OTPs, temporary credentials, and short-lived sensitive data. The core goal: the server must never be able to recover plaintext; encryption happens end-to-end in the browser and the backend only stores ciphertext temporarily.

Key properties:
- Client-side encryption (AES-256-GCM via WebCrypto)
- One-time retrieval (atomic consume)
- Short expiration (minutes)
- Protection against link-preview bots
- No user accounts required
- Minimal metadata retention

---

## Table of contents

- [Security principles](#security-principles)
- [Tech stack](#tech-stack-v1)
- [High-level flow](#high-level-flow)
  - [Create secret](#create-secret)
  - [Retrieve secret](#retrieve-secret)
- [Data model](#data-model-postgresql)
- [API design](#api-design-v1)
- [Frontend responsibilities](#frontend-responsibilities-svelte)
- [Cryptography details](#cryptography-details)
- [Security headers](#security-headers-mandatory)
- [Abuse & safety controls](#abuse--safety-controls)
- [Cleanup strategy](#cleanup-strategy)
- [Scope & non-goals](#scope--non-goals)
- [Future extensions (v2+)](#future-extensions-v2)
- [Success criterion](#v1-success-criterion)

---

## Security principles

1. **Zero-knowledge server** — Plaintext and encryption keys never reach the backend.
2. **One-time semantics** — A secret can be retrieved successfully only once.
3. **Ephemeral by default** — Secrets auto-expire after a short TTL.
4. **Link safety** — Encryption key (and claim token) are stored in the URL fragment (#) and are never sent to the server.
5. **Preview-bot resistance** — Claim token required to retrieve the secret.
6. **Minimal attack surface** — No third-party scripts, strict CSP, no analytics.

---

## Tech stack (v1)

- Frontend: Svelte (static SPA)
- Backend: FastAPI
- Database: PostgreSQL
- Crypto: WebCrypto API (AES-256-GCM)
- Transport: HTTPS only

---

## High-level flow

### Create secret

1. User pastes secret (text or JSON) into the web page.
2. Browser generates:
   - Encryption key (32 bytes)
   - AES-GCM nonce (12 bytes)
   - Claim token (32 bytes)
3. Browser encrypts the secret locally.
4. Browser sends only ciphertext + metadata to backend.
5. Backend stores ciphertext with expiration.
6. Browser displays a shareable link containing the secret ID (path) and the encryption key + claim token in the URL fragment.

### Retrieve secret

1. Recipient opens the link.
2. Browser extracts key + claim token from fragment.
3. User clicks Reveal.
4. Browser sends a claim request to backend.
5. Backend atomically:
   - Validates claim token
   - Ensures not expired or consumed
   - Marks secret as consumed
   - Returns ciphertext
6. Browser decrypts locally and displays secret.
7. UI clears plaintext after copy / timeout.

---

## Data model (PostgreSQL)

### Table: one_time_secrets

| Column | Type | Purpose |
|---|---:|---|
| id | TEXT (PK) | Unguessable secret identifier |
| ciphertext | BYTEA | Encrypted payload |
| nonce | BYTEA | AES-GCM nonce |
| aad | BYTEA (nullable) | Additional authenticated data |
| claim_hash | BYTEA | SHA-256 hash of claim token |
| created_at | TIMESTAMPTZ | Creation timestamp |
| expires_at | TIMESTAMPTZ | Expiration timestamp |
| consumed_at | TIMESTAMPTZ (nullable) | One-time consume marker |
| consumed_by_ip | INET (optional) | Minimal audit/debug |
| consumed_ua_hash | BYTEA (optional) | Hashed User-Agent |

Indexes:
- `expires_at`
- `consumed_at`

---

## API design (v1)

### POST /api/secrets
Create a new secret.

Input (JSON):
- `ciphertext_b64u`
- `nonce_b64u`
- `aad_b64u` (optional)
- `claim_hash_b64u`
- `expires_in_seconds`

Output (JSON):
- `id`
- `expires_at`

### GET /api/secrets/{id}/status
Non-consuming availability check.

Output (JSON):
- `exists`
- `consumed`
- `expired`
- `expires_at`

### POST /api/secrets/{id}/claim
Atomic one-time retrieval.

Input (JSON):
- `claim_hash_b64u`

Behavior:
- Fails if expired, already consumed, or claim hash mismatch.
- On success: marks the secret consumed and returns ciphertext.

Atomic SQL pattern:
```sql
UPDATE one_time_secrets
SET consumed_at = now()
WHERE id = :id
  AND consumed_at IS NULL
  AND expires_at > now()
  AND claim_hash = :claim_hash
RETURNING ciphertext, nonce, aad;
```

---

## Frontend responsibilities (Svelte)

- Create page (`/`): accept plaintext input, generate key/nonce/claim token, encrypt via WebCrypto, POST encrypted payload, and generate share link. Warn user about one-time behavior.
- Retrieve page (`/s/:id`): parse fragment (key, claim_token), remove fragment from address bar, show availability status, require explicit Reveal click, POST claim, decrypt locally, copy-to-clipboard, and auto-clear plaintext from memory.

---

## Cryptography details

- Algorithm: AES-256-GCM
- Key: 32 bytes random
- Nonce: 12 bytes random
- Claim token hash: SHA-256
- Encoding: Base64URL
- Optional AAD: versioned metadata (v1)

---

## Security headers (mandatory)

Apply to all pages and API responses:
- `Strict-Transport-Security`
- `Content-Security-Policy` (no third-party scripts)
- `Referrer-Policy: no-referrer`
- `Cache-Control: no-store`
- `X-Content-Type-Options: nosniff`
- `Frame-Ancestors: none`

---

## Abuse & safety controls

- Payload size limits (e.g. ≤ 8–32 KB)
- Rate limiting (create + claim)
- Unguessable IDs (≥128 bits entropy)
- Generic error responses (avoid enumeration)
- No request/response body logging

---

## Cleanup strategy

Scheduled background job to remove expired or consumed secrets:

```sql
DELETE FROM one_time_secrets
WHERE expires_at <= now()
   OR consumed_at IS NOT NULL;
```

Retention window for consumed secrets:
- Immediate delete (preferred)
- Short grace period (debug only)

---

## Scope & non-goals

Included in v1:
- One-time secret sharing
- OTP / short secrets
- Single recipient
- Manual reveal
- Stateless frontend

Non-goals for v1:
- Chat or messaging
- User accounts
- Long-term storage
- Multi-device synchronization
- Metadata obfuscation beyond basics

---

## Future extensions (v2+)

- Optional passphrase
- Enterprise auth / SSO
- Secure one-time chat
- Delivery receipts
- Client verification codes
- Encrypted file blobs

---

## v1 success criterion

A compromised database or backend operator cannot recover any plaintext secrets, and a leaked link cannot be used more than once.