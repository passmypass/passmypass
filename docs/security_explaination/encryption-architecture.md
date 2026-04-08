# PassMyPass Encryption Architecture

This document provides a detailed explanation of how PassMyPass encrypts and decrypts secrets, what data is sent to the server, and why this architecture ensures **zero-knowledge security**.

## Table of Contents

1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Creating a Secret (Encryption Flow)](#creating-a-secret-encryption-flow)
4. [Retrieving a Secret (Decryption Flow)](#retrieving-a-secret-decryption-flow)
5. [URL Structure](#url-structure)
6. [What the Server Knows vs. Doesn't Know](#what-the-server-knows-vs-doesnt-know)
7. [Security Properties](#security-properties)
8. [Cryptographic Details](#cryptographic-details)

---

## Overview

PassMyPass is a **zero-knowledge** secret sharing application. This means:

- The server **never** sees your plaintext secret
- The server **cannot** decrypt your secret (it doesn't have the key)
- All encryption/decryption happens **in your browser** using the Web Crypto API
- The encryption key is stored **only in the URL fragment** (`#...`), which browsers never send to servers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ZERO-KNOWLEDGE MODEL                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   YOUR BROWSER                          SERVER                              │
│   ────────────                          ──────                              │
│   ✓ Sees plaintext secret               ✗ Never sees plaintext              │
│   ✓ Generates encryption key            ✗ Never sees encryption key         │
│   ✓ Encrypts before sending             ✓ Only stores encrypted blob        │
│   ✓ Decrypts after receiving            ✗ Cannot decrypt                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### AES-256-GCM
- **AES** (Advanced Encryption Standard) - Industry standard symmetric encryption
- **256** - Key size in bits (256 bits = 32 bytes)
- **GCM** (Galois/Counter Mode) - Authenticated encryption mode that provides both confidentiality and integrity

### Encryption Key
- A randomly generated 256-bit (32 bytes) key
- Generated in the browser using `crypto.getRandomValues()`
- Used to encrypt and decrypt the secret
- **Never sent to the server**

### Claim Token
- A randomly generated 256-bit (32 bytes) token
- Acts as a "password" to claim/retrieve the secret
- Only its **hash** is sent to the server
- Prevents unauthorized access even if someone knows the secret ID

### Nonce (Number Used Once)
- A random 96-bit (12 bytes) value
- Required by AES-GCM to ensure the same plaintext produces different ciphertext
- Can be stored publicly (sent to server)

### AAD (Additional Authenticated Data)
- Contains metadata like timestamp
- Authenticated but not encrypted
- Ensures the ciphertext can't be tampered with

---

## Creating a Secret (Encryption Flow)

Here's the step-by-step process when you create a secret:

### Step 1: Generate Cryptographic Materials (Browser)

```
┌─────────────────────────────────────────────────────────────────┐
│ BROWSER: Generate random values                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   encryptionKey = random 32 bytes (256 bits)                    │
│   claimToken    = random 32 bytes (256 bits)                    │
│   nonce         = random 12 bytes (96 bits)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Prepare AAD (Browser)

```javascript
aad = JSON.stringify({
  version: 1,
  created: "2024-01-15T10:30:00.000Z"
})
```

### Step 3: Encrypt the Secret (Browser)

```
┌─────────────────────────────────────────────────────────────────┐
│ BROWSER: AES-256-GCM Encryption                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   INPUT:                                                        │
│   ├── plaintext     = "my-secret-password"                      │
│   ├── encryptionKey = [32 random bytes]                         │
│   ├── nonce         = [12 random bytes]                         │
│   └── aad           = '{"version":1,"created":"..."}'           │
│                                                                 │
│   OUTPUT:                                                       │
│   └── ciphertext    = [encrypted bytes + 16-byte auth tag]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: Hash the Claim Token (Browser)

```
┌─────────────────────────────────────────────────────────────────┐
│ BROWSER: SHA-256 Hash                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   claimHash = SHA256(claimToken)                                │
│                                                                 │
│   This hash is sent to the server.                              │
│   The original claimToken stays in the browser.                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 5: Send to Server (Browser → Server)

```
┌─────────────────────────────────────────────────────────────────┐
│ HTTP POST /api/secrets                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   REQUEST BODY (what the server receives):                      │
│   {                                                             │
│     "ciphertext_b64u": "encrypted-data-base64url",              │
│     "nonce_b64u": "random-nonce-base64url",                     │
│     "aad_b64u": "metadata-base64url",                           │
│     "claim_hash_b64u": "sha256-of-claim-token-base64url",       │
│     "expires_in_seconds": 600                                   │
│   }                                                             │
│                                                                 │
│   ⚠️  NOT SENT: encryptionKey, claimToken, plaintext            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 6: Server Response

```
┌─────────────────────────────────────────────────────────────────┐
│ HTTP 201 Created                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   RESPONSE BODY:                                                │
│   {                                                             │
│     "id": "SibA5_XbH9mtsXz1jA3vwg",                             │
│     "expires_at": "2024-01-15T10:40:00.000Z"                    │
│   }                                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 7: Generate Share URL (Browser)

```
┌─────────────────────────────────────────────────────────────────┐
│ BROWSER: Construct URL                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   https://example.com/s/{id}#{encryptionKey}.{claimToken}       │
│                              ▲                                  │
│                              │                                  │
│                   URL FRAGMENT (never sent to server)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Retrieving a Secret (Decryption Flow)

### Step 1: Parse URL (Recipient's Browser)

```
┌─────────────────────────────────────────────────────────────────┐
│ BROWSER: Extract from URL                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   URL: https://example.com/s/ABC123#key.token                   │
│                                                                 │
│   Extracted:                                                    │
│   ├── secretId      = "ABC123"    (from path)                   │
│   ├── encryptionKey = [32 bytes]  (from fragment, before .)    │
│   └── claimToken    = [32 bytes]  (from fragment, after .)     │
│                                                                 │
│   ⚠️  Browser immediately clears the URL fragment from history  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 2: Check Secret Status (Browser → Server)

```
┌─────────────────────────────────────────────────────────────────┐
│ HTTP GET /api/secrets/{id}/status                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   This is a non-consuming check to see if the secret exists     │
│   and hasn't been viewed or expired yet.                        │
│                                                                 │
│   RESPONSE:                                                     │
│   {                                                             │
│     "exists": true,                                             │
│     "consumed": false,                                          │
│     "expired": false,                                           │
│     "expires_at": "2024-01-15T10:40:00.000Z"                    │
│   }                                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3: Claim the Secret (Browser → Server)

```
┌─────────────────────────────────────────────────────────────────┐
│ HTTP POST /api/secrets/{id}/claim                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   REQUEST BODY:                                                 │
│   {                                                             │
│     "claim_token_b64u": "original-claim-token-base64url"        │
│   }                                                             │
│                                                                 │
│   SERVER PROCESS:                                               │
│   1. Compute SHA256(claim_token)                                │
│   2. Compare with stored claim_hash                             │
│   3. If match AND not consumed AND not expired:                 │
│      - Mark as consumed (atomic operation)                      │
│      - Return encrypted data                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 4: Server Response with Encrypted Data

```
┌─────────────────────────────────────────────────────────────────┐
│ HTTP 200 OK                                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   RESPONSE BODY:                                                │
│   {                                                             │
│     "ciphertext_b64u": "encrypted-data-base64url",              │
│     "nonce_b64u": "nonce-base64url",                            │
│     "aad_b64u": "metadata-base64url"                            │
│   }                                                             │
│                                                                 │
│   ⚠️  Server returns encrypted blob - it cannot read it!        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 5: Decrypt in Browser

```
┌─────────────────────────────────────────────────────────────────┐
│ BROWSER: AES-256-GCM Decryption                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   INPUT:                                                        │
│   ├── ciphertext    = [from server response]                    │
│   ├── encryptionKey = [from URL fragment - never sent!]         │
│   ├── nonce         = [from server response]                    │
│   └── aad           = [from server response]                    │
│                                                                 │
│   OUTPUT:                                                       │
│   └── plaintext     = "my-secret-password"                      │
│                                                                 │
│   If AAD or ciphertext was tampered with, decryption fails!     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## URL Structure

```
https://passmypass.com/s/SibA5_XbH9mtsXz1jA3vwg#k743xgPbT9VaENBi6rOW8EkUIFeNDUP9xEf1Sbn8l8g.Z_JfPrBkmDkK8sAEGp7An5nRhknTPg_9jEm2TImC0wE
└──────────┬──────────┘ └──────────┬──────────┘ └─────────────────────────────────┬─────────────────────────────────┘
        Domain                  Secret ID                              URL Fragment (never sent to server)
                            (sent to server)                    ┌──────────────┴──────────────┐
                                                         Encryption Key              Claim Token
                                                          (43 chars)                  (43 chars)
```

### Why Use URL Fragments?

The URL fragment (everything after `#`) has a special property defined in RFC 3986:

> **Browsers NEVER send the fragment to the server in HTTP requests.**

This is a fundamental web standard that all browsers follow. When you visit:
```
https://example.com/page#section
```

The server only sees:
```
GET /page HTTP/1.1
Host: example.com
```

This makes fragments perfect for storing sensitive client-side data.

---

## What the Server Knows vs. Doesn't Know

### Server HAS Access To:

| Data | Purpose | Risk Level |
|------|---------|------------|
| Ciphertext | Encrypted blob | Useless without key |
| Nonce | Required for decryption | Public knowledge is safe |
| AAD | Metadata | Contains only timestamp |
| Claim Hash | SHA-256 of claim token | Cannot reverse to get token |
| Secret ID | Database identifier | Random, unguessable |
| Client IP | Audit log | Standard web traffic |
| Expiration time | Auto-cleanup | Not sensitive |

### Server NEVER Has Access To:

| Data | Why Not |
|------|---------|
| Plaintext secret | Never leaves browser unencrypted |
| Encryption key | Only in URL fragment |
| Claim token | Only its hash is stored |
| Any way to decrypt | Missing the key entirely |

### Visual Summary:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA FLOW SUMMARY                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SENDER'S BROWSER                                              │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ "my-secret-password"                                    │   │
│   │         │                                               │   │
│   │         ▼                                               │   │
│   │ ┌─────────────────┐   ┌─────────────────┐               │   │
│   │ │ Encryption Key  │ + │ AES-256-GCM     │               │   │
│   │ │ (random 32B)    │   │ Encrypt         │               │   │
│   │ └─────────────────┘   └────────┬────────┘               │   │
│   │                                │                        │   │
│   │                                ▼                        │   │
│   │                        [Ciphertext]                     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                    │                            │
│                    ┌───────────────┼───────────────┐            │
│                    │               │               │            │
│                    ▼               ▼               ▼            │
│              ┌──────────┐   ┌──────────┐   ┌──────────────┐     │
│              │ To Server│   │ To URL # │   │ To URL #     │     │
│              │Ciphertext│   │   Key    │   │ Claim Token  │     │
│              │  Nonce   │   │          │   │              │     │
│              │   AAD    │   │          │   │              │     │
│              │ClaimHash │   │          │   │              │     │
│              └──────────┘   └──────────┘   └──────────────┘     │
│                    │               │               │            │
│                    │               └───────┬───────┘            │
│                    │                       │                    │
│                    ▼                       ▼                    │
│   ┌─────────────────────┐   ┌─────────────────────────────┐     │
│   │      SERVER         │   │    SHARE LINK               │     │
│   │  (stores encrypted  │   │  example.com/s/id#key.token │     │
│   │   blob only)        │   │  (key NEVER sent to server) │     │
│   └─────────────────────┘   └─────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Properties

### 1. Confidentiality
- Only someone with the full URL (including fragment) can decrypt
- Server compromise doesn't expose plaintext secrets
- Database leak only reveals encrypted blobs

### 2. Integrity
- AES-GCM includes authentication tag
- Any tampering with ciphertext or AAD causes decryption to fail
- Protects against data corruption and manipulation

### 3. One-Time Access
- Atomic database operation ensures exactly one successful claim
- Race conditions handled at database level with `UPDATE ... WHERE ... RETURNING`
- Once consumed, the encrypted data is scheduled for deletion

### 4. Claim Token Protection
- Token is required to claim the secret (not just the ID)
- Only hash stored on server - original token needed to claim
- Protects against ID enumeration attacks

### 5. Forward Secrecy
- Each secret has its own random key
- Compromising one secret doesn't affect others
- No master key exists

---

## Cryptographic Details

### Algorithms Used

| Purpose | Algorithm | Size |
|---------|-----------|------|
| Encryption | AES-256-GCM | 256-bit key |
| Key Derivation | None (random key) | N/A |
| Hashing | SHA-256 | 256-bit output |
| Random Generation | Web Crypto `getRandomValues()` | CSPRNG |

### Key Sizes

| Component | Size (bits) | Size (bytes) | Base64URL Length |
|-----------|-------------|--------------|------------------|
| Encryption Key | 256 | 32 | 43 chars |
| Claim Token | 256 | 32 | 43 chars |
| Claim Hash | 256 | 32 | 43 chars |
| Nonce | 96 | 12 | 16 chars |
| Secret ID | 128 | 16 | 22 chars |

### Why These Choices?

1. **AES-256-GCM**: NIST-approved, widely analyzed, provides authenticated encryption
2. **256-bit keys**: Future-proof against quantum computing threats (Grover's algorithm)
3. **96-bit nonce**: Standard for GCM, sufficient for random nonces
4. **128-bit Secret ID**: 3.4×10³⁸ possibilities - impossible to guess

---

## Comparison with Other Services

| Feature | PassMyPass | OneTimeSecret | PrivateBin |
|---------|------------|---------------|------------|
| Encryption Location | Client | Server | Client |
| Server Sees Plaintext | No | Yes | No |
| Key in URL Fragment | Yes | No | Yes |
| Open Source | Yes | Yes | Yes |
| Zero-Knowledge | Yes | No | Yes |

---

## Threat Model

### Protected Against:
- Server compromise
- Database breaches
- Man-in-the-middle (with HTTPS)
- Replay attacks
- ID enumeration
- Timing attacks on claim

### NOT Protected Against:
- Compromised recipient device
- URL shared in plain text (e.g., unencrypted email)
- Malicious browser extensions
- Shoulder surfing
- Rubber hose cryptanalysis 🔧

---

## Code References

- Encryption implementation: `src/lib/crypto.ts`
- API client: `src/lib/api.ts`
- Server routes: `server/app/routes.py`
- Database model: `server/app/models.py`
