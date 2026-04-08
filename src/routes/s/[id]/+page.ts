// Disable prerendering and SSR for dynamic secret routes (noindex, client-only)
export const prerender = false;
export const ssr = false;

export function load({ params }: { params: { id: string } }) {
	return {
		secretId: params.id
	};
}
