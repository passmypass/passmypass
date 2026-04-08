# PassMyPass

**Zero-knowledge encrypted secret sharing and ephemeral chat.**

Share passwords, API keys, and sensitive data through self-destructing encrypted links. The server never sees your data.

[passmypass.com](https://passmypass.com)

## Features

- **Zero-Knowledge Encryption** - AES-256-GCM encryption happens entirely in your browser. The encryption key stays in the URL fragment and is never sent to the server.
- **One-Time Viewing** - Each secret link works exactly once. After the recipient views it, the secret is permanently destroyed.
- **Auto-Expiring Links** - Set links to expire from 5 minutes to 24 hours. Unread secrets are automatically destroyed.
- **Password Protection** - Optional second layer using PBKDF2 (100,000 iterations). Even intercepting the link is not enough without the password.
- **Encrypted Chat Rooms** - Ephemeral 1-on-1 E2E encrypted chat rooms that auto-destruct after 10 minutes.
- **QR Code Generation** - Generate QR codes for share links for easy in-person sharing.
- **No Account Required** - No sign-up, no cookies, no tracking.
- **Developer API** - REST API with interactive docs at `/api/docs`.

## How It Works

1. You enter a secret in your browser
2. Your browser encrypts it with AES-256-GCM and generates a unique link
3. The encryption key lives in the URL fragment (`#`) which is never sent to the server
4. The server stores only ciphertext it cannot decrypt
5. The recipient opens the link, their browser decrypts it locally, and the secret is destroyed

## Tech Stack

- **Frontend**: Svelte 5 + SvelteKit + Tailwind CSS 4
- **Backend**: FastAPI (Python) + PostgreSQL
- **Crypto**: WebCrypto API (AES-256-GCM, SHA-256, PBKDF2)
- **Hosting**: Render

## Self-Hosting

```bash
# Clone the repo
git clone https://github.com/passmypass/passmypass.git
cd passmypass

# Start with Docker Compose
docker compose up -d
```

The app will be available at `http://localhost:8000`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/passmypass` | PostgreSQL connection string |
| `MAX_TTL_SECONDS` | `86400` | Maximum secret expiry (24 hours) |
| `RATE_LIMIT_CREATE` | `30/minute` | Rate limit for creating secrets |
| `RATE_LIMIT_CLAIM` | `60/minute` | Rate limit for claiming secrets |

## Development

### Backend

```bash
cd server
docker compose up -d          # Start PostgreSQL
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
npm install
npm run dev    # Runs on :5173, proxies /api to :8000
```

### API Documentation

Interactive API docs are available at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI spec: `http://localhost:8000/api/openapi.json`

## Security

PassMyPass uses a zero-knowledge architecture. The server mathematically cannot decrypt your secrets. For full technical details, see [Security Architecture](https://passmypass.com/security/).

To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

[AGPL-3.0](LICENSE) - If you modify and host this code as a service, you must share your changes.
