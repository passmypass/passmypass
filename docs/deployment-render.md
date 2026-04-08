# Deploying to Render.com

## Overview

Three services on Render:
1. **PostgreSQL** - Managed database
2. **Web Service** - FastAPI backend (`passmypass-api.onrender.com`)
3. **Static Site** - SvelteKit frontend (`passmypass-front.onrender.com`)

## 1. PostgreSQL Database

Create a new PostgreSQL instance. Copy the **Internal Database URL** for the backend.

## 2. Backend (Web Service)

**Settings:**
- Root Directory: `server`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
```
DATABASE_URL=<internal-postgres-url>
```

Note: Replace `postgresql://` prefix with `postgresql+asyncpg://` in the URL.

## 3. Frontend (Static Site)

**Settings:**
- Build Command: `npm install && npm run build`
- Publish Directory: `build`

**SPA Rewrite Rule (Required):**

This is critical for client-side routing to work (e.g., `/s/[id]` secret links).

1. Go to **passmypass-front** → **Redirects/Rewrites** in the left sidebar
2. Add a rewrite rule:

| Source | Destination | Action |
|--------|-------------|--------|
| `/*` | `/200.html` | Rewrite |

**Note on Assets:** We use `200.html` as the destination because it's the standard SvelteKit SPA fallback name. Using `/index.html` as a fallback can cause issues if the homepage is prerendered with relative asset paths. We also set `kit.paths.relative: false` in `svelte.config.js` to ensure absolute asset paths.

3. Save

No environment variables needed - the frontend calls `api.passmypass.com` directly in production.

## Environment Variables Reference

Only `DATABASE_URL` is required for the backend. All others have defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | - | PostgreSQL connection string (required) |
| MAX_TTL_SECONDS | 3600 | Max secret lifetime |
| RATE_LIMIT_CREATE | 30/minute | Create endpoint limit |
| RATE_LIMIT_CLAIM | 60/minute | Claim endpoint limit |

**Note:** CORS is pre-configured to allow requests from `passmypass.com` and `www.passmypass.com`.

## Domain Setup

Connect custom domains to both services:

| Domain | Service | Render URL |
|--------|---------|------------|
| `passmypass.com` | Frontend | `passmypass-front.onrender.com` |
| `api.passmypass.com` | Backend | `passmypass-api.onrender.com` |

### 1. Backend Subdomain (api.passmypass.com)

**Step 1: Add custom domain in Render**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select **passmypass-api** web service
3. Go to **Settings** → **Custom Domains**
4. Click **Add Custom Domain**
5. Enter: `api.passmypass.com`
6. Render will display a CNAME target (e.g., `passmypass-api.onrender.com`)

**Step 2: Add DNS record in your domain provider (GoDaddy)**
1. Go to GoDaddy → My Products → DNS for `passmypass.com`
2. Add a CNAME record:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | api | passmypass-api.onrender.com | 600 |

**Step 3: Verify in Render**
- Return to Render and wait for verification (usually 1-5 minutes)
- Render will auto-provision SSL certificate

### 2. Frontend Domain (passmypass.com)

**Step 1: Add custom domains in Render**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select **passmypass-front** static site
3. Go to **Settings** → **Custom Domains**
4. Add both: `passmypass.com` and `www.passmypass.com`

**Step 2: Add DNS records in GoDaddy**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 216.24.57.1 | 600 |
| CNAME | www | passmypass-front.onrender.com | 600 |

**Step 3: Verify in Render**
- Wait for DNS propagation and verification
- Render will auto-provision SSL certificates for both domains

### 3. DNS Propagation

- Usually takes 1-5 minutes
- Can take up to 48 hours in some cases
- Use [dnschecker.org](https://dnschecker.org) to verify propagation

### 4. SSL Certificates

Render automatically provisions free SSL certificates once DNS is verified. No action needed.

## Checklist

- [ ] Create PostgreSQL database
- [ ] Deploy backend web service with `DATABASE_URL`
- [ ] Deploy frontend static site
- [ ] Configure SPA rewrite rule (`/*` → `/200.html`)
- [ ] Add CNAME record for `api` → `passmypass-api.onrender.com`
- [ ] Add A record for `@` → `216.24.57.1`
- [ ] Add CNAME record for `www` → `passmypass-front.onrender.com`
- [ ] Verify all domains in Render (SSL auto-provisioned)
- [ ] Test end-to-end at https://passmypass.com

---

**Architecture:**
```
passmypass.com (frontend) → calls → api.passmypass.com (backend)
```
