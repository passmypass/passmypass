# PassMyPass Security - Plain English Explanation

## The Big Question: What Does the Server Actually Do?

### Short Answer

The server is a **"blind courier"** - it holds an encrypted package but has no idea what's inside and no way to open it.

### What the Server Does

1. **Stores encrypted blobs** - Random-looking bytes that mean nothing without the key
2. **Generates a unique ID** - A random identifier for each secret
3. **Tracks expiration** - Deletes secrets after they expire
4. **Enforces one-time access** - Ensures the secret can only be retrieved once
5. **Rate limiting** - Prevents abuse

### What the Server Does NOT Do

1. **Does NOT generate encryption keys** - Your browser does this
2. **Does NOT encrypt your secret** - Your browser does this
3. **Does NOT decrypt anything** - It can't, it doesn't have the key
4. **Does NOT see your password** - Ever. Not even for a millisecond.
5. **Does NOT provide any key** - Zero keys come from the server

---

## Do We Store the Password?

### No. We Store Encrypted Garbage.

Here's what gets stored in our database:

```
┌─────────────────────────────────────────────────────────────────┐
│ DATABASE RECORD                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ id: "SibA5_XbH9mtsXz1jA3vwg"                                    │
│                                                                 │
│ ciphertext: 0x8f3a2b1c9e8d7f6a5b4c3d2e1f0a9b8c...              │
│             ↑                                                   │
│             This looks like random noise.                       │
│             Without the key, it IS random noise.                │
│                                                                 │
│ nonce: 0x1a2b3c4d5e6f7a8b9c0d1e2f                               │
│        ↑                                                        │
│        Random value needed for decryption (safe to store)       │
│                                                                 │
│ claim_hash: 0x9f8e7d6c5b4a3928... (SHA-256 hash)                │
│             ↑                                                   │
│             Hash of the claim token - cannot be reversed        │
│                                                                 │
│ expires_at: 2024-01-15 10:40:00                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**If a hacker steals our entire database, they get:**
- Encrypted blobs they can't decrypt
- Random IDs that mean nothing
- Hashes they can't reverse
- Expiration timestamps

**They do NOT get:**
- Your passwords
- The encryption keys
- Any way to decrypt anything

---

## Where Are the Keys?

### The Key Lives ONLY in the URL

```
https://passmypass.com/s/ABC123#KEY_IS_HERE.TOKEN_IS_HERE
                               └──────────┬──────────────┘
                                          │
                         This part (after #) is NEVER sent to the server.
                         It only exists in the browser.
```

**This is not our invention** - it's how the web works:

> According to RFC 3986 (the URL standard), browsers MUST NOT send
> the fragment (everything after #) to servers. This is a 25+ year
> old web standard that all browsers follow.

When you visit `https://example.com/page#section`, the server only sees `/page`. It has no idea `#section` exists.

---

## The Complete Picture

```
    YOUR BROWSER                           OUR SERVER
    ════════════                           ══════════

    1. You type: "MyP@ssw0rd!"
           │
           ▼
    2. Browser generates random key
       (server never sees this)
           │
           ▼
    3. Browser encrypts password
       "MyP@ssw0rd!" → 0x8f3a2b1c9e...
           │
           ▼
    4. Browser sends ONLY the          ──→  5. Server stores the
       encrypted blob to server              encrypted blob
       (not the key, not the password)       (has no idea what's inside)
           │
           ▼
    6. Browser creates URL:
       example.com/s/id#key.token
       ─────────────────────────
       Only the "id" part was
       sent to server. The key
       stays in the URL fragment.
           │
           ▼
    7. You share the full URL
       with someone
                    │
                    ▼
              RECIPIENT'S BROWSER
              ═══════════════════

    8. Opens URL, extracts key from #fragment
       (server still never sees the key)
           │
           ▼
    9. Browser requests encrypted   ──→  10. Server returns the
       blob from server                      encrypted blob and
                                             marks it as "consumed"
           │
           ▼
    11. Browser decrypts using key
        0x8f3a2b1c9e... → "MyP@ssw0rd!"
           │
           ▼
    12. Recipient sees: "MyP@ssw0rd!"
```

---

## How Secure Is This Approach?

### Security Rating: Very High

This is called **"Zero-Knowledge Architecture"** and it's the gold standard for privacy-focused applications. It's the same approach used by:

- **Signal** (messaging)
- **ProtonMail** (email)
- **1Password** (password manager)
- **Bitwarden** (password manager)

### Why It's Secure

| Threat | Are We Protected? | How? |
|--------|-------------------|------|
| Server gets hacked | ✅ Yes | Hackers only get encrypted blobs |
| Database leaked | ✅ Yes | No keys stored, nothing to decrypt |
| Malicious server admin | ✅ Yes | Admin can't see keys or passwords |
| Government requests data | ✅ Yes | We can only provide encrypted blobs |
| Network eavesdropping | ✅ Yes | HTTPS + key never transmitted |
| Someone guesses the URL | ✅ Yes | 256-bit key = impossible to guess |
| Someone guesses the ID | ✅ Yes | Need both ID AND key AND claim token |

### The Math Behind "Impossible to Guess"

The encryption key is 256 bits. That means there are:

```
2^256 = 115,792,089,237,316,195,423,570,985,008,687,907,853,269,984,665,640,564,039,457,584,007,913,129,639,936

possible keys.
```

If you could try **1 trillion keys per second**, it would take:

```
3.67 × 10^57 years
```

The universe is only 13.8 billion years old. You'd need to try for **quadrillions of universe lifetimes**.

---

## Common Questions

### Q: But the server COULD be modified to steal passwords?

**A:** Only if we push malicious JavaScript to your browser. This is true for ANY web application. Mitigations:
- Open source code - you can audit it
- Self-host if you don't trust us
- Use browser extensions that verify script integrity

### Q: What if someone intercepts the URL I share?

**A:** Then they have everything needed to view the secret once. This is why:
- Share URLs through secure channels (Signal, encrypted email)
- Secrets expire quickly
- One-time view prevents ongoing access

### Q: Is AES-256 actually secure?

**A:** AES-256 is approved by the NSA for TOP SECRET classified information. It's used by:
- Banks
- Governments
- Military
- Every major tech company

No one has ever broken AES-256.

### Q: What about quantum computers?

**A:** Current quantum computers can't break AES-256. Future quantum computers using Grover's algorithm would reduce security to ~128 bits - still considered secure. We'd have years of warning to upgrade if needed.

---

## Comparison: Us vs. Traditional Services

### Traditional "Secret Sharing" (like OneTimeSecret)

```
Your Browser          Their Server
────────────          ────────────
"MyPassword"    ──→   Receives "MyPassword"
                      Encrypts it
                      Stores encrypted version

                      ⚠️ SERVER SEES YOUR PASSWORD
                      ⚠️ Server admin can read it
                      ⚠️ Hack = all passwords exposed
```

### PassMyPass (Zero-Knowledge)

```
Your Browser          Our Server
────────────          ──────────
"MyPassword"
     │
Encrypt locally
     │
0x8f3a2b...     ──→   Receives 0x8f3a2b...
                      Stores 0x8f3a2b...

                      ✅ Server NEVER sees password
                      ✅ Admin cannot read anything
                      ✅ Hack = only encrypted blobs
```

---

## Summary

| Question | Answer |
|----------|--------|
| Does the server store the password? | No, only encrypted blob |
| Does the server provide any key? | No, browser generates it |
| Can the server decrypt secrets? | No, it doesn't have the key |
| Where is the key? | Only in URL fragment (never sent to server) |
| How secure is this? | Very - same approach as Signal, ProtonMail |
| What if server is hacked? | Attackers get useless encrypted data |
| Can server admin read secrets? | No, mathematically impossible |

**Bottom Line:** Even if someone completely compromises our server, steals our database, and has unlimited computing power - they still cannot read your secrets. The encryption key exists only in the URL you share, and we never see it.
