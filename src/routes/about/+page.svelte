<script lang="ts">
	import { Footer } from '$lib';
	import { Shield, Lock, Eye, ServerOff, Heart } from '@lucide/svelte';
</script>

<svelte:head>
	<title>About PassMyPass - Zero-Knowledge Secret Sharing</title>
	<meta
		name="description"
		content="Learn about PassMyPass, the zero-knowledge encrypted secret sharing tool. Built for developers and IT teams who refuse to compromise on security."
	/>
	<link rel="canonical" href="https://passmypass.com/about/" />

	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/about/" />
	<meta property="og:title" content="About PassMyPass - Zero-Knowledge Secret Sharing" />
	<meta
		property="og:description"
		content="Learn about PassMyPass, the zero-knowledge encrypted secret sharing tool."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="About PassMyPass - Zero-Knowledge Secret Sharing" />
	<meta
		name="twitter:description"
		content="Learn about PassMyPass, the zero-knowledge encrypted secret sharing tool."
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
				<h1 class="mb-4 text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">
					About PassMyPass
				</h1>
				<p class="mx-auto max-w-xl text-base leading-relaxed text-neutral-400 sm:text-lg">
					We believe sharing sensitive data shouldn't require trusting a third party. So we built
					a tool where trust isn't needed.
				</p>
			</div>
		</div>
	</section>

	<!-- Mission -->
	<section class="container mx-auto max-w-3xl px-4 pb-16">
		<div class="space-y-12">
			<!-- The Problem -->
			<div>
				<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">The Problem</h2>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						Every day, millions of passwords, API keys, and credentials are shared through email,
						Slack, and text messages. These channels store data on multiple servers, often
						unencrypted, and persist it indefinitely. A single breach exposes everything.
					</p>
					<p>
						Most "secure" sharing tools still hold the encryption keys on their servers. They
						<em>promise</em> not to look at your data, but technically they can. If their server is
						compromised, subpoenaed, or operated by a malicious insider — your secrets are exposed.
					</p>
				</div>
			</div>

			<!-- Our Solution -->
			<div>
				<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">Our Solution</h2>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>
						PassMyPass uses <strong class="text-white">true zero-knowledge architecture</strong>.
						The encryption key is generated in your browser and embedded in the share link's URL
						fragment — the part after the <code class="text-red-400">#</code> symbol — which is
						<strong class="text-white">never sent to our server</strong> by any browser.
					</p>
					<p>
						We store only ciphertext that we mathematically cannot decrypt. Even if our entire
						database were stolen, every secret would remain unreadable. Even if we were compelled
						by law to hand over data, we couldn't provide plaintext — because we never had it.
					</p>
				</div>
			</div>

			<!-- Core Principles -->
			<div>
				<h2 class="mb-6 text-xl font-bold text-white sm:text-2xl">Core Principles</h2>
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<ServerOff class="mb-3 h-6 w-6 text-red-500" />
						<h3 class="mb-1.5 text-sm font-semibold text-white">Zero Trust Required</h3>
						<p class="text-xs leading-relaxed text-neutral-500">
							You don't need to trust us. The cryptographic design makes it impossible for us to
							access your data, by construction — not by policy.
						</p>
					</div>
					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<Eye class="mb-3 h-6 w-6 text-red-500" />
						<h3 class="mb-1.5 text-sm font-semibold text-white">Transparency</h3>
						<p class="text-xs leading-relaxed text-neutral-500">
							All encryption happens in client-side JavaScript you can inspect. The security
							architecture is fully documented on our Security page.
						</p>
					</div>
					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<Shield class="mb-3 h-6 w-6 text-red-500" />
						<h3 class="mb-1.5 text-sm font-semibold text-white">Privacy by Design</h3>
						<p class="text-xs leading-relaxed text-neutral-500">
							No accounts, no cookies, no tracking, no analytics. IP addresses are hashed before
							storage. We collect the minimum data needed to operate.
						</p>
					</div>
					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5">
						<Heart class="mb-3 h-6 w-6 text-red-500" />
						<h3 class="mb-1.5 text-sm font-semibold text-white">Free for Everyone</h3>
						<p class="text-xs leading-relaxed text-neutral-500">
							Secure secret sharing should be accessible to everyone. PassMyPass is free with no
							usage limits, no premium tiers, and no paywalled features.
						</p>
					</div>
				</div>
			</div>

			<!-- Who It's For -->
			<div>
				<h2 class="mb-4 text-xl font-bold text-white sm:text-2xl">Who It's For</h2>
				<div class="space-y-4 text-sm leading-relaxed text-neutral-400 sm:text-base">
					<p>PassMyPass is built for anyone who needs to share sensitive data securely:</p>
					<ul class="list-disc space-y-2 pl-6">
						<li>
							<strong class="text-white">Developers</strong> sharing API keys, database
							credentials, and secrets with team members or contractors
						</li>
						<li>
							<strong class="text-white">IT Teams</strong> distributing passwords, WiFi
							credentials, and access keys to employees
						</li>
						<li>
							<strong class="text-white">HR Departments</strong> sending temporary credentials to
							new hires without using email
						</li>
						<li>
							<strong class="text-white">Anyone</strong> who needs to send sensitive information
							and wants it to disappear after being read
						</li>
					</ul>
				</div>
			</div>

			<!-- CTA -->
			<div class="text-center">
				<a
					href="/"
					class="inline-flex items-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-red-500/20 transition-all hover:bg-red-500 hover:shadow-xl hover:shadow-red-500/25 active:scale-[0.98]"
				>
					<Lock class="h-4 w-4" />
					Share a Secret Now
				</a>
			</div>
		</div>
	</section>
</main>

<Footer />
