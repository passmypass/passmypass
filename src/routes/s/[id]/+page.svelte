<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import {
		decodeBase64Url,
		encodeBase64Url,
		decryptSecret,
		isPasswordProtected,
		getSecretStatus,
		claimSecret,
		ApiError,
		Footer
	} from '$lib';
	import { Lock, LockOpen, Eye, EyeOff, Check, Copy, Clock, CircleAlert, CircleX, Trash2, Frown, Info, Loader2, AlertTriangle } from '@lucide/svelte';

	type State =
		| 'loading'
		| 'ready'
		| 'password_required'
		| 'revealing'
		| 'revealed'
		| 'consumed'
		| 'expired'
		| 'not_found'
		| 'error';

	const { data } = $props<{ data: { secretId: string } }>();

	let pageState: State = $state('loading');
	let secretText = $state('');
	let errorMessage = $state('');
	let copied = $state(false);
	let expiresAt: Date | null = $state(null);
	let autoCleared = $state(false);
	let password = $state('');
	let showPassword = $state(false);
	let passwordError = $state('');
	let needsPassword = $state(false);
	let showSecretContent = $state(false);

	let encryptionKey: Uint8Array | null = null;
	let claimToken: Uint8Array | null = null;
	let storedCiphertext: Uint8Array | null = null;
	let storedNonce: Uint8Array | null = null;
	let storedAad: Uint8Array | null = null;

	const AUTO_CLEAR_DELAY = 60000;

	onMount(async () => {
		if (!browser) return;

		const secretId = data.secretId;
		const fragment = window.location.hash.slice(1);

		if (fragment) {
			window.history.replaceState(null, '', window.location.pathname);
		}

		if (!fragment) {
			errorMessage = 'Invalid link - missing encryption key';
			pageState = 'error';
			return;
		}

		const parts = fragment.split('.');
		if (parts.length !== 2) {
			errorMessage = 'Invalid link format';
			pageState = 'error';
			return;
		}

		try {
			encryptionKey = decodeBase64Url(parts[0]);
			claimToken = decodeBase64Url(parts[1]);

			if (encryptionKey.length !== 32 || claimToken.length !== 32) {
				throw new Error('Invalid key or token length');
			}
		} catch {
			errorMessage = 'Invalid link - corrupted encryption key';
			pageState = 'error';
			return;
		}

		try {
			const status = await getSecretStatus(secretId);

			if (!status.exists) {
				pageState = 'not_found';
				return;
			}

			if (status.consumed) {
				pageState = 'consumed';
				return;
			}

			if (status.expired) {
				pageState = 'expired';
				return;
			}

			if (status.expires_at) {
				expiresAt = new Date(status.expires_at);
			}

			pageState = 'ready';
		} catch (err) {
			console.error('Failed to check secret status:', err);
			if (err instanceof ApiError && err.status === 404) {
				pageState = 'not_found';
			} else {
				errorMessage = 'Failed to check secret availability';
				pageState = 'error';
			}
		}
	});

	async function revealSecret() {
		if (!encryptionKey || !claimToken) return;

		pageState = 'revealing';

		const secretId = data.secretId;

		try {
			const response = await claimSecret(secretId, {
				claim_token_b64u: encodeBase64Url(claimToken)
			});

			const ciphertext = decodeBase64Url(response.ciphertext_b64u);
			const nonce = decodeBase64Url(response.nonce_b64u);
			const aad = response.aad_b64u ? decodeBase64Url(response.aad_b64u) : undefined;

			// Check if password protected
			if (aad && isPasswordProtected(aad)) {
				storedCiphertext = ciphertext;
				storedNonce = nonce;
				storedAad = aad;
				needsPassword = true;
				pageState = 'password_required';
				return;
			}

			secretText = await decryptSecret(ciphertext, encryptionKey, nonce, aad);
			pageState = 'revealed';

			setTimeout(() => {
				if (pageState === 'revealed') {
					secretText = '';
					autoCleared = true;
				}
			}, AUTO_CLEAR_DELAY);
		} catch (err) {
			console.error('Failed to reveal secret:', err);
			if (err instanceof ApiError) {
				if (err.status === 404) {
					pageState = 'consumed';
				} else {
					errorMessage = err.message;
					pageState = 'error';
				}
			} else if (err instanceof Error && err.name === 'OperationError') {
				errorMessage = 'Failed to decrypt - the link may be corrupted';
				pageState = 'error';
			} else {
				errorMessage = 'Failed to reveal secret';
				pageState = 'error';
			}
		}
	}

	async function decryptWithPassword() {
		if (!encryptionKey || !storedCiphertext || !storedNonce || !storedAad) return;
		if (!password.trim()) {
			passwordError = 'Please enter the password';
			return;
		}

		passwordError = '';
		pageState = 'revealing';

		try {
			secretText = await decryptSecret(storedCiphertext, encryptionKey, storedNonce, storedAad, password);
			pageState = 'revealed';
			password = '';

			setTimeout(() => {
				if (pageState === 'revealed') {
					secretText = '';
					autoCleared = true;
				}
			}, AUTO_CLEAR_DELAY);
		} catch (err) {
			console.error('Failed to decrypt with password:', err);
			if (err instanceof Error && err.name === 'OperationError') {
				passwordError = 'Incorrect password';
				pageState = 'password_required';
			} else {
				errorMessage = 'Failed to decrypt secret';
				pageState = 'error';
			}
		}
	}

	async function copyToClipboard() {
		try {
			await navigator.clipboard.writeText(secretText);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		} catch {
			const textArea = document.createElement('textarea');
			textArea.value = secretText;
			document.body.appendChild(textArea);
			textArea.select();
			document.execCommand('copy');
			document.body.removeChild(textArea);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		}
	}

	function formatTimeRemaining(date: Date): string {
		const now = new Date();
		const diff = date.getTime() - now.getTime();
		if (diff <= 0) return 'expired';

		const minutes = Math.floor(diff / 60000);
		const seconds = Math.floor((diff % 60000) / 1000);

		if (minutes > 0) {
			return `${minutes}m ${seconds}s`;
		}
		return `${seconds}s`;
	}
