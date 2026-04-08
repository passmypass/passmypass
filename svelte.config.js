import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		paths: {
			relative: false
		},
		adapter: adapter({
			fallback: '200.html' // SPA fallback for non-prerendered routes (s/[id], c/[id])
		})
	}
};

export default config;
