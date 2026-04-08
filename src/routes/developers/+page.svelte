<script lang="ts">
	import { Footer } from '$lib';
	import { Code, Terminal, Copy, Check, Shield, Zap, ExternalLink } from '@lucide/svelte';

	let copiedSnippet = $state('');

	async function copyCode(id: string, text: string) {
		try {
			await navigator.clipboard.writeText(text);
		} catch {
			const ta = document.createElement('textarea');
			ta.value = text;
			document.body.appendChild(ta);
			ta.select();
			document.execCommand('copy');
			document.body.removeChild(ta);
		}
		copiedSnippet = id;
		setTimeout(() => (copiedSnippet = ''), 2000);
	}

	const curlCreate = `curl -X POST https://api.passmypass.com/api/secrets \\
  -H "Content-Type: application/json" \\
  -d '{
    "ciphertext_b64u": "<base64url-encoded-ciphertext>",
    "nonce_b64u": "<base64url-encoded-nonce>",
    "aad_b64u": "<base64url-encoded-aad>",
    "claim_hash_b64u": "<base64url-encoded-sha256-hash>",
    "expires_in_seconds": 3600
  }'`;

	const curlStatus = `curl https://api.passmypass.com/api/secrets/{id}/status`;

	const curlClaim = `curl -X POST https://api.passmypass.com/api/secrets/{id}/claim \\
  -H "Content-Type: application/json" \\
  -d '{"claim_token_b64u": "<base64url-encoded-claim-token>"}'`;

	const jsExample = `// Full client-side encryption + API call example
// Note: You MUST perform encryption client-side.
// The server only accepts pre-encrypted ciphertext.

async function shareSecret(plaintext, expiresInSeconds = 3600) {
  // 1. Generate cryptographic materials
  const key = crypto.getRandomValues(new Uint8Array(32));
  const nonce = crypto.getRandomValues(new Uint8Array(12));
  const claimToken = crypto.getRandomValues(new Uint8Array(32));
  const aad = new Uint8Array([0x01, 0x00]); // v1, no password

  // 2. Import key and encrypt
  const cryptoKey = await crypto.subtle.importKey(
    'raw', key, { name: 'AES-GCM' }, false, ['encrypt']
  );
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: nonce, additionalData: aad },
      cryptoKey,
      new TextEncoder().encode(plaintext)
    )
  );

  // 3. Hash the claim token
  const claimHash = new Uint8Array(
    await crypto.subtle.digest('SHA-256', claimToken)
  );

  // 4. Base64url encode helper
  const b64u = (bytes) =>
    btoa(String.fromCharCode(...bytes))
      .replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');

  // 5. Send to API
  const res = await fetch('https://api.passmypass.com/api/secrets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ciphertext_b64u: b64u(ciphertext),
      nonce_b64u: b64u(nonce),
      aad_b64u: b64u(aad),
      claim_hash_b64u: b64u(claimHash),
      expires_in_seconds: expiresInSeconds,
    }),
  });
  const { id } = await res.json();

  // 6. Build share link (key + token in fragment — never sent to server)
  return \`https://passmypass.com/s/\${id}#\${b64u(key)}.\${b64u(claimToken)}\`;
}

// Usage
const link = await shareSecret('my-database-password', 86400);
console.log(link); // https://passmypass.com/s/abc123#key.token`;

	const pyExample = `import hashlib, secrets, base64, json
from urllib.request import Request, urlopen

# NOTE: This is a simplified example.
# In production, use the WebCrypto API in the browser for true E2E encryption.
# Server-side encryption means the server momentarily sees the plaintext.

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def share_secret(plaintext: str, expires_in: int = 3600) -> str:
    key = secrets.token_bytes(32)
    nonce = secrets.token_bytes(12)
    claim_token = secrets.token_bytes(32)
    aad = bytes([0x01, 0x00])  # v1, no password

    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode(), aad)
    claim_hash = hashlib.sha256(claim_token).digest()

    body = json.dumps({
        "ciphertext_b64u": b64u(ciphertext),
        "nonce_b64u": b64u(nonce),
        "aad_b64u": b64u(aad),
        "claim_hash_b64u": b64u(claim_hash),
        "expires_in_seconds": expires_in,
    }).encode()

    req = Request(
        "https://api.passmypass.com/api/secrets",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = json.loads(urlopen(req).read())

    return f"https://passmypass.com/s/{resp['id']}#{b64u(key)}.{b64u(claim_token)}"

link = share_secret("my-api-key-here", 86400)
print(link)`;
</script>

