<script lang="ts">
	import { Footer } from '$lib';
	import { ArrowRight, Calendar, Clock } from '@lucide/svelte';

	const posts = [
		{
			slug: 'how-to-share-passwords-securely',
			title: 'How to Share Passwords Securely in 2026',
			description:
				'Email, Slack, and text messages are the worst ways to share credentials. Here are 4 safer methods, and why one-time encrypted links beat them all.',
			date: '2026-04-08',
			readTime: '6 min read',
			category: 'Guide'
		},
		{
			slug: 'server-side-vs-zero-knowledge-encryption',
			title: 'Server-Side vs Zero-Knowledge Encryption: Which Actually Protects Your Secrets?',
			description:
				"Most secret sharing tools encrypt on the server — meaning they can read your data. Learn why zero-knowledge client-side encryption is the only architecture that truly protects your secrets.",
			date: '2026-04-08',
			readTime: '5 min read',
			category: 'Security'
		},
		{
			slug: 'zero-knowledge-encryption-explained',
			title: 'Zero-Knowledge Encryption Explained: How PassMyPass Protects Your Data',
			description:
				"A technical but accessible explanation of how zero-knowledge architecture works, why it's superior to server-side encryption, and how PassMyPass implements it.",
			date: '2026-04-08',
			readTime: '7 min read',
			category: 'Security'
		}
	];
</script>

<svelte:head>
	<title>Blog - PassMyPass | Security Guides & Zero-Knowledge Encryption</title>
	<meta
		name="description"
		content="Security guides, encryption explainers, and best practices for sharing passwords and sensitive data. From the team behind PassMyPass."
	/>
	<link rel="canonical" href="https://passmypass.com/blog/" />

	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/blog/" />
	<meta property="og:title" content="Blog - PassMyPass" />
	<meta
		property="og:description"
		content="Security guides, encryption explainers, and best practices for sharing sensitive data."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="Blog - PassMyPass" />
	<meta
		name="twitter:description"
		content="Security guides, encryption explainers, and best practices for sharing sensitive data."
	/>
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />
</svelte:head>

<main class="flex-1">
	<section class="relative overflow-hidden">
		<div
			class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-950/20 via-transparent to-transparent"
		></div>
		<div class="container mx-auto max-w-4xl px-4 py-12 sm:py-20">
			<div class="text-center">
				<h1 class="mb-4 text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">Blog</h1>
				<p class="mx-auto max-w-xl text-base leading-relaxed text-neutral-400 sm:text-lg">
					Security guides, encryption explainers, and best practices for sharing sensitive data
					safely.
				</p>
			</div>
		</div>
	</section>

	<section class="container mx-auto max-w-4xl px-4 pb-16">
		<div class="space-y-6">
			{#each posts as post}
				<a
					href="/blog/{post.slug}/"
					class="group block rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-6 transition hover:border-neutral-700 hover:bg-neutral-900/60 sm:p-8"
				>
					<div class="mb-3 flex items-center gap-3 text-xs text-neutral-500">
						<span
							class="rounded-full bg-red-500/10 px-2.5 py-0.5 font-medium text-red-400"
						>
							{post.category}
						</span>
						<span class="flex items-center gap-1">
							<Calendar class="h-3 w-3" />
							{new Date(post.date).toLocaleDateString('en-US', {
								year: 'numeric',
								month: 'long',
								day: 'numeric'
							})}
						</span>
						<span class="flex items-center gap-1">
							<Clock class="h-3 w-3" />
							{post.readTime}
						</span>
					</div>
					<h2
						class="mb-2 text-lg font-bold text-white transition group-hover:text-red-400 sm:text-xl"
					>
						{post.title}
					</h2>
					<p class="mb-4 text-sm leading-relaxed text-neutral-400">{post.description}</p>
					<span
						class="inline-flex items-center gap-1.5 text-sm font-medium text-red-500 transition group-hover:gap-2.5"
					>
						Read article
						<ArrowRight class="h-4 w-4" />
					</span>
				</a>
			{/each}
		</div>
	</section>
</main>

<Footer />
