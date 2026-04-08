<script lang="ts">
	import './layout.css';
	import { Navbar } from '$lib';
	import { page } from '$app/state';

	let { children } = $props();

	// Hide navbar on chat room pages (they have their own compact header)
	const hideNavbar = $derived(page.url.pathname.startsWith('/c/'));
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
</svelte:head>

<div class="flex min-h-screen flex-col bg-neutral-950 text-white">
	{#if !hideNavbar}
		<Navbar />
	{/if}
	{@render children()}
</div>