<svelte:head>
	<title>Developer API Documentation - PassMyPass</title>
	<meta
		name="description"
		content="PassMyPass REST API documentation. Integrate zero-knowledge secret sharing into your apps, scripts, and CI/CD pipelines. Free, no API key required."
	/>
	<link rel="canonical" href="https://passmypass.com/developers/" />

	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/developers/" />
	<meta property="og:title" content="Developer API Documentation - PassMyPass" />
	<meta
		property="og:description"
		content="Integrate zero-knowledge secret sharing into your apps. Free REST API, no API key required."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="Developer API Documentation - PassMyPass" />
	<meta
		name="twitter:description"
		content="Integrate zero-knowledge secret sharing into your apps. Free REST API."
	/>
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />
</svelte:head>

<main class="flex-1">
	<!-- Hero -->
	<section class="relative overflow-hidden">
		<div
			class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-950/20 via-transparent to-transparent"
		></div>
		<div class="container mx-auto max-w-4xl px-4 py-12 sm:py-20">
			<div class="text-center">
				<div
					class="mb-4 inline-flex items-center gap-2 rounded-full border border-neutral-800 bg-neutral-900/80 px-4 py-1.5 text-xs font-medium text-neutral-300"
				>
					<Code class="h-3.5 w-3.5 text-red-500" />
					REST API
				</div>
				<h1 class="mb-4 text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">
					Developer API
				</h1>
				<p class="mx-auto max-w-xl text-base leading-relaxed text-neutral-400 sm:text-lg">
					Integrate zero-knowledge secret sharing into your applications, scripts, and CI/CD
					pipelines. Free, no API key required.
				</p>
				<div class="mt-6 flex flex-wrap justify-center gap-3">
					<a
						href="https://api.passmypass.com/api/docs"
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-red-500/20 transition hover:bg-red-500"
					>
						Interactive API Docs
						<ExternalLink class="h-4 w-4" />
					</a>
					<a
						href="https://api.passmypass.com/api/openapi.json"
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex items-center gap-2 rounded-lg border border-neutral-700 bg-neutral-800/30 px-4 py-2.5 text-sm font-medium text-neutral-300 transition hover:bg-neutral-800 hover:text-white"
					>
						OpenAPI Spec
						<ExternalLink class="h-4 w-4" />
					</a>
				</div>
			</div>
		</div>
	</section>

	<section class="container mx-auto max-w-4xl px-4 pb-16">
		<div class="space-y-12">
			<!-- Quick Start -->
			<div>
				<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">Quick Start</h2>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<div class="grid gap-4 sm:grid-cols-3">
						<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
							<Shield class="mb-3 h-5 w-5 text-red-500" />
							<h3 class="mb-1 text-sm font-semibold text-white">No API Key</h3>
							<p class="text-xs text-neutral-500">
								No authentication required. Rate limits apply per IP address.
							</p>
						</div>
						<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
							<Zap class="mb-3 h-5 w-5 text-red-500" />
							<h3 class="mb-1 text-sm font-semibold text-white">Client-Side Encryption</h3>
							<p class="text-xs text-neutral-500">
								You must encrypt data before sending. The API only accepts ciphertext.
							</p>
						</div>
						<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
							<Terminal class="mb-3 h-5 w-5 text-red-500" />
							<h3 class="mb-1 text-sm font-semibold text-white">REST + WebSocket</h3>
							<p class="text-xs text-neutral-500">
								Secrets via REST. Chat rooms via WebSocket with the same encryption model.
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Base URL -->
			<div>
				<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">Base URL</h2>
				<div
					class="flex items-center justify-between rounded-xl border border-neutral-700 bg-neutral-950 p-4 font-mono text-sm text-red-400"
				>
					<span>https://api.passmypass.com</span>
				</div>
			</div>

			<!-- Rate Limits -->
			<div>
				<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">Rate Limits</h2>
				<div class="overflow-hidden rounded-xl border border-neutral-800/50">
					<table class="w-full text-sm">
						<thead>
							<tr class="border-b border-neutral-800/50 bg-neutral-900/40">
								<th class="px-4 py-3 text-left font-medium text-neutral-300">Endpoint</th>
								<th class="px-4 py-3 text-left font-medium text-neutral-300">Limit</th>
							</tr>
						</thead>
						<tbody class="text-neutral-400">
							<tr class="border-b border-neutral-800/30">
								<td class="px-4 py-3 font-mono text-xs">POST /api/secrets</td>
								<td class="px-4 py-3">30 requests/minute</td>
							</tr>
							<tr class="border-b border-neutral-800/30">
								<td class="px-4 py-3 font-mono text-xs">POST /api/secrets/{'{id}'}/claim</td>
								<td class="px-4 py-3">60 requests/minute</td>
							</tr>
							<tr>
								<td class="px-4 py-3 font-mono text-xs">POST /api/chat/rooms</td>
								<td class="px-4 py-3">10 requests/minute</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Endpoints -->
			<div>
				<h2 class="mb-6 text-xl font-bold text-white sm:text-2xl">API Endpoints</h2>

				<!-- Create Secret -->
				<div class="mb-8 rounded-xl border border-neutral-800/50 bg-neutral-900/30 p-5 sm:p-6">
					<div class="mb-4 flex items-center gap-3">
						<span
							class="rounded-md bg-emerald-500/10 px-2 py-1 font-mono text-xs font-bold text-emerald-400"
							>POST</span
						>
						<code class="text-sm text-neutral-300">/api/secrets</code>
					</div>
					<p class="mb-4 text-sm text-neutral-400">
						Create a new one-time secret. The request body must contain pre-encrypted ciphertext
						and cryptographic parameters.
					</p>

					<h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
						Request Body
					</h4>
					<div class="mb-4 overflow-hidden rounded-lg border border-neutral-800/50">
						<table class="w-full text-xs">
							<thead>
								<tr class="border-b border-neutral-800/50 bg-neutral-950/50">
									<th class="px-3 py-2 text-left font-medium text-neutral-400">Field</th>
									<th class="px-3 py-2 text-left font-medium text-neutral-400">Type</th>
									<th class="px-3 py-2 text-left font-medium text-neutral-400">Description</th>
								</tr>
							</thead>
							<tbody class="text-neutral-500">
								<tr class="border-b border-neutral-800/30">
									<td class="px-3 py-2 font-mono text-red-400">ciphertext_b64u</td>
									<td class="px-3 py-2">string</td>
									<td class="px-3 py-2">Base64url-encoded AES-256-GCM ciphertext</td>
								</tr>
								<tr class="border-b border-neutral-800/30">
									<td class="px-3 py-2 font-mono text-red-400">nonce_b64u</td>
									<td class="px-3 py-2">string</td>
									<td class="px-3 py-2">Base64url-encoded 12-byte nonce</td>
								</tr>
								<tr class="border-b border-neutral-800/30">
									<td class="px-3 py-2 font-mono text-red-400">aad_b64u</td>
									<td class="px-3 py-2">string?</td>
									<td class="px-3 py-2">Base64url-encoded additional authenticated data</td>
								</tr>
								<tr class="border-b border-neutral-800/30">
									<td class="px-3 py-2 font-mono text-red-400">claim_hash_b64u</td>
									<td class="px-3 py-2">string</td>
									<td class="px-3 py-2">SHA-256 hash of the claim token (base64url)</td>
								</tr>
								<tr>
									<td class="px-3 py-2 font-mono text-red-400">expires_in_seconds</td>
									<td class="px-3 py-2">int</td>
									<td class="px-3 py-2">60 to 86400 (1 min to 24 hours)</td>
								</tr>
							</tbody>
						</table>
					</div>

					<h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
						Response (201)
					</h4>
					<div class="relative rounded-lg border border-neutral-800/50 bg-neutral-950 p-4">
						<pre class="overflow-x-auto font-mono text-xs text-neutral-300"><code>{`{
  "id": "aB3xK9mZ...",
  "expires_at": "2026-04-09T06:00:00Z"
}`}</code></pre>
					</div>
				</div>

				<!-- Check Status -->
				<div class="mb-8 rounded-xl border border-neutral-800/50 bg-neutral-900/30 p-5 sm:p-6">
					<div class="mb-4 flex items-center gap-3">
						<span
							class="rounded-md bg-blue-500/10 px-2 py-1 font-mono text-xs font-bold text-blue-400"
							>GET</span
						>
						<code class="text-sm text-neutral-300">/api/secrets/{'{id}'}/status</code>
					</div>
					<p class="mb-4 text-sm text-neutral-400">
						Check if a secret exists and is available without consuming it. Useful for showing
						status to senders.
					</p>
					<h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
						Response (200)
					</h4>
					<div class="rounded-lg border border-neutral-800/50 bg-neutral-950 p-4">
						<pre class="overflow-x-auto font-mono text-xs text-neutral-300"><code>{`{
  "exists": true,
  "consumed": false,
  "expired": false,
  "expires_at": "2026-04-09T06:00:00Z"
}`}</code></pre>
					</div>
				</div>

				<!-- Claim Secret -->
				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/30 p-5 sm:p-6">
					<div class="mb-4 flex items-center gap-3">
						<span
							class="rounded-md bg-emerald-500/10 px-2 py-1 font-mono text-xs font-bold text-emerald-400"
							>POST</span
						>
						<code class="text-sm text-neutral-300">/api/secrets/{'{id}'}/claim</code>
					</div>
					<p class="mb-4 text-sm text-neutral-400">
						Atomically claim and retrieve a one-time secret. The secret is permanently deleted
						after this call.
					</p>

					<h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
						Request Body
					</h4>
					<div class="mb-4 overflow-hidden rounded-lg border border-neutral-800/50">
						<table class="w-full text-xs">
							<thead>
								<tr class="border-b border-neutral-800/50 bg-neutral-950/50">
									<th class="px-3 py-2 text-left font-medium text-neutral-400">Field</th>
									<th class="px-3 py-2 text-left font-medium text-neutral-400">Type</th>
									<th class="px-3 py-2 text-left font-medium text-neutral-400">Description</th>
								</tr>
							</thead>
							<tbody class="text-neutral-500">
								<tr>
									<td class="px-3 py-2 font-mono text-red-400">claim_token_b64u</td>
									<td class="px-3 py-2">string</td>
									<td class="px-3 py-2">The original claim token (base64url), not the hash</td>
								</tr>
							</tbody>
						</table>
					</div>

					<h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
						Response (200)
					</h4>
					<div class="rounded-lg border border-neutral-800/50 bg-neutral-950 p-4">
						<pre class="overflow-x-auto font-mono text-xs text-neutral-300"><code>{`{
  "ciphertext_b64u": "...",
  "nonce_b64u": "...",
  "aad_b64u": "..." // or null
}`}</code></pre>
					</div>
				</div>
			</div>

			<!-- Code Examples -->
			<div>
				<h2 class="mb-6 text-xl font-bold text-white sm:text-2xl">Code Examples</h2>

				<!-- cURL -->
				<div class="mb-6">
					<div class="mb-2 flex items-center justify-between">
						<h3 class="flex items-center gap-2 text-sm font-semibold text-neutral-300">
							<Terminal class="h-4 w-4 text-neutral-500" />
							cURL — Create Secret
						</h3>
						<button
							onclick={() => copyCode('curl-create', curlCreate)}
							class="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-neutral-500 transition hover:bg-neutral-800 hover:text-white"
						>
							{#if copiedSnippet === 'curl-create'}
								<Check class="h-3 w-3" /> Copied
							{:else}
								<Copy class="h-3 w-3" /> Copy
							{/if}
						</button>
					</div>
					<div class="rounded-lg border border-neutral-800/50 bg-neutral-950 p-4">
						<pre
							class="overflow-x-auto font-mono text-xs leading-relaxed text-neutral-300"
						><code>{curlCreate}</code></pre>
					</div>
				</div>

				<div class="mb-6">
					<div class="mb-2 flex items-center justify-between">
						<h3 class="flex items-center gap-2 text-sm font-semibold text-neutral-300">
							<Terminal class="h-4 w-4 text-neutral-500" />
							cURL — Check Status
						</h3>
						<button
							onclick={() => copyCode('curl-status', curlStatus)}
							class="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-neutral-500 transition hover:bg-neutral-800 hover:text-white"
						>
							{#if copiedSnippet === 'curl-status'}
								<Check class="h-3 w-3" /> Copied
							{:else}
								<Copy class="h-3 w-3" /> Copy
							{/if}
						</button>
					</div>
					<div class="rounded-lg border border-neutral-800/50 bg-neutral-950 p-4">
						<pre
							class="overflow-x-auto font-mono text-xs leading-relaxed text-neutral-300"
						><code>{curlStatus}</code></pre>
					</div>
				</div>

				<!-- JavaScript -->
				<div class="mb-6">
					<div class="mb-2 flex items-center justify-between">
						<h3 class="flex items-center gap-2 text-sm font-semibold text-neutral-300">
							<Code class="h-4 w-4 text-neutral-500" />
							JavaScript — Full E2E Example
						</h3>
						<button
							onclick={() => copyCode('js', jsExample)}
							class="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-neutral-500 transition hover:bg-neutral-800 hover:text-white"
						>
							{#if copiedSnippet === 'js'}
								<Check class="h-3 w-3" /> Copied
							{:else}
								<Copy class="h-3 w-3" /> Copy
							{/if}
						</button>
					</div>
					<div class="rounded-lg border border-neutral-800/50 bg-neutral-950 p-4">
						<pre
							class="overflow-x-auto font-mono text-xs leading-relaxed text-neutral-300"
						><code>{jsExample}</code></pre>
					</div>
				</div>

				<!-- Python -->
				<div>
					<div class="mb-2 flex items-center justify-between">
						<h3 class="flex items-center gap-2 text-sm font-semibold text-neutral-300">
							<Code class="h-4 w-4 text-neutral-500" />
							Python — E2E Example
						</h3>
						<button
							onclick={() => copyCode('py', pyExample)}
							class="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-neutral-500 transition hover:bg-neutral-800 hover:text-white"
						>
							{#if copiedSnippet === 'py'}
								<Check class="h-3 w-3" /> Copied
							{:else}
								<Copy class="h-3 w-3" /> Copy
							{/if}
						</button>
					</div>
					<div class="rounded-lg border border-neutral-800/50 bg-neutral-950 p-4">
						<pre
							class="overflow-x-auto font-mono text-xs leading-relaxed text-neutral-300"
						><code>{pyExample}</code></pre>
					</div>
				</div>
			</div>

			<!-- Important Notes -->
			<div>
				<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">Important Notes</h2>
				<div class="space-y-3 text-sm text-neutral-400">
					<div class="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
						<p class="font-medium text-amber-300">Encryption must happen client-side</p>
						<p class="mt-1 text-amber-400/80">
							The API only accepts pre-encrypted ciphertext. If you encrypt server-side, you lose
							the zero-knowledge guarantee — your server will see the plaintext. For true E2E
							encryption, perform all crypto in the browser using the WebCrypto API.
						</p>
					</div>
					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-4">
						<p class="font-medium text-neutral-200">
							The URL fragment (#) is never sent to the server
						</p>
						<p class="mt-1 text-neutral-500">
							The encryption key and claim token live in the URL fragment. Per RFC 3986, browsers
							never transmit the fragment to the server. This is the foundation of the
							zero-knowledge design.
						</p>
					</div>
				</div>
			</div>
		</div>
	</section>
</main>

<Footer />
