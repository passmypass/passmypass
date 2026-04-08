# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in PassMyPass, please report it responsibly via our [contact form](https://passmypass.com/contact/).

Select "Security Vulnerability Report" as the subject.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

### What to expect

- We will acknowledge your report within 48 hours
- We will provide an estimated timeline for a fix
- We will credit you in the fix (unless you prefer anonymity)

## Security Architecture

PassMyPass uses a zero-knowledge architecture. All encryption happens client-side using AES-256-GCM via the WebCrypto API. The server never sees plaintext data or encryption keys.

For full technical details, see [passmypass.com/security](https://passmypass.com/security/).

## Scope

The following are in scope for security reports:

- Cryptographic weaknesses in the client-side encryption
- Server-side vulnerabilities (API, WebSocket, database)
- Authentication/authorization bypasses
- Information disclosure (plaintext leaks, key leaks)
- Cross-site scripting (XSS) or injection attacks
- Rate limiting bypasses

The following are out of scope:

- Social engineering attacks
- Denial of service (DoS) attacks
- Issues in third-party dependencies (report to the upstream project)
- Issues requiring physical access to a user's device
