<script lang="ts">
	import { Footer } from '$lib';
	import { Shield, Lock, Key, Hash, ServerOff, Clock, Database, Globe } from '@lucide/svelte';
</script>

<svelte:head>
	<title>Security Architecture - PassMyPass | Zero-Knowledge Encryption Details</title>
	<meta
		name="description"
		content="Detailed security architecture of PassMyPass. Learn how AES-256-GCM encryption, zero-knowledge design, PBKDF2 password protection, and URL fragment keys keep your secrets safe."
	/>
	<link rel="canonical" href="https://passmypass.com/security/" />

	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/security/" />
	<meta property="og:title" content="Security Architecture - PassMyPass" />
	<meta
		property="og:description"
		content="How PassMyPass uses zero-knowledge encryption to keep your secrets safe. Full technical details."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="Security Architecture - PassMyPass" />
	<meta
		name="twitter:description"
		content="How PassMyPass uses zero-knowledge encryption to keep your secrets safe."
	/>
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />
</svelte:head>

<main class="flex-1">
	<!-- Hero -->
	<section class="relative overflow-hidden">
		<div
			class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-950/20 via-transparent to-transparent"
		></div>
		<div class="container mx-auto max-w-3xl px-4 py-12 sm:py-20">
			<div class="text-center">
				<div
					class="mb-4 inline-flex items-center gap-2 rounded-full border border-neutral-800 bg-neutral-900/80 px-4 py-1.5 text-xs font-medium text-neutral-300"
				>
					<Shield class="h-3.5 w-3.5 text-red-500" />
					Security Documentation
				</div>
				<h1 class="mb-4 text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">
					Security Architecture
				</h1>
				<p class="mx-auto max-w-xl text-base leading-relaxed text-neutral-400 sm:text-lg">
					A complete technical overview of how PassMyPass protects your secrets using
					zero-knowledge end-to-end encryption.
				</p>
			</div>
		</div>
	</section>

	<!-- Content -->
	<section class="container mx-auto max-w-3xl px-4 pb-16">
		<div class="space-y-12">
			<!-- Zero-Knowledge Overview -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<ServerOff class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Zero-Knowledge Design</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						PassMyPass is designed so that the server <strong class="text-white">never has access</strong>
						to your plaintext data or the encryption keys. This is not a policy — it is a cryptographic
						guarantee built into the architecture.
					</p>
					<p>The core mechanism relies on the <strong class="text-white">URL fragment</strong> (the part
						after the <code class="rounded bg-neutral-800 px-1.5 py-0.5 text-red-400">#</code> symbol).
						Per the HTTP specification (<a
							href="https://www.rfc-editor.org/rfc/rfc3986#section-3.5"
							class="text-red-400 hover:text-red-300"
							target="_blank"
							rel="noopener noreferrer">RFC 3986 §3.5</a>),
						the fragment identifier is <em>never</em> transmitted to the server in HTTP requests.
						The encryption key and claim token live exclusively in this fragment.
					</p>
				</div>
			</div>

			<!-- Encryption Details -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Lock class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Encryption Implementation</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>All encryption uses the <strong class="text-white">Web Crypto API</strong>, which provides
						hardware-accelerated, constant-time cryptographic operations in the browser.</p>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">Secret Encryption Flow</h3>
						<ol class="list-decimal space-y-2 pl-5 text-sm text-neutral-400">
							<li>A <strong class="text-white">256-bit random key</strong> is generated using
								<code class="text-red-400">crypto.getRandomValues()</code></li>
							<li>A <strong class="text-white">12-byte nonce</strong> is generated (unique per encryption)</li>
							<li>A <strong class="text-white">32-byte claim token</strong> is generated and SHA-256 hashed</li>
							<li>The secret is encrypted using <strong class="text-white">AES-256-GCM</strong> with authenticated
								additional data (AAD)</li>
							<li>The server receives: ciphertext, nonce, AAD, and claim_hash</li>
							<li>The share link contains: <code class="text-red-400">/s/&#123;id&#125;#&#123;key&#125;.&#123;token&#125;</code></li>
						</ol>
					</div>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">What the Server Stores</h3>
						<div class="grid gap-2 text-sm">
							<div class="flex items-start gap-2">
								<Database class="mt-0.5 h-4 w-4 shrink-0 text-neutral-600" />
								<span><strong class="text-neutral-300">Ciphertext</strong> — encrypted data (unreadable without the key)</span>
							</div>
							<div class="flex items-start gap-2">
								<Database class="mt-0.5 h-4 w-4 shrink-0 text-neutral-600" />
								<span><strong class="text-neutral-300">Nonce</strong> — 12-byte initialization vector (not secret)</span>
							</div>
							<div class="flex items-start gap-2">
								<Database class="mt-0.5 h-4 w-4 shrink-0 text-neutral-600" />
								<span><strong class="text-neutral-300">AAD</strong> — version byte + flags + optional PBKDF2 salt</span>
							</div>
							<div class="flex items-start gap-2">
								<Database class="mt-0.5 h-4 w-4 shrink-0 text-neutral-600" />
								<span><strong class="text-neutral-300">Claim hash</strong> — SHA-256 of the claim token (not the token itself)</span>
							</div>
							<div class="flex items-start gap-2">
								<Database class="mt-0.5 h-4 w-4 shrink-0 text-neutral-600" />
								<span><strong class="text-neutral-300">Timestamps</strong> — creation, expiry, and consumption times</span>
							</div>
						</div>
					</div>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">What the Server Never Sees</h3>
						<div class="grid gap-2 text-sm">
							<div class="flex items-start gap-2">
								<span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"></span>
								<span>The encryption key (stays in URL fragment)</span>
							</div>
							<div class="flex items-start gap-2">
								<span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"></span>
								<span>The plaintext secret</span>
							</div>
							<div class="flex items-start gap-2">
								<span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"></span>
								<span>The claim token (only its SHA-256 hash)</span>
							</div>
							<div class="flex items-start gap-2">
								<span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500"></span>
								<span>Any password used for protection</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Password Protection -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Key class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Password Protection</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>When password protection is enabled, an additional layer of encryption is applied:</p>
					<ol class="list-decimal space-y-2 pl-5">
						<li>A <strong class="text-white">16-byte salt</strong> is generated and stored in the AAD</li>
						<li>The password is fed through <strong class="text-white">PBKDF2-SHA256</strong> with
							<strong class="text-white">100,000 iterations</strong> to derive a 256-bit key</li>
						<li>The final encryption key = <code class="text-red-400">random_key XOR password_key</code></li>
						<li>The random key (from the URL) alone cannot decrypt — the password is also required</li>
					</ol>
					<p>
						This means even if someone intercepts the share link, they still cannot decrypt the
						secret without knowing the password. The password is never stored anywhere — not on
						the server, not in the link.
					</p>
				</div>
			</div>

			<!-- Atomic Claim -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Hash class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">One-Time Retrieval</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						Secret retrieval uses an <strong class="text-white">atomic database operation</strong>
						(<code class="text-red-400">UPDATE ... WHERE consumed_at IS NULL RETURNING</code>) to
						guarantee that even concurrent requests will only succeed once. The claim token is
						verified by comparing its SHA-256 hash against the stored hash.
					</p>
					<p>
						After retrieval, consumed secrets are cleaned up by a background process. There are no
						backups of secret data.
					</p>
				</div>
			</div>

			<!-- Chat Room Security -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Globe class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Chat Room Security</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>Encrypted chat rooms use the same zero-knowledge principle:</p>
					<ul class="list-disc space-y-2 pl-5">
						<li>The encryption key is generated client-side and shared via the URL fragment</li>
						<li>Each message is encrypted with <strong class="text-white">AES-256-GCM</strong> using
							a unique nonce before being sent over WebSocket</li>
						<li>The server only relays ciphertext — it never sees plaintext messages</li>
						<li>Rooms exist <strong class="text-white">only in server memory</strong> (never written
							to disk or database)</li>
						<li>Rooms are destroyed when either participant disconnects or after 10 minutes</li>
						<li>Maximum 2 participants per room</li>
					</ul>
				</div>
			</div>

			<!-- Infrastructure Security -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Shield class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Infrastructure Security</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>Beyond encryption, PassMyPass enforces multiple layers of defense:</p>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">Security Headers</h3>
						<div class="space-y-2 text-sm text-neutral-400">
							<p><strong class="text-neutral-300">HSTS</strong> — Forces HTTPS with preload and includeSubDomains</p>
							<p><strong class="text-neutral-300">CSP</strong> — Strict Content Security Policy (no inline scripts, frame-ancestors 'none')</p>
							<p><strong class="text-neutral-300">Referrer-Policy</strong> — no-referrer (prevents URL leakage)</p>
							<p><strong class="text-neutral-300">X-Frame-Options</strong> — DENY (prevents clickjacking)</p>
							<p><strong class="text-neutral-300">Cache-Control</strong> — no-store on all API routes (prevents caching of sensitive data)</p>
							<p><strong class="text-neutral-300">Permissions-Policy</strong> — Disables geolocation, microphone, camera</p>
						</div>
					</div>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">Rate Limiting</h3>
						<div class="space-y-2 text-sm text-neutral-400">
							<p>Secret creation: 30 requests/minute</p>
							<p>Secret claiming: 60 requests/minute</p>
							<p>Chat room creation: 10 requests/minute</p>
						</div>
					</div>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">Privacy Measures</h3>
						<div class="space-y-2 text-sm text-neutral-400">
							<p>IP addresses are SHA-256 hashed before storage</p>
							<p>No cookies, no tracking, no analytics</p>
							<p>User-Agent strings are hashed for audit</p>
							<p>Only anonymous aggregate statistics are collected</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Report a Vulnerability -->
			<div class="rounded-xl border border-neutral-800 bg-neutral-900/60 p-6 text-center">
				<h2 class="mb-2 text-lg font-bold text-white">Found a Vulnerability?</h2>
				<p class="mb-4 text-sm text-neutral-400">
					We take security seriously. If you've found a security issue, please report it
					responsibly.
				</p>
				<a
					href="/contact/"
					class="inline-flex items-center gap-2 rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500"
				>
					Report a Vulnerability
				</a>
			</div>
		</div>
	</section>
</main>

<Footer />
