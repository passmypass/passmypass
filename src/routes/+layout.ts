// Prerender all pages at build time (dynamic routes opt out individually)
export const prerender = true;

// SSR enabled (default) so prerendered pages include full HTML content for SEO
// Dynamic routes (s/[id], c/[id]) opt out of SSR in their own +page.ts

// Use trailing slashes for consistent URL handling (fixes Google "Page with redirect" indexing issues)
export const trailingSlash = 'always';
