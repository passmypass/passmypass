<script lang="ts">
	import { slide } from 'svelte/transition';
	import { encryptSecret, encodeBase64Url, createSecret, ApiError, Footer } from '$lib';
	import {
		Lock,
		Eye,
		EyeOff,
		ChevronRight,
		ChevronDown,
		Check,
		Copy,
		Info,
		CircleX,
		Loader2,
		MessageSquareLock,
		Shield,
		Zap,
		Trash2,
		KeyRound,
		ServerOff,
		Timer,
		UserX,
		ArrowRight,
		ShieldCheck,
		QrCode
	} from '@lucide/svelte';
	import QRCode from 'qrcode';

	type State = 'input' | 'creating' | 'success' | 'error';

	let pageState: State = $state('input');
	let secretText = $state('');
	let password = $state('');
	let showPassword = $state(false);
	let showSecretText = $state(false);
	let showPasswordSection = $state(false);
	let expiresInMinutes = $state(10);
	let shareLink = $state('');
	let errorMessage = $state('');
	let copied = $state(false);
	let isDropdownOpen = $state(false);
	let isPasswordProtected = $state(false);
	let qrCodeDataUrl = $state('');
	let showQR = $state(false);

	// FAQ accordion state
	let openFaq = $state(-1);

	const MAX_SECRET_LENGTH = 10000;

	const expiryOptions = [
		{ value: 5, label: '5 minutes' },
		{ value: 10, label: '10 minutes' },
		{ value: 30, label: '30 minutes' },
		{ value: 60, label: '1 hour' },
		{ value: 360, label: '6 hours' },
		{ value: 720, label: '12 hours' },
		{ value: 1440, label: '24 hours' }
	];

	const faqItems = [
		{
			q: 'How does PassMyPass protect my secrets?',
			a: 'Your secret is encrypted directly in your browser using AES-256-GCM, the same standard used by governments and banks. The encryption key is embedded in the share link fragment (#) which is never sent to our server. We only store ciphertext that we mathematically cannot decrypt.'
		},
		{
			q: 'Can PassMyPass read my secrets?',
			a: "No. PassMyPass uses a zero-knowledge architecture. The encryption key exists only in the share link and your browser's memory. Our server stores only encrypted data — even if our database were compromised, your secrets would remain unreadable."
		},
		{
			q: 'What happens after the secret is viewed?',
			a: 'The secret is permanently destroyed from our database the instant it is viewed. There are no backups, no copies, no way to recover it. The link becomes permanently invalid.'
		},
		{
			q: 'Is PassMyPass really free?',
			a: 'Yes, completely free with no limits on usage. No account required, no ads, no tracking. We believe secure secret sharing should be accessible to everyone.'
		},
		{
			q: 'How is PassMyPass different from emailing passwords?',
			a: 'Email is stored on multiple servers, often unencrypted, and persists indefinitely. PassMyPass links are end-to-end encrypted, work exactly once, and auto-destruct. Even if someone intercepts the link later, the secret is already gone.'
		},
		{
			q: 'What is the encrypted chat feature?',
			a: 'Secret Chat Rooms are ephemeral, end-to-end encrypted 1-on-1 chat rooms. Messages are encrypted in your browser before being relayed through our server. Rooms auto-destroy after 10 minutes or when either person leaves. No messages are ever stored.'
		}
	];

	async function handleCreate() {
		if (!secretText.trim()) {
			errorMessage = 'Please enter a secret to share';
			pageState = 'error';
			return;
		}

		if (secretText.length > MAX_SECRET_LENGTH) {
			errorMessage = `Secret is too long. Maximum ${MAX_SECRET_LENGTH} characters.`;
			pageState = 'error';
			return;
		}

		pageState = 'creating';
		errorMessage = '';

		try {
			const encrypted = await encryptSecret(secretText, password || undefined);

			const response = await createSecret({
				ciphertext_b64u: encodeBase64Url(encrypted.ciphertext),
				nonce_b64u: encodeBase64Url(encrypted.nonce),
				aad_b64u: encodeBase64Url(encrypted.aad),
				claim_hash_b64u: encodeBase64Url(encrypted.claimHash),
				expires_in_seconds: expiresInMinutes * 60
			});

			const keyB64 = encodeBase64Url(encrypted.encryptionKey);
			const claimB64 = encodeBase64Url(encrypted.claimToken);
			shareLink = `${window.location.origin}/s/${response.id}#${keyB64}.${claimB64}`;

			isPasswordProtected = encrypted.passwordProtected;
			secretText = '';
			password = '';
			pageState = 'success';

			// Generate QR code
			try {
				qrCodeDataUrl = await QRCode.toDataURL(shareLink, {
					width: 200,
					margin: 2,
					color: { dark: '#ffffff', light: '#0a0a0a' }
				});
			} catch {
				// QR generation is optional
			}
		} catch (err) {
			console.error('Failed to create secret:', err);
			if (err instanceof ApiError) {
				errorMessage = err.message;
			} else {
				errorMessage = 'Failed to create secret. Please try again.';
			}
			pageState = 'error';
		}
	}

	function selectExpiry(value: number) {
		expiresInMinutes = value;
		isDropdownOpen = false;
	}

	async function copyToClipboard() {
		try {
			await navigator.clipboard.writeText(shareLink);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		} catch {
			const textArea = document.createElement('textarea');
			textArea.value = shareLink;
			document.body.appendChild(textArea);
			textArea.select();
			document.execCommand('copy');
			document.body.removeChild(textArea);
			copied = true;
			setTimeout(() => (copied = false), 2000);
		}
	}

	function reset() {
		pageState = 'input';
		secretText = '';
		password = '';
		showPassword = false;
		showSecretText = false;
		showPasswordSection = false;
		shareLink = '';
		errorMessage = '';
		expiresInMinutes = 10;
		isDropdownOpen = false;
		isPasswordProtected = false;
		qrCodeDataUrl = '';
		showQR = false;
	}

	function formatExpiry(minutes: number): string {
		if (minutes < 60) return `${minutes} minutes`;
		if (minutes < 1440) return `${minutes / 60} hour${minutes > 60 ? 's' : ''}`;
		return `${minutes / 1440} day${minutes > 1440 ? 's' : ''}`;
	}
