<script lang="ts">
	import { Footer } from '$lib';
	import { Send, Check, CircleX, Loader2, Mail } from '@lucide/svelte';

	type State = 'idle' | 'sending' | 'success' | 'error';

	let formState: State = $state('idle');
	let name = $state('');
	let email = $state('');
	let subject = $state('general');
	let message = $state('');
	let errorMessage = $state('');

	const subjectOptions = [
		{ value: 'general', label: 'General Inquiry' },
		{ value: 'security', label: 'Security Vulnerability Report' },
		{ value: 'abuse', label: 'Report Abuse' },
		{ value: 'feedback', label: 'Feedback' },
		{ value: 'other', label: 'Other' }
	];

	async function handleSubmit() {
		if (!email.trim() || !message.trim()) {
			errorMessage = 'Please fill in your email and message.';
			formState = 'error';
			return;
		}

		formState = 'sending';
		errorMessage = '';

		try {
			const response = await fetch('https://formspree.io/f/mjgpzokq', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					name: name.trim(),
					email: email.trim(),
					subject: subjectOptions.find((o) => o.value === subject)?.label || subject,
					message: message.trim()
				})
			});

			if (response.ok) {
				formState = 'success';
				name = '';
				email = '';
				subject = 'general';
				message = '';
			} else {
				errorMessage = 'Failed to send message. Please try again.';
				formState = 'error';
			}
		} catch {
			errorMessage = 'Network error. Please try again.';
			formState = 'error';
		}
	}

	function reset() {
		formState = 'idle';
		errorMessage = '';
	}
</script>

<svelte:head>
	<title>Contact Us - PassMyPass</title>
	<meta
		name="description"
		content="Get in touch with the PassMyPass team. Report security vulnerabilities, send feedback, or ask questions about our zero-knowledge encrypted secret sharing service."
	/>
	<link rel="canonical" href="https://passmypass.com/contact/" />

	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/contact/" />
	<meta property="og:title" content="Contact Us - PassMyPass" />
	<meta
		property="og:description"
		content="Get in touch with the PassMyPass team. Report vulnerabilities, send feedback, or ask questions."
	/>
	<meta property="og:site_name" content="PassMyPass" />
	<meta property="og:image" content="https://passmypass.com/og-image.png" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="Contact Us - PassMyPass" />
	<meta
		name="twitter:description"
		content="Get in touch with the PassMyPass team."
	/>
	<meta name="twitter:image" content="https://passmypass.com/og-image.png" />
</svelte:head>

<main class="flex-1">
	<section class="relative overflow-hidden">
		<div
			class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-950/20 via-transparent to-transparent"
		></div>
		<div class="container mx-auto max-w-xl px-4 py-12 sm:py-20">
			<div class="mb-8 text-center sm:mb-10">
				<div
					class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/10"
				>
					<Mail class="h-7 w-7 text-red-500" />
				</div>
				<h1 class="mb-3 text-3xl font-extrabold tracking-tight sm:text-4xl">Contact Us</h1>
				<p class="text-sm text-neutral-400 sm:text-base">
					Have a question, feedback, or want to report a security issue? We'd love to hear from
					you.
				</p>
			</div>

			{#if formState === 'success'}
				<div
					class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8"
				>
					<div
						class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10"
					>
						<Check class="h-7 w-7 text-emerald-500" />
					</div>
					<h2 class="mb-2 text-xl font-bold text-white">Message Sent</h2>
					<p class="mb-6 text-sm text-neutral-400">
						Thank you for reaching out. We'll get back to you as soon as possible.
					</p>
					<button
						onclick={reset}
						class="rounded-xl border border-neutral-700 bg-neutral-800/30 px-6 py-2.5 text-sm font-medium text-neutral-300 transition hover:bg-neutral-800 hover:text-white"
					>
						Send Another Message
					</button>
				</div>
			{:else}
				<div
					class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-4 shadow-xl backdrop-blur-sm sm:p-6"
				>
					<form
						onsubmit={(e) => {
							e.preventDefault();
							handleSubmit();
						}}
					>
						<div class="mb-4">
							<label for="name" class="mb-2 block text-sm font-medium text-neutral-200">
								Name <span class="text-neutral-600">(optional)</span>
							</label>
							<input
								type="text"
								id="name"
								bind:value={name}
								placeholder="Your name"
								disabled={formState === 'sending'}
								class="min-h-[44px] w-full rounded-xl border border-neutral-700 bg-neutral-950 p-3 text-sm text-white placeholder-neutral-600 transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 disabled:opacity-50"
							/>
						</div>

						<div class="mb-4">
							<label for="email" class="mb-2 block text-sm font-medium text-neutral-200">
								Email
							</label>
							<input
								type="email"
								id="email"
								bind:value={email}
								placeholder="you@example.com"
								required
								disabled={formState === 'sending'}
								class="min-h-[44px] w-full rounded-xl border border-neutral-700 bg-neutral-950 p-3 text-sm text-white placeholder-neutral-600 transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 disabled:opacity-50"
							/>
						</div>

						<div class="mb-4">
							<label for="subject" class="mb-2 block text-sm font-medium text-neutral-200">
								Subject
							</label>
							<select
								id="subject"
								bind:value={subject}
								disabled={formState === 'sending'}
								class="min-h-[44px] w-full cursor-pointer rounded-xl border border-neutral-700 bg-neutral-950 p-3 text-sm text-white transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 disabled:opacity-50"
							>
								{#each subjectOptions as option}
									<option value={option.value}>{option.label}</option>
								{/each}
							</select>
						</div>

						<div class="mb-4">
							<label for="message" class="mb-2 block text-sm font-medium text-neutral-200">
								Message
							</label>
							<textarea
								id="message"
								bind:value={message}
								placeholder="How can we help?"
								rows="5"
								required
								disabled={formState === 'sending'}
								class="w-full resize-none rounded-xl border border-neutral-700 bg-neutral-950 p-3 text-sm leading-relaxed text-white placeholder-neutral-600 transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 disabled:opacity-50"
							></textarea>
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
							disabled={formState === 'sending' || !email.trim() || !message.trim()}
							class="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-xl bg-red-600 py-3.5 font-semibold text-white shadow-lg shadow-red-500/20 transition-all hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
						>
							{#if formState === 'sending'}
								<Loader2 class="h-5 w-5 animate-spin" />
								Sending...
							{:else}
								<Send class="h-5 w-5" />
								Send Message
							{/if}
						</button>
					</form>
				</div>
			{/if}
		</div>
	</section>
</main>

<Footer />
