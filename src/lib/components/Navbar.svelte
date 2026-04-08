<script lang="ts">
	import { page } from '$app/state';
	import {
		Lock,
		Menu,
		X,
		MessageSquareLock,
		Shield,
		Info,
		ChevronRight,
		Code,
		FileText
	} from '@lucide/svelte';

	let mobileOpen = $state(false);

	// Always visible on desktop
	const primaryLinks = [
		{ href: '/chat/', label: 'Chat', icon: MessageSquareLock },
		{ href: '/security/', label: 'Security', icon: Shield },
		{ href: '/about/', label: 'About', icon: Info }
	];

	// Only visible on larger screens
	const secondaryLinks = [
		{ href: '/blog/', label: 'Blog', icon: FileText },
		{ href: '/developers/', label: 'Developers', icon: Code }
	];

	const allLinks = [...primaryLinks, ...secondaryLinks];

	function isActive(href: string) {
		return page.url.pathname === href || page.url.pathname === href.replace(/\/$/, '');
	}
</script>

<nav class="sticky top-0 z-50 border-b border-neutral-800/50 bg-neutral-950/80 backdrop-blur-lg">
	<div class="container mx-auto flex items-center justify-between px-4 py-3 sm:px-6">
		<a href="/" class="flex items-center gap-2.5 transition-opacity hover:opacity-80">
			<div
				class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-red-600 to-red-500 shadow-md shadow-red-500/20"
			>
				<Lock class="h-4 w-4 text-white" />
			</div>
			<span class="text-lg font-bold tracking-tight">PassMyPass</span>
		</a>

		<!-- Desktop links -->
		<div class="hidden items-center gap-1 sm:flex">
			{#each primaryLinks as link}
				<a
					href={link.href}
					class="rounded-lg px-3 py-2 text-sm font-medium transition-colors {isActive(link.href)
						? 'bg-neutral-800 text-white'
						: 'text-neutral-400 hover:bg-neutral-800/50 hover:text-white'}"
				>
					{link.label}
				</a>
			{/each}
			{#each secondaryLinks as link}
				<a
					href={link.href}
					class="hidden rounded-lg px-3 py-2 text-sm font-medium transition-colors lg:block {isActive(
						link.href
					)
						? 'bg-neutral-800 text-white'
						: 'text-neutral-400 hover:bg-neutral-800/50 hover:text-white'}"
				>
					{link.label}
				</a>
			{/each}
			<a
				href="/"
				class="ml-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-red-500/20 transition-all hover:bg-red-500 hover:shadow-md hover:shadow-red-500/25 active:scale-[0.97]"
			>
				Share a Secret
			</a>
		</div>

		<!-- Mobile hamburger -->
		<button
			onclick={() => (mobileOpen = !mobileOpen)}
			class="rounded-lg p-2 text-neutral-400 transition hover:bg-neutral-800 hover:text-white sm:hidden"
			aria-label="Toggle menu"
		>
			{#if mobileOpen}
				<X class="h-5 w-5" />
			{:else}
				<Menu class="h-5 w-5" />
			{/if}
		</button>
	</div>

	<!-- Mobile menu -->
	{#if mobileOpen}
		<div class="border-t border-neutral-800/50 bg-neutral-950/95 backdrop-blur-lg sm:hidden">
			<div class="space-y-1 px-4 py-3">
				{#each allLinks as link}
					<a
						href={link.href}
						onclick={() => (mobileOpen = false)}
						class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors {isActive(
							link.href
						)
							? 'bg-neutral-800 text-white'
							: 'text-neutral-400 hover:bg-neutral-800/50 hover:text-white'}"
					>
						<link.icon class="h-4 w-4" />
						{link.label}
						<ChevronRight class="ml-auto h-4 w-4 opacity-40" />
					</a>
				{/each}
				<a
					href="/"
					onclick={() => (mobileOpen = false)}
					class="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-500"
				>
					<Lock class="h-4 w-4" />
					Share a Secret
				</a>
			</div>
		</div>
	{/if}
</nav>
