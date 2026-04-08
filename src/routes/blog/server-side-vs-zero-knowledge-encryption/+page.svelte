<script lang="ts">
	import { Footer } from '$lib';
	import {
		ArrowLeft,
		ArrowRight,
		Shield,
		ShieldAlert,
		Lock,
		MessageSquareLock
	} from '@lucide/svelte';
</script>

<svelte:head>
	<title>Server-Side vs Zero-Knowledge Encryption: Which Actually Protects Your Secrets?</title>
	<meta
		name="description"
		content="Most secret sharing tools encrypt on the server — meaning they can read your data. Learn why zero-knowledge client-side encryption is the only architecture that truly protects your secrets."
	/>
	<link
		rel="canonical"
		href="https://passmypass.com/blog/server-side-vs-zero-knowledge-encryption/"
	/>

	<meta property="og:type" content="article" />
	<meta
		property="og:url"
		content="https://passmypass.com/blog/server-side-vs-zero-knowledge-encryption/"
	/>
	<meta
		property="og:title"
		content="Server-Side vs Zero-Knowledge Encryption: Which Protects Your Secrets?"
	/>
	<meta
		property="og:description"
		content="Most secret sharing tools encrypt on the server. Learn why zero-knowledge client-side encryption is the only architecture that truly protects your secrets."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />

	<meta name="twitter:card" content="summary_large_image" />
	<meta
		name="twitter:title"
		content="Server-Side vs Zero-Knowledge Encryption: Which Protects Your Secrets?"
	/>
	<meta
		name="twitter:description"
		content="Most secret sharing tools encrypt on the server. Learn why zero-knowledge client-side encryption is the only architecture that truly protects your secrets."
	/>
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />

	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'Article',
		headline:
			'Server-Side vs Zero-Knowledge Encryption: Which Actually Protects Your Secrets?',
		description:
			'Most secret sharing tools encrypt on the server — meaning they can read your data. Learn why zero-knowledge client-side encryption is the only architecture that truly protects your secrets.',
		url: 'https://passmypass.com/blog/server-side-vs-zero-knowledge-encryption/',
		datePublished: '2026-04-08',
		dateModified: '2026-04-08',
		author: { '@type': 'Organization', name: 'PassMyPass', url: 'https://passmypass.com' },
		publisher: { '@type': 'Organization', name: 'PassMyPass', url: 'https://passmypass.com' },
		mainEntityOfPage: {
			'@type': 'WebPage',
			'@id': 'https://passmypass.com/blog/server-side-vs-zero-knowledge-encryption/'
		}
	})}</script>`}
</svelte:head>

<main class="flex-1">
	<div class="container mx-auto max-w-3xl px-4 pt-8 sm:pt-12">
		<a
			href="/blog/"
			class="inline-flex items-center gap-1.5 text-sm text-neutral-500 transition hover:text-red-400"
		>
			<ArrowLeft class="h-4 w-4" />
			Back to Blog
		</a>
	</div>

	<article class="container mx-auto max-w-3xl px-4 py-8 sm:py-12">
		<header class="mb-10">
			<div class="mb-4 flex items-center gap-3 text-xs text-neutral-500">
				<span class="rounded-full bg-red-500/10 px-2.5 py-0.5 font-medium text-red-400">
					Security
				</span>
				<span>April 8, 2026</span>
				<span>5 min read</span>
			</div>
			<h1 class="mb-4 text-3xl font-extrabold tracking-tight sm:text-4xl">
				Server-Side vs Zero-Knowledge Encryption: Which Actually Protects Your Secrets?
			</h1>
			<p class="text-lg leading-relaxed text-neutral-400">
				Most secret sharing tools encrypt your data on their server. That means they hold the keys
				and can technically read everything you share. There is a better way.
			</p>
		</header>

		<div class="prose prose-invert prose-neutral max-w-none space-y-10 text-neutral-300">
			<section>
				<p>
					One-time secret sharing tools have become popular for sending passwords, API keys, and
					credentials securely. But not all of them are created equal. The critical difference lies
					not in whether they encrypt your data — most do — but in <strong class="text-white"
						>where the encryption happens and who holds the keys</strong
					>.
				</p>
				<p>
					Many popular tools use <strong class="text-white">server-side encryption</strong>: your
					secret travels to the server in plaintext over TLS, the server encrypts it, and later
					decrypts it when the recipient requests it. The encryption key lives on the server
					throughout this process.
				</p>
				<p>
					<a
						href="/"
						class="text-red-400 underline decoration-red-400/30 hover:decoration-red-400"
						>PassMyPass</a
					>
					takes a fundamentally different approach called
					<strong class="text-white">zero-knowledge encryption</strong>: all encryption happens in
					your browser before any data leaves your device. The server never sees plaintext and never
					holds an encryption key.
				</p>
			</section>

			<section>
				<h2 class="text-2xl font-bold text-white">How Server-Side Encryption Works</h2>
				<p>
					With server-side encryption, the typical flow is: you paste your secret into a form, it
					is sent to the server over HTTPS, the server encrypts it with a key it generates and
					controls, and stores the ciphertext. When the recipient opens the link, the server
					decrypts the data and sends the plaintext back.
				</p>
				<p>
					This is better than storing secrets in plaintext. But it introduces a trust problem:
					<strong class="text-white">the service provider can read your secrets</strong>.
				</p>

				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-6">
					<div class="mb-3 flex items-center gap-2">
						<ShieldAlert class="h-5 w-5 text-amber-400" />
						<h3 class="text-base font-semibold text-white">
							Three risks of server-side encryption
						</h3>
					</div>
					<ul class="space-y-3 text-sm">
						<li>
							<strong class="text-white">Insider access.</strong> Any employee or contractor with server
							access could view secrets in transit or extract the encryption key. You are trusting the
							organization, not mathematics.
						</li>
						<li>
							<strong class="text-white">Server compromise.</strong> If an attacker breaches the server,
							they gain access to the encryption keys alongside the ciphertext — a single point of
							failure.
						</li>
						<li>
							<strong class="text-white">Legal compulsion.</strong> Government agencies can compel the
							provider to hand over data. Since the server holds the keys, the provider has the
							technical ability to comply.
						</li>
					</ul>
				</div>

				<p>
					The teams behind these tools may be trustworthy. But the point is architectural: with
					server-side encryption, security depends on trust. With zero-knowledge encryption,
					security depends on math.
				</p>
			</section>

			<section>
				<h2 class="text-2xl font-bold text-white">How Zero-Knowledge Encryption Works</h2>
				<p>
					PassMyPass uses a <strong class="text-white">zero-knowledge architecture</strong>. The
					encryption key is generated in your browser, the secret is encrypted using
					<strong class="text-white">AES-256-GCM</strong>, and only the ciphertext is sent to the
					server.
				</p>
				<p>
					The key is placed in the
					<strong class="text-white">URL fragment</strong> (the part after the
					<code class="rounded bg-neutral-800 px-1 text-red-400">#</code> symbol). URL fragments
					are never sent to the server by the browser — this is guaranteed by the HTTP
					specification (RFC 3986). When the recipient opens the link, their browser extracts the
					key from the fragment, requests the ciphertext, and decrypts it locally.
				</p>

				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-6">
					<div class="mb-3 flex items-center gap-2">
						<Shield class="h-5 w-5 text-emerald-400" />
						<h3 class="text-base font-semibold text-white">What the PassMyPass server stores</h3>
					</div>
					<ul class="space-y-2 text-sm">
						<li><strong class="text-white">Ciphertext</strong> that it cannot decrypt</li>
						<li>
							<strong class="text-white">A nonce</strong> used for AES-GCM (useless without the key)
						</li>
						<li>
							<strong class="text-white">A SHA-256 hash</strong> of the claim token (to verify retrieval
							without knowing the token)
						</li>
					</ul>
					<p class="mt-3 text-sm text-neutral-500">
						The server never receives, processes, or stores the encryption key. Even a complete
						database leak would reveal nothing readable.
					</p>
				</div>

				<p>
					PassMyPass also offers optional
					<a
						href="/"
						class="text-red-400 underline decoration-red-400/30 hover:decoration-red-400"
						>password protection</a
					>
					adding a second encryption layer via PBKDF2. And the
					<a
						href="/chat/"
						class="text-red-400 underline decoration-red-400/30 hover:decoration-red-400"
						>encrypted chat</a
					>
					feature provides end-to-end encrypted ephemeral messaging with the same zero-knowledge
					guarantees. See the
					<a
						href="/security/"
						class="text-red-400 underline decoration-red-400/30 hover:decoration-red-400"
						>security architecture</a
					> for the full technical details.
				</p>
			</section>

			<section>
				<h2 class="text-2xl font-bold text-white">Side-by-Side Comparison</h2>
				<div class="overflow-x-auto rounded-xl border border-neutral-800/50">
					<table class="w-full text-sm">
						<thead>
							<tr class="border-b border-neutral-800/50 bg-neutral-900/60">
								<th class="px-4 py-3 text-left font-semibold text-white">Feature</th>
								<th class="px-4 py-3 text-left font-semibold text-emerald-400"
									>Zero-Knowledge (PassMyPass)</th
								>
								<th class="px-4 py-3 text-left font-semibold text-neutral-400"
									>Server-Side (Other Tools)</th
								>
							</tr>
						</thead>
						<tbody class="divide-y divide-neutral-800/30">
							<tr class="bg-neutral-900/20">
								<td class="px-4 py-3 font-medium text-white">Where encryption happens</td>
								<td class="px-4 py-3 text-emerald-400">In your browser</td>
								<td class="px-4 py-3 text-neutral-400">On the server</td>
							</tr>
							<tr>
								<td class="px-4 py-3 font-medium text-white">Who holds the key</td>
								<td class="px-4 py-3 text-emerald-400">Only you (via the link)</td>
								<td class="px-4 py-3 text-neutral-400">The server</td>
							</tr>
							<tr class="bg-neutral-900/20">
								<td class="px-4 py-3 font-medium text-white">Can the provider read secrets?</td>
								<td class="px-4 py-3 text-emerald-400">No, mathematically impossible</td>
								<td class="px-4 py-3 text-neutral-400">Yes, technically possible</td>
							</tr>
							<tr>
								<td class="px-4 py-3 font-medium text-white">Database breach exposure</td>
								<td class="px-4 py-3 text-emerald-400">Ciphertext only (unreadable)</td>
								<td class="px-4 py-3 text-neutral-400">Keys + ciphertext (readable)</td>
							</tr>
							<tr class="bg-neutral-900/20">
								<td class="px-4 py-3 font-medium text-white">Legal compulsion risk</td>
								<td class="px-4 py-3 text-emerald-400">Cannot comply (no access)</td>
								<td class="px-4 py-3 text-neutral-400">Can be compelled to decrypt</td>
							</tr>
							<tr>
								<td class="px-4 py-3 font-medium text-white">Encrypted chat</td>
								<td class="px-4 py-3 text-emerald-400">Yes (E2E encrypted)</td>
								<td class="px-4 py-3 text-neutral-400">Rarely offered</td>
							</tr>
						</tbody>
					</table>
				</div>
			</section>

			<section>
				<h2 class="text-2xl font-bold text-white">The Bottom Line</h2>
				<p>
					Server-side encryption tools deserve credit for making secret sharing safer than email.
					But their architecture means you are placing trust in an organization rather than in
					cryptography.
				</p>
				<p>
					If you want a tool that eliminates the need for trust entirely, look for
					<strong class="text-white">zero-knowledge architecture</strong> — where encryption
					happens in your browser, the key never touches the server, and even a complete database
					breach reveals nothing. That is the difference between "we promise not to look" and "we
					mathematically cannot look."
				</p>
			</section>

			<!-- CTA -->
			<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-8 text-center">
				<div class="mb-3 flex justify-center">
					<Lock class="h-8 w-8 text-red-500" />
				</div>
				<h3 class="mb-2 text-xl font-bold text-white">
					Ready to share secrets the secure way?
				</h3>
				<p class="mb-6 text-sm text-neutral-400">
					No sign-up required. Your secret is encrypted in your browser before it ever reaches our
					server.
				</p>
				<div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
					<a
						href="/"
						class="inline-flex items-center gap-2 rounded-lg bg-red-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500"
					>
						Share a Secret
						<ArrowRight class="h-4 w-4" />
					</a>
					<a
						href="/chat/"
						class="inline-flex items-center gap-2 rounded-lg border border-neutral-700 px-6 py-2.5 text-sm font-semibold text-neutral-300 transition hover:border-neutral-600 hover:text-white"
					>
						<MessageSquareLock class="h-4 w-4" />
						Start Encrypted Chat
					</a>
				</div>
			</div>
		</div>
	</article>
</main>

<Footer />
