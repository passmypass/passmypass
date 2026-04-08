<script lang="ts">
	import { generateChatKey, encodeBase64Url, createChatRoom, ApiError, Footer } from '$lib';
	import { Lock, MessageSquareLock, Copy, Check, ExternalLink, Loader2, CircleX } from '@lucide/svelte';

	type State = 'idle' | 'creating' | 'created' | 'error';

	let pageState: State = $state('idle');
	let roomLink = $state('');
	let errorMessage = $state('');
	let copied = $state(false);

	async function handleCreate() {
		pageState = 'creating';
		errorMessage = '';

		try {
			const key = generateChatKey();
			const response = await createChatRoom();
			const keyB64 = encodeBase64Url(key);
			roomLink = `${window.location.origin}/c/${response.room_id}#${keyB64}`;
			pageState = 'created';
		} catch (err) {
			console.error('Failed to create chat room:', err);
			if (err instanceof ApiError) {
				errorMessage = err.message;
			} else {
				errorMessage = 'Failed to create chat room. Please try again.';
			}
			pageState = 'error';
		}
	}

	async function copyToClipboard() {
		try {
			await navigator.clipboard.writeText(roomLink);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		} catch {
			const textArea = document.createElement('textarea');
			textArea.value = roomLink;
			document.body.appendChild(textArea);
			textArea.select();
			document.execCommand('copy');
			document.body.removeChild(textArea);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		}
	}

	function joinRoom() {
		window.location.href = roomLink;
	}

	function reset() {
		pageState = 'idle';
		roomLink = '';
		errorMessage = '';
		copied = false;
	}
</script>

<svelte:head>
	<title>Encrypted Chat Room - No Account Required | PassMyPass</title>
	<meta name="description" content="Create an ephemeral end-to-end encrypted chat room. Zero-knowledge, auto-destroys after 10 minutes. No sign-up, no logs, completely free." />
	<link rel="canonical" href="https://passmypass.com/chat/" />

	<!-- Open Graph -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/chat/" />
	<meta property="og:title" content="Encrypted Chat Room - No Account Required | PassMyPass" />
	<meta property="og:description" content="Ephemeral 1-on-1 encrypted chat. Zero-knowledge, auto-destroys after 10 minutes. No sign-up required." />
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="Encrypted Chat Room - No Account Required | PassMyPass" />
	<meta name="twitter:description" content="Ephemeral 1-on-1 encrypted chat. Zero-knowledge, auto-destroys after 10 minutes." />
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />

	<!-- Chat page JSON-LD -->
	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'WebApplication',
		name: 'PassMyPass Encrypted Chat',
		description: 'Ephemeral end-to-end encrypted 1-on-1 chat rooms with auto-destruction',
		url: 'https://passmypass.com/chat/',
		applicationCategory: 'SecurityApplication',
		operatingSystem: 'Any',
		offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' }
	})}</script>`}
</svelte:head>

	<main class="flex-1">
		<div class="container mx-auto max-w-xl px-4 py-6 sm:py-10">
			<!-- Header -->
			<header class="mb-6 text-center sm:mb-10">
				<h1 class="text-2xl font-bold tracking-tight sm:text-3xl">Secret Chat Room</h1>
				<p class="mt-1.5 text-sm text-neutral-400 sm:text-base">End-to-end encrypted ephemeral conversations</p>
			</header>

			{#if pageState === 'idle' || pageState === 'creating' || pageState === 'error'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-xl backdrop-blur-sm sm:p-6">
					<div class="mb-5 text-center sm:mb-6">
						<div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-neutral-800 sm:mb-4 sm:h-14 sm:w-14">
							<MessageSquareLock class="h-6 w-6 text-red-500 sm:h-7 sm:w-7" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Ephemeral Encrypted Chat</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">
							1-on-1 end-to-end encrypted chat. No logs, no history.
						</p>
					</div>

					<div class="mb-5 space-y-2 text-xs text-neutral-400 sm:mb-6 sm:text-sm">
						<div class="flex items-start gap-2">
							<span class="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500"></span>
							<span>Room auto-destroys after <strong class="text-neutral-300">10 minutes</strong></span>
						</div>
						<div class="flex items-start gap-2">
							<span class="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500"></span>
							<span>Encryption key stays in your browser - server sees only ciphertext</span>
						</div>
						<div class="flex items-start gap-2">
							<span class="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500"></span>
							<span>Either party closing the tab ends the chat</span>
						</div>
					</div>

					{#if errorMessage}
						<div class="mb-4 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
							<CircleX class="mt-0.5 h-5 w-5 shrink-0" />
							{errorMessage}
						</div>
					{/if}

					<button
						onclick={handleCreate}
						disabled={pageState === 'creating'}
						class="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-red-600 py-3.5 font-semibold text-white transition-all hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
					>
						{#if pageState === 'creating'}
							<Loader2 class="h-5 w-5 animate-spin" />
							Creating Room...
						{:else}
							<MessageSquareLock class="h-5 w-5" />
							Create Secret Room
						{/if}
					</button>
				</div>

				<!-- Cross-link to secrets -->
				<div class="mt-6 text-center sm:mt-8">
					<a href="/" class="inline-flex items-center gap-2 text-sm text-neutral-500 transition hover:text-neutral-300">
						<Lock class="h-4 w-4" />
						Need to share a secret? Try One-Time Secret
					</a>
				</div>

			{:else if pageState === 'created'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-xl backdrop-blur-sm sm:p-6">
					<div class="mb-5 text-center sm:mb-6">
						<div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-neutral-800 sm:mb-4 sm:h-14 sm:w-14">
							<Check class="h-6 w-6 text-emerald-500 sm:h-7 sm:w-7" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Room Created</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">Share the link below with your chat partner</p>
					</div>

					<div class="mb-4 sm:mb-5">
						<div class="flex flex-col gap-2 sm:relative sm:flex-row sm:gap-0">
							<input
								type="text"
								readonly
								value={roomLink}
								class="min-h-[44px] w-full rounded-xl border border-neutral-700 bg-neutral-950 p-3 font-mono text-base text-white sm:p-4 sm:pr-28 sm:text-sm"
							/>
							<button
								onclick={copyToClipboard}
								class="min-h-[44px] w-full rounded-xl bg-red-600 px-4 py-2.5 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:absolute sm:right-2 sm:top-1/2 sm:w-auto sm:-translate-y-1/2 sm:rounded-lg sm:py-2 sm:min-h-0"
							>
								{#if copied}
									<span class="inline-flex items-center gap-1.5">
										<Check class="h-4 w-4" />
										Copied!
									</span>
								{:else}
									<span class="inline-flex items-center gap-1.5">
										<Copy class="h-4 w-4" />
										Copy Link
									</span>
								{/if}
							</button>
						</div>
					</div>

					<button
						onclick={joinRoom}
						class="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-red-600 py-3.5 font-semibold text-white transition-all hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 active:scale-[0.98] mb-4"
					>
						<ExternalLink class="h-5 w-5" />
						Join Room
					</button>

					<button
						onclick={reset}
						class="min-h-[48px] w-full rounded-xl border border-neutral-700 bg-neutral-800/30 py-2.5 text-sm font-medium text-neutral-300 transition active:scale-[0.98] hover:bg-neutral-800 hover:text-white sm:py-3 sm:text-base"
					>
						Create Another Room
					</button>
				</div>
			{/if}
		</div>
	</main>

	<Footer />