</script>

<svelte:head>
	<title>PassMyPass - Secure One-Time Secret Sharing | Zero-Knowledge Encryption</title>
	<meta
		name="description"
		content="Share passwords, API keys & sensitive data with zero-knowledge encryption. AES-256-GCM, one-time viewing, auto-destruct up to 24 hours. No sign-up. Free."
	/>
	<link rel="canonical" href="https://passmypass.com/" />

	<!-- Open Graph -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/" />
	<meta property="og:title" content="PassMyPass - Secure One-Time Secret Sharing" />
	<meta
		property="og:description"
		content="Share passwords and sensitive data with zero-knowledge encryption. View once, then destroyed forever. No account required."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="PassMyPass - Secure One-Time Secret Sharing" />
	<meta
		name="twitter:description"
		content="Share passwords and sensitive data with zero-knowledge encryption. View once, then destroyed forever."
	/>
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />

	<!-- FAQ Schema -->
	{@html `<script type="application/ld+json">${JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'FAQPage',
		mainEntity: faqItems.map((item) => ({
			'@type': 'Question',
			name: item.q,
			acceptedAnswer: { '@type': 'Answer', text: item.a }
		}))
	})}</script>`}
</svelte:head>

<main class="flex-1">
	<!-- Hero Section -->
	<section class="relative overflow-hidden">
		<!-- Background glow -->
		<div
			class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-950/20 via-transparent to-transparent"
		></div>

		<div class="container mx-auto max-w-5xl px-4 pb-4 pt-6 sm:pb-16 sm:pt-20">
			<div class="mx-auto max-w-3xl text-center">
				<div
					class="mb-3 hidden items-center gap-2 rounded-full border border-neutral-800 bg-neutral-900/80 px-4 py-1.5 text-xs font-medium text-neutral-300 sm:inline-flex"
				>
					<ShieldCheck class="h-3.5 w-3.5 text-red-500" />
					Zero-knowledge end-to-end encryption
				</div>

				<h1
					class="mb-2 text-3xl font-extrabold leading-tight tracking-tight sm:mb-4 sm:text-5xl md:text-6xl"
				>
					Share Secrets.
					<span class="bg-gradient-to-r from-red-500 to-red-400 bg-clip-text text-transparent"
						>Not Risk.</span
					>
				</h1>

				<p
					class="mx-auto mb-4 max-w-xl text-sm leading-relaxed text-neutral-400 sm:mb-8 sm:text-lg"
				>
					Send passwords, API keys, and sensitive data through self-destructing encrypted links.
					The server never sees your data.
				</p>

				<!-- Trust badges — hidden on mobile -->
				<div
					class="hidden flex-wrap items-center justify-center gap-3 text-xs text-neutral-500 sm:flex"
				>
					<span class="flex items-center gap-1.5 rounded-full bg-neutral-900 px-3 py-1.5">
						<Shield class="h-3.5 w-3.5 text-red-500" />
						AES-256-GCM
					</span>
					<span class="flex items-center gap-1.5 rounded-full bg-neutral-900 px-3 py-1.5">
						<ServerOff class="h-3.5 w-3.5 text-red-500" />
						Zero-Knowledge
					</span>
					<span class="flex items-center gap-1.5 rounded-full bg-neutral-900 px-3 py-1.5">
						<UserX class="h-3.5 w-3.5 text-red-500" />
						No Account Needed
					</span>
					<span class="flex items-center gap-1.5 rounded-full bg-neutral-900 px-3 py-1.5">
						<Timer class="h-3.5 w-3.5 text-red-500" />
						Auto-Destruct
					</span>
				</div>
			</div>
		</div>
	</section>

	<!-- Create Secret Form -->
	<section id="create" class="relative">
		<div class="container mx-auto max-w-xl px-4 pb-10 sm:pb-16">
			{#if pageState === 'input' || pageState === 'creating' || pageState === 'error'}
				<div
					class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-2xl shadow-red-500/5 backdrop-blur-sm sm:p-6"
				>
					<form
						onsubmit={(e) => {
							e.preventDefault();
							handleCreate();
						}}
					>
						<div class="mb-4 sm:mb-5">
							<label for="secret" class="mb-2 block text-sm font-medium text-neutral-200">
								Your Secret
							</label>

							<div class="relative">
								<textarea
									id="secret"
									bind:value={secretText}
									placeholder="Paste your password, API key, or sensitive data here..."
									rows="5"
									maxlength={MAX_SECRET_LENGTH}
									class="w-full resize-none rounded-xl border border-neutral-700 bg-neutral-950 p-3 pr-12 font-mono text-base leading-relaxed text-white placeholder-neutral-600 transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 sm:p-4 sm:text-sm"
									style={!showSecretText
										? '-webkit-text-security: disc; overflow-x: hidden; word-break: break-all;'
										: 'overflow-x: hidden; word-break: break-all;'}
									disabled={pageState === 'creating'}
								></textarea>
								{#if secretText}
									<button
										type="button"
										onclick={() => (showSecretText = !showSecretText)}
										class="absolute right-3 top-3 p-1 text-neutral-400 hover:text-neutral-300"
										aria-label={showSecretText ? 'Hide secret' : 'Show secret'}
									>
										{#if showSecretText}
											<EyeOff class="h-5 w-5" />
										{:else}
											<Eye class="h-5 w-5" />
										{/if}
									</button>
								{/if}
							</div>
							{#if secretText.length > 0}
								<p class="mt-1.5 text-right text-[11px] text-neutral-600">
									{secretText.length.toLocaleString()} / {MAX_SECRET_LENGTH.toLocaleString()}
								</p>
							{/if}
						</div>

						<div class="mb-4 grid grid-cols-1 gap-4 sm:mb-5 sm:grid-cols-2">
							<!-- Expiry -->
							<div>
								<label for="expiry" class="mb-2 block text-sm font-medium text-neutral-200">
									Expires in
								</label>
								<div class="relative">
									<button
										type="button"
										id="expiry"
										onclick={() => (isDropdownOpen = !isDropdownOpen)}
										disabled={pageState === 'creating'}
										class="relative min-h-[44px] w-full cursor-pointer rounded-xl border border-neutral-700 bg-neutral-950 p-3 text-left text-white transition-all hover:border-neutral-600 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 disabled:cursor-not-allowed disabled:opacity-50"
									>
										<span class="block truncate text-sm">
											{expiryOptions.find((o) => o.value === expiresInMinutes)?.label}
										</span>
										<span
											class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3"
										>
											<ChevronDown class="h-4 w-4 text-neutral-400" />
										</span>
									</button>

									{#if isDropdownOpen}
										<div
											class="fixed inset-0 z-10"
											onclick={() => (isDropdownOpen = false)}
											role="presentation"
										></div>

										<div
											class="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-xl border border-neutral-700 bg-neutral-900 shadow-2xl"
										>
											<div class="p-1">
												{#each expiryOptions as option}
													<button
														type="button"
														class="relative min-h-[40px] w-full cursor-pointer rounded-lg py-2.5 pl-3 pr-9 text-left text-sm text-neutral-200 hover:bg-neutral-800 hover:text-white focus:bg-neutral-800 focus:text-white focus:outline-none"
														onclick={() => selectExpiry(option.value)}
													>
														<span
															class="block truncate {expiresInMinutes === option.value
																? 'font-semibold text-white'
																: ''}"
														>
															{option.label}
														</span>
														{#if expiresInMinutes === option.value}
															<span
																class="absolute inset-y-0 right-0 flex items-center pr-3 text-red-500"
															>
																<Check class="h-4 w-4" />
															</span>
														{/if}
													</button>
												{/each}
											</div>
										</div>
									{/if}
								</div>
							</div>

							<!-- Password protection -->
							<div>
								<button
									type="button"
									onclick={() => {
										showPasswordSection = !showPasswordSection;
										if (!showPasswordSection) password = '';
									}}
									disabled={pageState === 'creating'}
									class="mb-2 flex items-center gap-1.5 text-sm font-medium text-neutral-200"
								>
									<KeyRound class="h-3.5 w-3.5 text-neutral-400" />
									Password
									<span class="text-xs font-normal text-neutral-600">(optional)</span>
								</button>

								{#if showPasswordSection}
									<div transition:slide={{ duration: 200 }}>
										<div class="relative">
											<input
												type={showPassword ? 'text' : 'password'}
												id="password"
												bind:value={password}
												placeholder="Enter a password"
												autocomplete="off"
												disabled={pageState === 'creating'}
												class="min-h-[44px] w-full rounded-xl border border-neutral-700 bg-neutral-950 p-3 pr-12 text-sm text-white placeholder-neutral-600 transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 disabled:cursor-not-allowed disabled:opacity-50"
											/>
											<button
												type="button"
												onclick={() => (showPassword = !showPassword)}
												class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-neutral-400 hover:text-neutral-300"
												aria-label={showPassword ? 'Hide password' : 'Show password'}
											>
												{#if showPassword}
													<EyeOff class="h-4 w-4" />
												{:else}
													<Eye class="h-4 w-4" />
												{/if}
											</button>
										</div>
										{#if password}
											<p
												class="mt-1.5 flex items-center gap-1.5 text-[10px] text-emerald-400 sm:text-[11px]"
											>
												<Check class="h-3 w-3" />
												Recipient needs this password
											</p>
										{/if}
									</div>
								{:else}
									<button
										type="button"
										onclick={() => (showPasswordSection = true)}
										disabled={pageState === 'creating'}
										class="min-h-[44px] w-full rounded-xl border border-dashed border-neutral-700 bg-neutral-950/50 p-3 text-left text-sm text-neutral-600 transition hover:border-neutral-600 hover:text-neutral-400"
									>
										Add password protection...
									</button>
								{/if}
							</div>
						</div>

						{#if errorMessage}
							<div
								class="mb-4 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-400"
							>
								<CircleX class="mt-0.5 h-4 w-4 shrink-0" />
								{errorMessage}
							</div>
						{/if}

						<button
							type="submit"
							disabled={pageState === 'creating' || !secretText.trim()}
							class="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-red-600 py-3.5 font-semibold text-white shadow-lg shadow-red-500/20 transition-all hover:bg-red-500 hover:shadow-xl hover:shadow-red-500/25 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
						>
							{#if pageState === 'creating'}
								<Loader2 class="h-5 w-5 animate-spin" />
								Encrypting...
							{:else}
								<Lock class="h-5 w-5" />
								Create Secure Link
							{/if}
						</button>
					</form>
				</div>
			{:else if pageState === 'success'}
				<div
					class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-2xl shadow-red-500/5 backdrop-blur-sm sm:p-6"
				>
					<div class="mb-5 text-center sm:mb-6">
						<div
							class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/10 sm:mb-4 sm:h-14 sm:w-14"
						>
							<Check class="h-6 w-6 text-emerald-500 sm:h-7 sm:w-7" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Secure Link Created</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2">
							Share this link with your recipient
						</p>
						{#if isPasswordProtected}
							<div
								class="mt-2.5 inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400 sm:mt-3 sm:px-3 sm:text-xs"
							>
								<Lock class="h-3 w-3 sm:h-3.5 sm:w-3.5" />
								Password protected
							</div>
						{/if}
					</div>

					<div class="mb-4 sm:mb-5">
						<div class="flex flex-col gap-2 sm:relative sm:flex-row sm:gap-0">
							<input
								type="text"
								readonly
								value={shareLink}
								class="min-h-[44px] w-full rounded-xl border border-neutral-700 bg-neutral-950 p-3 font-mono text-base text-white sm:p-4 sm:pr-28 sm:text-sm"
							/>
							<button
								onclick={copyToClipboard}
								class="min-h-[44px] w-full rounded-xl bg-red-600 px-4 py-2.5 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:absolute sm:right-2 sm:top-1/2 sm:min-h-0 sm:w-auto sm:-translate-y-1/2 sm:rounded-lg sm:py-2"
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

					<!-- QR Code toggle -->
					{#if qrCodeDataUrl}
						<div class="mb-4">
							<button
								onclick={() => (showQR = !showQR)}
								class="flex w-full items-center justify-center gap-2 rounded-xl border border-neutral-700 bg-neutral-800/30 py-2.5 text-sm text-neutral-400 transition hover:bg-neutral-800 hover:text-white"
							>
								<QrCode class="h-4 w-4" />
								{showQR ? 'Hide' : 'Show'} QR Code
							</button>
							{#if showQR}
								<div
									transition:slide={{ duration: 200 }}
									class="mt-3 flex justify-center rounded-xl bg-neutral-950 p-4"
								>
									<img src={qrCodeDataUrl} alt="QR code for secret link" class="h-48 w-48" />
								</div>
							{/if}
						</div>
					{/if}

					<div class="mb-4 rounded-xl border border-neutral-700 bg-neutral-800/50 p-3 sm:mb-5">
						<div class="flex gap-2.5">
							<Info class="mt-0.5 h-4 w-4 shrink-0 text-neutral-400" />
							<div class="text-xs sm:text-sm">
								<p class="font-medium text-neutral-200">Important</p>
								<ul class="mt-1 space-y-0.5 text-neutral-400">
									<li>&#8226; This link can be opened <strong>only once</strong></li>
									<li>&#8226; Expires in {formatExpiry(expiresInMinutes)}</li>
									{#if isPasswordProtected}
										<li>&#8226; Recipient needs the password you set</li>
									{/if}
									<li>&#8226; Cannot be recovered if lost</li>
								</ul>
							</div>
						</div>
					</div>

					<button
						onclick={reset}
						class="min-h-[48px] w-full rounded-xl border border-neutral-700 bg-neutral-800/30 py-2.5 text-sm font-medium text-neutral-300 transition active:scale-[0.98] hover:bg-neutral-800 hover:text-white"
					>
						Create Another Secret
					</button>
				</div>
			{/if}
		</div>
	</section>

	<!-- Features Section -->
	<section class="border-t border-neutral-800/30 py-16 sm:py-20">
		<div class="container mx-auto max-w-5xl px-4">
			<div class="mb-10 text-center sm:mb-14">
				<h2 class="mb-3 text-2xl font-bold tracking-tight sm:text-3xl">
					Why Choose PassMyPass?
				</h2>
				<p class="mx-auto max-w-lg text-sm text-neutral-400 sm:text-base">
					Built from the ground up with true zero-knowledge architecture. The server never sees
					your data.
				</p>
			</div>

			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5 sm:p-6">
					<div
						class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10"
					>
						<ServerOff class="h-5 w-5 text-red-500" />
					</div>
					<h3 class="mb-1.5 text-sm font-semibold text-white">Zero-Knowledge Architecture</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						The encryption key never leaves your browser. Our server stores only ciphertext it
						mathematically cannot decrypt — even if compelled by law.
					</p>
				</div>

				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5 sm:p-6">
					<div
						class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10"
					>
						<Shield class="h-5 w-5 text-red-500" />
					</div>
					<h3 class="mb-1.5 text-sm font-semibold text-white">AES-256-GCM Encryption</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						Military-grade encryption performed entirely in your browser using the WebCrypto API.
						The same standard used by governments and financial institutions.
					</p>
				</div>

				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5 sm:p-6">
					<div
						class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10"
					>
						<Zap class="h-5 w-5 text-red-500" />
					</div>
					<h3 class="mb-1.5 text-sm font-semibold text-white">One-Time Viewing</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						Each link works exactly once. After the recipient views the secret, it is permanently
						and irreversibly destroyed from our servers.
					</p>
				</div>

				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5 sm:p-6">
					<div
						class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10"
					>
						<Timer class="h-5 w-5 text-red-500" />
					</div>
					<h3 class="mb-1.5 text-sm font-semibold text-white">Flexible Auto-Expiry</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						Set links to expire from 5 minutes to 24 hours. Unread secrets are automatically
						destroyed when the timer runs out.
					</p>
				</div>

				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5 sm:p-6">
					<div
						class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10"
					>
						<KeyRound class="h-5 w-5 text-red-500" />
					</div>
					<h3 class="mb-1.5 text-sm font-semibold text-white">Password Protection</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						Add an optional password for double encryption. Uses PBKDF2 with 100,000 iterations
						to derive a key that XORs with the random key.
					</p>
				</div>

				<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40 p-5 sm:p-6">
					<div
						class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10"
					>
						<MessageSquareLock class="h-5 w-5 text-red-500" />
					</div>
					<h3 class="mb-1.5 text-sm font-semibold text-white">Encrypted Chat Rooms</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						Need a real-time conversation? Create ephemeral 1-on-1 encrypted chat rooms that
						auto-destruct after 10 minutes.
					</p>
				</div>
			</div>
		</div>
	</section>

	<!-- How It Works -->
	<section class="border-t border-neutral-800/30 py-16 sm:py-20">
		<div class="container mx-auto max-w-4xl px-4">
			<h2 class="mb-10 text-center text-2xl font-bold tracking-tight sm:mb-14 sm:text-3xl">
				How It Works
			</h2>

			<div class="grid gap-6 sm:grid-cols-3 sm:gap-8">
				<div class="text-center">
					<div
						class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-lg font-bold text-red-500"
					>
						1
					</div>
					<h3 class="mb-2 text-sm font-semibold text-white">Enter Your Secret</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						Paste your password, API key, or sensitive text. Optionally add a password and set an
						expiry time.
					</p>
				</div>

				<div class="text-center">
					<div
						class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-lg font-bold text-red-500"
					>
						2
					</div>
					<h3 class="mb-2 text-sm font-semibold text-white">Share the Link</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						Your secret is encrypted in your browser. You get a unique link containing the
						encryption key — we never see it.
					</p>
				</div>

				<div class="text-center">
					<div
						class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-lg font-bold text-red-500"
					>
						3
					</div>
					<h3 class="mb-2 text-sm font-semibold text-white">Secret Self-Destructs</h3>
					<p class="text-xs leading-relaxed text-neutral-500">
						The recipient opens the link, the secret is decrypted in their browser, and it's
						permanently destroyed. Gone forever.
					</p>
				</div>
			</div>
		</div>
	</section>

	<!-- Chat CTA -->
	<section class="border-t border-neutral-800/30 py-16 sm:py-20">
		<div class="container mx-auto max-w-3xl px-4 text-center">
			<div
				class="rounded-2xl border border-neutral-800/50 bg-gradient-to-b from-neutral-900/80 to-neutral-950 p-8 sm:p-12"
			>
				<div
					class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/10"
				>
					<MessageSquareLock class="h-7 w-7 text-red-500" />
				</div>
				<h2 class="mb-3 text-xl font-bold sm:text-2xl">Need a Real-Time Conversation?</h2>
				<p class="mx-auto mb-6 max-w-md text-sm text-neutral-400 sm:text-base">
					Create an ephemeral encrypted chat room. End-to-end encrypted, no logs, auto-destroys
					in 10 minutes. Free.
				</p>
				<a
					href="/chat/"
					class="inline-flex items-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-red-500/20 transition-all hover:bg-red-500 hover:shadow-xl hover:shadow-red-500/25 active:scale-[0.98]"
				>
					Create Secret Chat Room
					<ArrowRight class="h-4 w-4" />
				</a>
			</div>
		</div>
	</section>

	<!-- FAQ Section -->
	<section class="border-t border-neutral-800/30 py-16 sm:py-20">
		<div class="container mx-auto max-w-3xl px-4">
			<h2 class="mb-10 text-center text-2xl font-bold tracking-tight sm:text-3xl">
				Frequently Asked Questions
			</h2>

			<div class="space-y-3">
				{#each faqItems as item, i}
					<div class="rounded-xl border border-neutral-800/50 bg-neutral-900/40">
						<button
							onclick={() => (openFaq = openFaq === i ? -1 : i)}
							class="flex w-full items-center justify-between p-4 text-left text-sm font-medium text-neutral-200 transition hover:text-white sm:p-5"
						>
							{item.q}
							<ChevronDown
								class="ml-4 h-4 w-4 shrink-0 text-neutral-500 transition-transform duration-200 {openFaq ===
								i
									? 'rotate-180'
									: ''}"
							/>
						</button>
						{#if openFaq === i}
							<div transition:slide={{ duration: 200 }} class="px-4 pb-4 sm:px-5 sm:pb-5">
								<p class="text-sm leading-relaxed text-neutral-400">{item.a}</p>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	</section>
</main>

<Footer />