</script>

<svelte:head>
	<title>View Secret - PassMyPass</title>
	<meta name="robots" content="noindex, nofollow" />
</svelte:head>

	<main class="flex-1">
		<div class="container mx-auto max-w-xl px-4 py-6 sm:py-10">
			<!-- Header -->
			<header class="mb-6 text-center sm:mb-10">
				<h1 class="text-2xl font-bold tracking-tight sm:text-3xl">View Secret</h1>
				<p class="mt-1.5 text-sm text-neutral-400 sm:text-base">Secure one-time secret sharing</p>
			</header>

			{#if pageState === 'loading'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8">
					<Loader2 class="mx-auto mb-3 h-10 w-10 animate-spin text-red-500 sm:mb-4 sm:h-12 sm:w-12" />
					<p class="text-sm text-neutral-400 sm:text-base">Checking secret availability...</p>
				</div>

			{:else if pageState === 'ready'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-xl backdrop-blur-sm sm:p-6">
					<div class="mb-5 text-center sm:mb-6">
						<div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-neutral-800 sm:mb-4 sm:h-14 sm:w-14">
							<Lock class="h-6 w-6 text-red-500 sm:h-7 sm:w-7" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">One-Time Secret Ready</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">A secure secret awaits your retrieval</p>
						{#if expiresAt}
							{@const timeRemaining = expiresAt.getTime() - new Date().getTime()}
							<div class="mt-2.5 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium sm:mt-3 sm:px-3 sm:text-xs {timeRemaining < 60000 ? 'bg-amber-500/10 text-amber-400' : 'bg-neutral-800/50 text-neutral-400'}">
								<Clock class="h-3 w-3 sm:h-3.5 sm:w-3.5" />
								Expires in {formatTimeRemaining(expiresAt)}
							</div>
						{/if}
					</div>

					<!-- Burn Confirmation Warning -->
					<div class="mb-4 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 sm:mb-5">
						<div class="flex gap-3">
							<AlertTriangle class="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
							<div class="text-xs sm:text-sm">
								<p class="font-semibold text-amber-300">This secret will be permanently deleted</p>
								<p class="mt-1 text-amber-400/80">
									Once you click "Reveal Secret", the content is decrypted in your browser and
									<strong>permanently destroyed</strong> from our servers. This action cannot be undone.
									Make sure you are ready to save or use the secret.
								</p>
							</div>
						</div>
					</div>

					<button
						onclick={revealSecret}
						class="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-red-600 py-3 font-semibold text-white transition-all active:scale-[0.98] hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 sm:py-3.5"
					>
						<LockOpen class="h-5 w-5" />
						Reveal Secret
					</button>
				</div>

			{:else if pageState === 'password_required'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-xl backdrop-blur-sm sm:p-6">
					<div class="mb-5 text-center sm:mb-6">
						<div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-neutral-800 sm:mb-4 sm:h-14 sm:w-14">
							<Lock class="h-6 w-6 text-red-500 sm:h-7 sm:w-7" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Password Required</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">This secret is password protected</p>
					</div>

					<form onsubmit={(e) => { e.preventDefault(); decryptWithPassword(); }}>
						<div class="mb-4">
							<label for="decrypt-password" class="mb-2 block text-sm font-medium text-neutral-200">
								Enter password
							</label>
							<div class="relative">
								<input
									type={showPassword ? 'text' : 'password'}
									id="decrypt-password"
									bind:value={password}
									placeholder="Password from sender"
									autocomplete="off"
									class="min-h-[44px] w-full rounded-xl border border-neutral-700 bg-neutral-950 p-3 pr-12 text-white placeholder-neutral-500 transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 sm:p-3.5"
								/>
								<button
									type="button"
									onclick={() => showPassword = !showPassword}
									class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-neutral-400 hover:text-neutral-300"
									aria-label={showPassword ? 'Hide password' : 'Show password'}
								>
									{#if showPassword}
										<EyeOff class="h-5 w-5" />
									{:else}
										<Eye class="h-5 w-5" />
									{/if}
								</button>
							</div>
							{#if passwordError}
								<p class="mt-2 flex items-center gap-1.5 text-[11px] text-red-400 sm:text-xs">
									<CircleX class="h-3 w-3" />
									{passwordError}
								</p>
							{/if}
						</div>

						<button
							type="submit"
							disabled={!password.trim()}
							class="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-red-600 py-3 font-semibold text-white transition-all active:scale-[0.98] hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 disabled:cursor-not-allowed disabled:opacity-40 sm:py-3.5"
						>
							<LockOpen class="h-5 w-5" />
							Decrypt Secret
						</button>
					</form>
				</div>

			{:else if pageState === 'revealing'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8">
					<Loader2 class="mx-auto mb-3 h-10 w-10 animate-spin text-red-500 sm:mb-4 sm:h-12 sm:w-12" />
					<p class="text-sm text-neutral-400 sm:text-base">Decrypting secret...</p>
				</div>

			{:else if pageState === 'revealed'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-xl backdrop-blur-sm sm:p-6">
					<div class="mb-5 text-center sm:mb-6">
						<div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-neutral-800 sm:mb-4 sm:h-14 sm:w-14">
							<LockOpen class="h-6 w-6 text-red-500 sm:h-7 sm:w-7" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Secret Revealed</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">Decrypted locally in your browser</p>
					</div>

					{#if autoCleared}
						<div class="rounded-xl border border-neutral-700 bg-neutral-950 p-6 text-center sm:p-8">
							<Trash2 class="mx-auto mb-3 h-8 w-8 text-neutral-600 sm:h-10 sm:w-10" />
							<p class="text-sm font-medium text-neutral-300">Secret Destroyed</p>
							<p class="mt-1 text-xs text-neutral-500">This secret has been cleared from memory and can no longer be accessed.</p>
						</div>
					{:else}
						<!-- Text secret UI -->
						<div class="mb-4">
							<div class="relative">
								<textarea
									readonly
									value={secretText}
									rows="6"
									class="w-full resize-none rounded-xl border border-neutral-700 bg-neutral-950 p-3 pr-12 font-mono text-base leading-relaxed text-white sm:p-4 sm:text-sm"
									style={!showSecretContent ? '-webkit-text-security: disc; overflow-x: hidden; word-break: break-all;' : 'overflow-x: hidden; word-break: break-all;'}
								></textarea>
								<button
									type="button"
									onclick={() => showSecretContent = !showSecretContent}
									class="absolute right-3 top-3 p-1 text-neutral-400 hover:text-neutral-300"
									aria-label={showSecretContent ? 'Hide secret' : 'Show secret'}
								>
									{#if showSecretContent}
										<EyeOff class="h-5 w-5" />
									{:else}
										<Eye class="h-5 w-5" />
									{/if}
								</button>
							</div>
						</div>

						<button
							onclick={copyToClipboard}
							class="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-red-600 py-3 font-semibold text-white transition-all active:scale-[0.98] hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 sm:py-3.5"
						>
							{#if copied}
								<Check class="h-5 w-5" />
								Copied!
							{:else}
								<Copy class="h-5 w-5" />
								Copy to Clipboard
							{/if}
						</button>

						<p class="mt-3 text-center text-[11px] text-neutral-500 sm:mt-4 sm:text-xs">
							This secret will be cleared from this page in 1 minute.
						</p>
					{/if}

					<div class="mt-5 border-t border-neutral-800 pt-5 sm:mt-6 sm:pt-6">
						<a
							href="/"
							class="block min-h-[48px] w-full rounded-xl border border-neutral-700 bg-neutral-800 py-3 text-center text-sm font-medium leading-6 text-white transition active:scale-[0.98] hover:bg-neutral-700 sm:py-3 sm:text-base"
						>
							Create Your Own Secret
						</a>
					</div>
				</div>

			{:else if pageState === 'consumed'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8">
					<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/20 sm:mb-4 sm:h-16 sm:w-16">
						<CircleX class="h-7 w-7 text-red-400 sm:h-8 sm:w-8" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Already Viewed</h2>
					<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">This secret has already been revealed and is no longer available.</p>
					<a
						href="/"
							class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
					>
						Create New Secret
					</a>
				</div>

			{:else if pageState === 'expired'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8">
					<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/20 sm:mb-4 sm:h-16 sm:w-16">
						<Clock class="h-7 w-7 text-amber-400 sm:h-8 sm:w-8" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Link Expired</h2>
					<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">This secret has expired and is no longer available.</p>
					<a
						href="/"
							class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
					>
						Create New Secret
					</a>
				</div>

			{:else if pageState === 'not_found'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8">
					<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-neutral-700/50 sm:mb-4 sm:h-16 sm:w-16">
						<Frown class="h-7 w-7 text-neutral-400 sm:h-8 sm:w-8" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Not Found</h2>
					<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">This secret doesn't exist or the link is invalid.</p>
					<a
						href="/"
							class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
					>
						Create New Secret
					</a>
				</div>

			{:else if pageState === 'error'}
				<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8">
					<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/20 sm:mb-4 sm:h-16 sm:w-16">
						<CircleAlert class="h-7 w-7 text-red-400 sm:h-8 sm:w-8" />
					</div>
					<h2 class="text-xl font-bold text-white sm:text-2xl">Error</h2>
					<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">{errorMessage}</p>
					<a
						href="/"
							class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
					>
						Go Home
					</a>
				</div>
			{/if}
		</div>
	</main>

	<Footer />
