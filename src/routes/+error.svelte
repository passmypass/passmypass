<script lang="ts">
	import { page } from '$app/state';
	import { Footer } from '$lib';
	import { Frown, ChevronLeft } from '@lucide/svelte';
</script>

<svelte:head>
	<title>{page.status === 404 ? 'Page Not Found' : 'Error'} - PassMyPass</title>
	<meta name="robots" content="noindex, nofollow" />
</svelte:head>

<main class="flex-1">
	<div class="container mx-auto max-w-xl px-4 py-6 sm:py-10">

		<div class="rounded-2xl border border-neutral-800 bg-neutral-900/80 p-6 text-center shadow-xl backdrop-blur-sm sm:p-8">
			<div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-neutral-700/50 sm:mb-4 sm:h-16 sm:w-16">
				<Frown class="h-7 w-7 text-neutral-400 sm:h-8 sm:w-8" />
			</div>
			<h2 class="text-xl font-bold text-white sm:text-2xl">
				{#if page.status === 404}
					Page Not Found
				{:else}
					Something Went Wrong
				{/if}
			</h2>
			<p class="mt-1.5 text-sm text-neutral-400 sm:mt-2 sm:text-base">
				{#if page.status === 404}
					The page you're looking for doesn't exist or has been removed.
				{:else}
					An unexpected error occurred. Please try again.
				{/if}
			</p>
			<a
				href="/"
				class="mt-5 inline-flex min-h-[48px] items-center justify-center gap-2 rounded-xl bg-red-600 px-6 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-red-500 sm:mt-6 sm:text-base"
			>
				<ChevronLeft class="h-4 w-4" />
				Back to Home
			</a>
		</div>
	</div>
</main>

<Footer />
