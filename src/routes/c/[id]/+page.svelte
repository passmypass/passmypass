<script lang="ts">
	import { onMount, onDestroy, tick } from 'svelte';
	import { browser } from '$app/environment';
	import { decodeBase64Url, encryptMessage, decryptMessage, getChatWsUrl, Footer } from '$lib';
	import { Lock, Send, Loader2, CircleAlert, Clock, MessageSquareLock, Users } from '@lucide/svelte';

	type ChatState = 'connecting' | 'waiting_for_peer' | 'active' | 'ended' | 'error' | 'expired';

	interface Message {
		id: number;
		text: string;
		own: boolean;
		timestamp: Date;
	}

	const { data } = $props<{ data: { roomId: string } }>();

	let chatState: ChatState = $state('connecting');
	let messages: Message[] = $state([]);
	let inputText = $state('');
	let errorMessage = $state('');
	let peerTyping = $state(false);
	let messageIdCounter = 0;

	let encryptionKey: Uint8Array | null = null;
	let ws: WebSocket | null = null;
	let typingTimeout: ReturnType<typeof setTimeout> | null = null;
	let peerTypingTimeout: ReturnType<typeof setTimeout> | null = null;
	let messagesContainer: HTMLDivElement | undefined = $state(undefined);
	let textareaEl: HTMLTextAreaElement | undefined = $state(undefined);

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	onMount(async () => {
		if (!browser) return;

		const fragment = window.location.hash.slice(1);

		// Strip fragment from URL for security
		if (fragment) {
			window.history.replaceState(null, '', window.location.pathname);
		}

		if (!fragment) {
			errorMessage = 'Invalid link - missing encryption key';
			chatState = 'error';
			return;
		}

		try {
			encryptionKey = decodeBase64Url(fragment);
			if (encryptionKey.length !== 32) {
				throw new Error('Invalid key length');
			}
		} catch {
			errorMessage = 'Invalid link - corrupted encryption key';
			chatState = 'error';
			return;
		}

		connectWebSocket();
	});

	function connectWebSocket() {
		const wsUrl = getChatWsUrl(data.roomId);
		ws = new WebSocket(wsUrl);

		ws.onopen = () => {
			chatState = 'waiting_for_peer';
		};

		ws.onmessage = async (event) => {
			try {
				const msg = JSON.parse(event.data);

				if (msg.type === 'system') {
					handleSystemMessage(msg.event);
				} else if (msg.type === 'message' && encryptionKey) {
					const plaintext = await decryptMessage(msg.data, msg.nonce, encryptionKey);
					messages.push({
						id: ++messageIdCounter,
						text: plaintext,
						own: false,
						timestamp: new Date()
					});
					peerTyping = false;
					await tick();
					scrollToBottom();
				} else if (msg.type === 'typing') {
					peerTyping = true;
					if (peerTypingTimeout) clearTimeout(peerTypingTimeout);
					peerTypingTimeout = setTimeout(() => {
						peerTyping = false;
					}, 3000);
				}
			} catch (err) {
				console.error('Failed to process message:', err);
			}
		};

		ws.onclose = (event) => {
			if (event.code === 4001) {
				chatState = 'ended';
			} else if (event.code === 4003) {
				errorMessage = 'Room is full - someone else already joined';
				chatState = 'error';
			} else if (event.code === 4004) {
				errorMessage = 'Room not found - it may have expired or been deleted';
				chatState = 'error';
			} else if (event.code === 4008) {
				chatState = 'expired';
			} else if (chatState === 'active' || chatState === 'waiting_for_peer') {
				chatState = 'ended';
			}
		};

		ws.onerror = () => {
			if (chatState === 'connecting') {
				errorMessage = 'Failed to connect to chat server';
				chatState = 'error';
			}
		};
	}

	function handleSystemMessage(event: string) {
		if (event === 'peer_joined') {
			chatState = 'active';
		} else if (event === 'peer_left') {
			chatState = 'ended';
		} else if (event === 'room_expired') {
			chatState = 'expired';
		}
	}

	async function sendMessage() {
		if (!inputText.trim() || !ws || !encryptionKey || chatState !== 'active') return;

		const text = inputText.trim();
		inputText = '';
		// Reset textarea height
		if (textareaEl) {
			textareaEl.style.height = 'auto';
		}

		try {
			const encrypted = await encryptMessage(text, encryptionKey);
			ws.send(JSON.stringify({
				type: 'message',
				data: encrypted.ciphertext,
				nonce: encrypted.nonce
			}));

			messages.push({
				id: ++messageIdCounter,
				text,
				own: true,
				timestamp: new Date()
			});
			await tick();
			scrollToBottom();
		} catch (err) {
			console.error('Failed to send message:', err);
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function resizeTextarea() {
		if (textareaEl) {
			textareaEl.style.height = 'auto';
			textareaEl.style.height = Math.min(textareaEl.scrollHeight, 120) + 'px';
		}
	}

	function handleInput() {
		if (!ws || chatState !== 'active') return;

		// Send typing indicator (throttled)
		if (!typingTimeout) {
			try {
				ws.send(JSON.stringify({ type: 'typing' }));
			} catch {
				// Ignore send errors
			}
			typingTimeout = setTimeout(() => {
				typingTimeout = null;
			}, 2000);
		}
	}

	function handleBeforeUnload(event: BeforeUnloadEvent) {
		if (chatState === 'active') {
			event.preventDefault();
		}
	}

	onDestroy(() => {
		if (ws) {
			ws.close();
			ws = null;
		}
		if (typingTimeout) clearTimeout(typingTimeout);
		if (peerTypingTimeout) clearTimeout(peerTypingTimeout);
	});

	function formatTime(date: Date): string {
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}
</script>

<svelte:window onbeforeunload={handleBeforeUnload} />

<svelte:head>
	<title>Chat Room - PassMyPass</title>
	<meta name="robots" content="noindex, nofollow" />
</svelte:head>

	<main class="flex h-dvh flex-col overflow-hidden">
		<div class="container mx-auto flex min-h-0 max-w-xl flex-1 flex-col px-4 pb-4 pt-4 sm:pb-6 sm:pt-6">
			<!-- Compact header -->
			<header class="mb-4 flex shrink-0 items-center justify-between">
				<a href="/" class="flex items-center gap-2">
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-neutral-800 shadow sm:h-9 sm:w-9">
						<Lock class="h-4 w-4 text-red-500" />
					</div>
					<span class="text-lg font-bold tracking-tight sm:text-xl">PassMyPass</span>
				</a>
				<div class="flex items-center gap-1.5 text-xs text-neutral-500">
					{#if chatState === 'active'}
						<span class="h-2 w-2 rounded-full bg-emerald-500"></span>
						<span>Connected</span>
					{:else if chatState === 'waiting_for_peer'}
						<span class="h-2 w-2 animate-pulse rounded-full bg-amber-500"></span>
						<span>Waiting...</span>
					{:else if chatState === 'connecting'}
						<Loader2 class="h-3 w-3 animate-spin" />
						<span>Connecting</span>
					{/if}
				</div>
			</header>

			{#if chatState === 'connecting'}
				<div class="flex flex-1 items-center justify-center">
					<div class="text-center">
						<Loader2 class="mx-auto mb-3 h-10 w-10 animate-spin text-red-500" />
						<p class="text-sm text-neutral-400">Connecting to chat room...</p>
					</div>
				</div>

			{:else if chatState === 'waiting_for_peer'}
				<div class="flex flex-1 items-center justify-center">
					<div class="text-center">
						<div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-neutral-800">
							<Users class="h-7 w-7 text-red-500" />
						</div>
						<h2 class="text-lg font-bold text-white sm:text-xl">Waiting for peer</h2>
						<p class="mt-1.5 text-sm text-neutral-400">Share the room link with your chat partner</p>
						<div class="mt-4 inline-flex items-center gap-1.5 rounded-full bg-neutral-800/50 px-3 py-1.5 text-xs text-neutral-400">
							<Clock class="h-3 w-3" />
							Room expires in 10 minutes
						</div>
					</div>
				</div>

			{:else if chatState === 'active'}
				<!-- Messages area -->
				<div
					bind:this={messagesContainer}
					class="min-h-0 flex-1 space-y-3 overflow-y-auto rounded-2xl border border-neutral-800 bg-neutral-900/50 p-3 sm:p-4"
				>
					{#if messages.length === 0}
						<div class="flex h-full items-center justify-center">
							<p class="text-sm text-neutral-600">Send a message to start the conversation</p>
						</div>
					{/if}

					{#each messages as msg (msg.id)}
						<div class="flex {msg.own ? 'justify-end' : 'justify-start'}">
							<div class="max-w-[80%] rounded-2xl px-3.5 py-2 sm:px-4 sm:py-2.5 {msg.own ? 'bg-red-600/20 text-white' : 'bg-neutral-800 text-neutral-200'}">
								<p class="whitespace-pre-wrap break-words text-sm">{msg.text}</p>
								<p class="mt-1 text-right text-[10px] {msg.own ? 'text-red-400/50' : 'text-neutral-500'}">{formatTime(msg.timestamp)}</p>
							</div>
						</div>
					{/each}

					{#if peerTyping}
						<div class="flex justify-start">
							<div class="rounded-2xl bg-neutral-800 px-4 py-2.5">
								<div class="flex gap-1">
									<span class="h-2 w-2 animate-bounce rounded-full bg-neutral-500" style="animation-delay: 0ms"></span>
									<span class="h-2 w-2 animate-bounce rounded-full bg-neutral-500" style="animation-delay: 150ms"></span>
									<span class="h-2 w-2 animate-bounce rounded-full bg-neutral-500" style="animation-delay: 300ms"></span>
								</div>
							</div>
						</div>
					{/if}
				</div>

				<!-- Input area -->
				<div class="mt-3 flex shrink-0 items-end gap-2 sm:mt-4">
					<textarea
						bind:this={textareaEl}
						bind:value={inputText}
						onkeydown={handleKeydown}
						oninput={() => { handleInput(); resizeTextarea(); }}
						placeholder="Type a message..."
						rows={1}
						class="min-h-[44px] max-h-[120px] flex-1 resize-none rounded-xl border border-neutral-700 bg-neutral-950 px-4 py-2.5 text-sm text-white placeholder-neutral-500 transition-all focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20"
					></textarea>
					<button
						onclick={sendMessage}
						disabled={!inputText.trim()}
						class="flex h-[44px] w-[44px] shrink-0 items-center justify-center rounded-xl bg-red-600 text-white transition hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-neutral-900 active:scale-95 disabled:opacity-40"
					>
						<Send class="h-5 w-5" />
					</button>
				</div>

			{:else if chatState === 'ended'}
				<div class="flex flex-1 items-center justify-center">
					<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl sm:p-8">
						<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-neutral-700/50 sm:mb-4 sm:h-16 sm:w-16">
							<MessageSquareLock class="h-7 w-7 text-neutral-400 sm:h-8 sm:w-8" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Chat Ended</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2">Your peer has disconnected. The room has been destroyed.</p>
						<a
							href="/chat/"
							class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
						>
							Create New Room
						</a>
					</div>
				</div>

			{:else if chatState === 'expired'}
				<div class="flex flex-1 items-center justify-center">
					<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl sm:p-8">
						<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/20 sm:mb-4 sm:h-16 sm:w-16">
							<Clock class="h-7 w-7 text-amber-400 sm:h-8 sm:w-8" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Room Expired</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2">This chat room has expired after 10 minutes.</p>
						<a
							href="/chat/"
							class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
						>
							Create New Room
						</a>
					</div>
				</div>

			{:else if chatState === 'error'}
				<div class="flex flex-1 items-center justify-center">
					<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl sm:p-8">
						<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-red-500/20 sm:mb-4 sm:h-16 sm:w-16">
							<CircleAlert class="h-7 w-7 text-red-400 sm:h-8 sm:w-8" />
						</div>
						<h2 class="text-xl font-bold text-white sm:text-2xl">Error</h2>
						<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2">{errorMessage}</p>
						<a
							href="/chat/"
							class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
						>
							Create New Room
						</a>
					</div>
				</div>
			{/if}
		</div>
	</main>

	{#if chatState !== 'active'}
		<Footer />
	{/if}
