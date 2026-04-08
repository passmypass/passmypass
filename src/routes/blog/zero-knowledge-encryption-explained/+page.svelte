<script lang="ts">
	import { Footer } from '$lib';
	import { ArrowLeft, Shield, Lock, Key, Hash, Globe, AlertTriangle } from '@lucide/svelte';
</script>

<svelte:head>
	<title>Zero-Knowledge Encryption Explained: How PassMyPass Protects Your Data</title>
	<meta
		name="description"
		content="Learn how zero-knowledge encryption works and why it's superior to traditional server-side encryption. A technical deep dive into AES-256-GCM, URL fragments, and the cryptographic architecture behind PassMyPass."
	/>
	<link
		rel="canonical"
		href="https://passmypass.com/blog/zero-knowledge-encryption-explained/"
	/>

	<meta property="og:type" content="article" />
	<meta
		property="og:url"
		content="https://passmypass.com/blog/zero-knowledge-encryption-explained/"
	/>
	<meta
		property="og:title"
		content="Zero-Knowledge Encryption Explained: How PassMyPass Protects Your Data"
	/>
	<meta
		property="og:description"
		content="Learn how zero-knowledge encryption works and why it's superior to traditional server-side encryption."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />

	<meta name="twitter:card" content="summary_large_image" />
	<meta
		name="twitter:title"
		content="Zero-Knowledge Encryption Explained: How PassMyPass Protects Your Data"
	/>
	<meta
		name="twitter:description"
		content="Learn how zero-knowledge encryption works and why it's superior to traditional server-side encryption."
	/>
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />

	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'Article',
		headline: 'Zero-Knowledge Encryption Explained: How PassMyPass Protects Your Data',
		description:
			"Learn how zero-knowledge encryption works and why it's superior to traditional server-side encryption. A technical deep dive into AES-256-GCM, URL fragments, and the cryptographic architecture behind PassMyPass.",
		image: 'https://passmypass.com/og-image.png',
		author: {
			'@type': 'Organization',
			name: 'PassMyPass',
			url: 'https://passmypass.com'
		},
		publisher: {
			'@type': 'Organization',
			name: 'PassMyPass',
			url: 'https://passmypass.com'
		},
		datePublished: '2026-04-08',
		dateModified: '2026-04-08',
		mainEntityOfPage: {
			'@type': 'WebPage',
			'@id': 'https://passmypass.com/blog/zero-knowledge-encryption-explained/'
		}
	})}</script>`}
</svelte:head>

<main class="flex-1">
	<!-- Hero -->
	<section class="relative overflow-hidden">
		<div
			class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-950/20 via-transparent to-transparent"
		></div>
		<div class="container mx-auto max-w-3xl px-4 py-12 sm:py-20">
			<a
				href="/blog/"
				class="mb-6 inline-flex items-center gap-1.5 text-sm text-neutral-500 transition hover:text-red-400"
			>
				<ArrowLeft class="h-4 w-4" />
				Back to Blog
			</a>
			<div class="mb-3 flex items-center gap-3 text-xs text-neutral-500">
				<span class="rounded-full bg-red-500/10 px-2.5 py-0.5 font-medium text-red-400">
					Security
				</span>
				<span>April 8, 2026</span>
				<span>7 min read</span>
			</div>
			<h1 class="mb-4 text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">
				Zero-Knowledge Encryption Explained: How PassMyPass Protects Your Data
			</h1>
			<p class="max-w-xl text-base leading-relaxed text-neutral-400 sm:text-lg">
				A technical but accessible explanation of how zero-knowledge architecture works, why it
				matters more than ever, and how PassMyPass implements it from the ground up.
			</p>
		</div>
	</section>

	<!-- Article Content -->
	<article class="container mx-auto max-w-3xl px-4 pb-16">
		<div class="space-y-12">
			<!-- Introduction -->
			<div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						When a service claims to use "zero-knowledge encryption," it means something very
						specific: the service provider is <strong class="text-white"
							>cryptographically unable</strong
						>
						to access your data. Not "we promise not to look" — they literally cannot, even if they
						wanted to, even under a court order, even if their entire infrastructure is compromised.
					</p>
					<p>
						This distinction matters more than most people realize. In a world of data breaches,
						government surveillance programs, and insider threats, the question isn't whether you
						trust a company's intentions. The question is whether the system's architecture
						<em>eliminates the need for trust entirely</em>.
					</p>
					<p>
						In this article, we'll break down exactly how zero-knowledge encryption works, why it's
						fundamentally different from traditional encryption, and how
						<a href="/" class="text-red-400 hover:text-red-300">PassMyPass</a> implements it to protect
						every secret you share.
					</p>
				</div>
			</div>

			<!-- Section 1: Traditional vs Zero-Knowledge -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Shield class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">
						Traditional Encryption vs Zero-Knowledge
					</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						Most services you use every day encrypt your data — but they also hold the keys. Your
						email provider encrypts messages at rest, your cloud storage encrypts files on their
						servers, and your password manager encrypts your vault. This is good practice, but
						there's a critical limitation: <strong class="text-white">the provider can decrypt your
						data whenever they choose</strong>.
					</p>
					<p>
						This is called <strong class="text-white">server-side encryption</strong>. The server
						generates the key, the server encrypts, and the server decrypts. If that server is
						breached, the attacker gets both the ciphertext and the key. If the company receives a
						subpoena, they can comply. If a rogue employee gains access, your data is exposed.
					</p>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">The Key Difference</h3>
						<div class="space-y-3 text-sm text-neutral-400">
							<div class="flex items-start gap-3">
								<span
									class="mt-1 inline-block h-2 w-2 shrink-0 rounded-full bg-amber-500"
								></span>
								<span
									><strong class="text-neutral-300">Server-side encryption:</strong> The
									service encrypts your data and holds the key. They
									<em>can</em> decrypt it. Security depends on trust and their operational security.</span
								>
							</div>
							<div class="flex items-start gap-3">
								<span
									class="mt-1 inline-block h-2 w-2 shrink-0 rounded-full bg-emerald-500"
								></span>
								<span
									><strong class="text-neutral-300">Zero-knowledge encryption:</strong> Your
									device encrypts the data before it leaves your browser. The server never
									sees the key. Security is guaranteed by math, not trust.</span
								>
							</div>
						</div>
					</div>

					<p>
						With zero-knowledge architecture, the encryption key is generated on
						<em>your</em> device and never leaves it. The server only ever receives ciphertext — encrypted
						data that is computationally indistinguishable from random noise without the key.
					</p>
				</div>
			</div>

			<!-- Section 2: How Zero-Knowledge Works in PassMyPass -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Lock class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">
						How Zero-Knowledge Works in PassMyPass
					</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						When you create a secret on <a href="/" class="text-red-400 hover:text-red-300"
							>PassMyPass</a
						>, the following happens entirely within your browser — before any data touches the
						network:
					</p>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">
							Step-by-Step: Creating a Secret
						</h3>
						<ol class="list-decimal space-y-2 pl-5 text-sm text-neutral-400">
							<li>
								Your browser generates a <strong class="text-white">256-bit random encryption key</strong>
								using the Web Crypto API's cryptographically secure random number generator.
							</li>
							<li>
								A <strong class="text-white">12-byte nonce</strong> (number used once) is generated to
								ensure uniqueness, even if the same plaintext is encrypted twice.
							</li>
							<li>
								A <strong class="text-white">32-byte claim token</strong> is generated. This token proves
								you're the intended recipient. Only its SHA-256 hash is sent to the server.
							</li>
							<li>
								Your secret is encrypted with <strong class="text-white">AES-256-GCM</strong>,
								producing ciphertext plus a 16-byte authentication tag that prevents tampering.
							</li>
							<li>
								The server receives and stores: ciphertext, nonce, additional authenticated data
								(AAD), and the claim hash. <strong class="text-white">It never receives the key or the plaintext.</strong>
							</li>
							<li>
								A share link is generated:
								<code class="rounded bg-neutral-800 px-1.5 py-0.5 text-red-400"
									>passmypass.com/s/&#123;id&#125;#&#123;key&#125;.&#123;token&#125;</code
								>
							</li>
						</ol>
					</div>

					<p>
						The crucial detail is in step 6. The encryption key and claim token are placed after
						the <code class="rounded bg-neutral-800 px-1.5 py-0.5 text-red-400">#</code> symbol in
						the URL. This isn't a cosmetic choice — it's the architectural foundation of the entire
						zero-knowledge design.
					</p>
				</div>
			</div>

			<!-- Section 3: The URL Fragment Trick -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Hash class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">The URL Fragment Trick</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						Every URL has a structure defined by <a
							href="https://www.rfc-editor.org/rfc/rfc3986#section-3.5"
							class="text-red-400 hover:text-red-300"
							target="_blank"
							rel="noopener noreferrer">RFC 3986</a
						>. The part after the
						<code class="rounded bg-neutral-800 px-1.5 py-0.5 text-red-400">#</code> symbol is
						called the <strong class="text-white">fragment identifier</strong>, and it has a unique
						property that makes zero-knowledge secret sharing possible: <strong
							class="text-white"
							>browsers never send the fragment to the server</strong
						>.
					</p>
					<p>
						This isn't a browser quirk or an implementation detail — it's part of the HTTP
						specification. When you visit
						<code class="rounded bg-neutral-800 px-1.5 py-0.5 text-xs text-red-400"
							>passmypass.com/s/abc123#secretkey.claimtoken</code
						>, your browser sends a request for
						<code class="rounded bg-neutral-800 px-1.5 py-0.5 text-xs text-red-400"
							>passmypass.com/s/abc123</code
						>
						only. The fragment stays in your browser's address bar and is accessible to client-side JavaScript,
						but it is <strong class="text-white">never transmitted over the network</strong>.
					</p>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">What This Means in Practice</h3>
						<div class="space-y-2 text-sm text-neutral-400">
							<p>
								The server logs show a request for <code class="text-red-400">/s/abc123</code>
								— nothing more. The encryption key and claim token are invisible to server-side
								logging, network monitoring, reverse proxies, CDNs, and anyone inspecting
								traffic. The key exists only in the browser of the person who has the link.
							</p>
							<p>
								This is why the
								<code class="rounded bg-neutral-800 px-1.5 py-0.5 text-red-400"
									>Referrer-Policy: no-referrer</code
								>
								header matters too. Without it, clicking a link on the page could leak the full URL
								(including the fragment) to a third-party site via the
								<code class="text-red-400">Referer</code> header. PassMyPass blocks this entirely.
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Section 4: AES-256-GCM in the Browser -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Globe class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">
						AES-256-GCM in the Browser
					</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						PassMyPass uses <strong class="text-white">AES-256-GCM</strong> (Advanced Encryption
						Standard with 256-bit keys in Galois/Counter Mode) for all encryption operations. This
						is the same algorithm used by governments and militaries worldwide for protecting
						classified information.
					</p>
					<p>
						The "GCM" part is especially important. Unlike basic encryption modes that only provide
						confidentiality, GCM is an <strong class="text-white"
							>authenticated encryption</strong
						>
						scheme. It produces a 16-byte authentication tag alongside the ciphertext, which guarantees
						two things:
					</p>
					<ul class="list-disc space-y-2 pl-6">
						<li>
							<strong class="text-white">Confidentiality:</strong> No one without the key can read
							the data.
						</li>
						<li>
							<strong class="text-white">Integrity:</strong> Any modification to the ciphertext —
							even a single flipped bit — causes decryption to fail. An attacker cannot tamper with
							your secret without detection.
						</li>
					</ul>
					<p>
						All of this runs through the <strong class="text-white">Web Crypto API</strong>, a
						browser-native interface to hardware-accelerated cryptographic operations. Unlike
						third-party JavaScript crypto libraries, Web Crypto is implemented in the browser's
						native code, which provides constant-time operations resistant to timing side-channel
						attacks. The key material is handled in a protected memory space that JavaScript cannot
						directly inspect.
					</p>
				</div>
			</div>

			<!-- Section 5: Password Protection Layer -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<Key class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">
						The Password Protection Layer
					</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						The URL fragment approach is elegant, but what if the link itself is intercepted? A
						compromised chat history, a shoulder-surfed screen, or a clipboard vulnerability could
						expose the share link. This is why PassMyPass offers an optional
						<strong class="text-white">password protection layer</strong> that adds true two-factor
						security.
					</p>
					<p>When you enable password protection, the encryption process gains an additional step:</p>

					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<h3 class="mb-3 text-sm font-semibold text-white">How Password Protection Works</h3>
						<ol class="list-decimal space-y-2 pl-5 text-sm text-neutral-400">
							<li>
								A <strong class="text-white">16-byte salt</strong> is randomly generated and embedded
								in the additional authenticated data (AAD).
							</li>
							<li>
								Your password is fed through <strong class="text-white">PBKDF2-SHA256</strong>
								with <strong class="text-white">100,000 iterations</strong>, using that salt, to
								derive a 256-bit password key. The high iteration count makes brute-force attacks
								computationally expensive.
							</li>
							<li>
								The final encryption key is computed as
								<code class="rounded bg-neutral-800 px-1.5 py-0.5 text-red-400"
									>random_key XOR password_key</code
								>. This means both the link and the password are needed to reconstruct the
								decryption key.
							</li>
						</ol>
					</div>

					<p>
						The result is a genuine two-factor system: the recipient needs <strong
							class="text-white">something they have</strong
						>
						(the link) and
						<strong class="text-white">something they know</strong> (the password). Intercepting either
						one alone is useless. The password is never stored anywhere — not on the server, not in
						the link, not in a cookie.
					</p>
				</div>
			</div>

			<!-- Section 6: Why This Matters -->
			<div>
				<div class="mb-4 flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
						<AlertTriangle class="h-5 w-5 text-red-500" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Why This Matters</h2>
				</div>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						The practical implications of zero-knowledge architecture become clear when you consider
						real-world threat scenarios:
					</p>
					<ul class="list-disc space-y-3 pl-6">
						<li>
							<strong class="text-white">Data breaches:</strong> If PassMyPass's database is dumped,
							attackers get ciphertext that is worthless without the keys — keys that were never stored
							on the server. Compare this to a breach of a service that holds encryption keys: every
							secret is immediately readable.
						</li>
						<li>
							<strong class="text-white">Government surveillance:</strong> Even under a legal
							order, PassMyPass cannot produce plaintext data. There is no key to hand over. This
							is not a policy — it is a mathematical impossibility.
						</li>
						<li>
							<strong class="text-white">Insider threats:</strong> A malicious employee with full
							database access sees only encrypted blobs. Without the key (which lives in the
							recipient's browser or link), the data is unreadable.
						</li>
						<li>
							<strong class="text-white">Compliance requirements:</strong> For organizations bound
							by GDPR, HIPAA, or SOC 2, zero-knowledge encryption provides the strongest possible
							data protection posture. You can demonstrate that sensitive data is protected by design,
							not just by policy.
						</li>
					</ul>
					<p>
						The one-time retrieval mechanism adds another layer. Even if someone eventually
						reconstructed a key, the secret is already consumed and deleted. There is no archive to
						attack, no history to mine. Each secret exists exactly once, is read exactly once, and
						then ceases to exist.
					</p>
				</div>
			</div>

			<!-- Conclusion / CTA -->
			<div class="space-y-6">
				<div>
					<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">
						Trust Math, Not Promises
					</h2>
					<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
						<p>
							Zero-knowledge encryption shifts the security model from "we promise to protect
							your data" to "we are architecturally unable to access your data." That distinction
							is the difference between security by policy and security by design.
						</p>
						<p>
							PassMyPass implements this principle at every layer: client-side key generation, URL
							fragment isolation, AES-256-GCM authenticated encryption, optional PBKDF2 password
							protection, and one-time atomic retrieval. The result is a system where even a
							complete server compromise reveals nothing.
						</p>
						<p>
							Want the full technical details? Read our complete
							<a href="/security/" class="text-red-400 hover:text-red-300"
								>security architecture documentation</a
							>, which covers everything from security headers and rate limiting to chat room
							encryption and infrastructure hardening.
						</p>
					</div>
				</div>

				<div class="rounded-xl border border-neutral-800 bg-neutral-900/60 p-6 text-center">
					<h3 class="mb-2 text-lg font-bold text-white">
						Ready to Share Secrets Securely?
					</h3>
					<p class="mb-4 text-sm text-neutral-400">
						Experience zero-knowledge encryption firsthand. Create a self-destructing encrypted
						secret in seconds — no account required.
					</p>
					<a
						href="/"
						class="inline-flex items-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-red-500/20 transition-all hover:bg-red-500 hover:shadow-xl hover:shadow-red-500/25 active:scale-[0.98]"
					>
						<Lock class="h-4 w-4" />
						Share a Secret Now
					</a>
				</div>
			</div>
		</div>
	</article>
</main>

<Footer />
