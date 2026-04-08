<script lang="ts">
	import { Footer } from '$lib';
</script>

<svelte:head>
	<title>Privacy Policy - PassMyPass</title>
	<meta name="description" content="PassMyPass Privacy Policy - Learn how we protect your data with end-to-end encryption and zero-knowledge architecture." />
	<link rel="canonical" href="https://passmypass.com/privacy/" />

	<!-- Open Graph -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/privacy/" />
	<meta property="og:title" content="Privacy Policy - PassMyPass" />
	<meta property="og:description" content="Learn how PassMyPass protects your data with end-to-end encryption and zero-knowledge architecture." />
	<meta property="og:site_name" content="PassMyPass" />

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Privacy Policy - PassMyPass" />
	<meta name="twitter:description" content="Learn how PassMyPass protects your data with end-to-end encryption and zero-knowledge architecture." />
</svelte:head>

	<main class="flex-1">
		<div class="container mx-auto max-w-3xl px-4 py-8 sm:py-12">
			<h1 class="mb-6 text-3xl font-bold sm:text-4xl">Privacy Policy</h1>
			<p class="mb-8 text-sm text-neutral-400">Last updated: April 2026</p>

			<div class="prose prose-invert prose-neutral max-w-none space-y-8 text-neutral-300">
				<section>
					<h2 class="text-xl font-semibold text-white">1. Introduction</h2>
					<p>
						PassMyPass ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and safeguard information when you use our one-time secret sharing and ephemeral chat services.
					</p>
					<p>
						Our service is built on a <strong>zero-knowledge architecture</strong> - this means we cannot access, read, or decrypt your secrets or chat messages. All encryption happens in your browser before any data is sent to our servers.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">2. Information We Collect</h2>

					<h3 class="text-lg font-medium text-neutral-200">What We Store</h3>
					<ul class="list-disc pl-6 space-y-2">
						<li><strong>Encrypted data only:</strong> We store only the encrypted ciphertext of your secrets. We never have access to the plaintext content or the encryption keys.</li>
						<li><strong>Cryptographic metadata:</strong> Nonces and additional authenticated data (AAD) required for decryption.</li>
						<li><strong>Hashed identifiers:</strong> SHA-256 hashes of claim tokens and IP addresses for security auditing.</li>
						<li><strong>Timestamps:</strong> Creation, expiration, and consumption times for secret lifecycle management.</li>
						<li><strong>Aggregate statistics:</strong> Daily totals of secrets created, claimed, and expired, as well as chat rooms created and messages relayed - used to monitor service health. These are aggregate counts only, with no link to individual users, secret content, or chat messages.</li>
					</ul>

					<h3 class="text-lg font-medium text-neutral-200 mt-4">Chat Room Data</h3>
					<ul class="list-disc pl-6 space-y-2">
						<li><strong>Ephemeral only:</strong> Chat room data exists only in server memory and is never written to disk or any database.</li>
						<li><strong>Encrypted relay:</strong> Chat messages are end-to-end encrypted; the server only relays ciphertext it cannot decrypt.</li>
						<li><strong>Automatic destruction:</strong> Rooms are destroyed when either participant disconnects or after 10 minutes, whichever comes first.</li>
					</ul>

					<h3 class="text-lg font-medium text-neutral-200 mt-4">What We Do NOT Collect</h3>
					<ul class="list-disc pl-6 space-y-2">
						<li>Your plaintext secrets or chat messages</li>
						<li>Encryption keys (they never leave your browser)</li>
						<li>User accounts or personal information</li>
						<li>Cookies or tracking data</li>
						<li>Raw IP addresses in our application database (we only store one-way hashes)</li>
					</ul>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">3. How We Use Information</h2>
					<p>The limited information we collect is used solely to:</p>
					<ul class="list-disc pl-6 space-y-2">
						<li>Provide the secret sharing and chat services</li>
						<li>Automatically delete secrets after they are viewed or expire</li>
						<li>Prevent abuse and rate-limit excessive requests</li>
						<li>Maintain security audit logs</li>
						<li>Comply with legal requirements</li>
					</ul>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">4. Data Retention</h2>
					<ul class="list-disc pl-6 space-y-2">
						<li><strong>Secrets:</strong> Automatically deleted immediately after being viewed, or when they expire (maximum 24 hours), whichever comes first.</li>
						<li><strong>Chat rooms:</strong> Destroyed instantly when either participant disconnects or after 10 minutes. No chat data is ever persisted.</li>
						<li><strong>Audit logs:</strong> Retained for a limited period for security purposes, then automatically purged.</li>
						<li><strong>No backups of secrets:</strong> We do not create persistent backups of encrypted secrets.</li>
					</ul>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">5. Data Security</h2>
					<p>We employ industry-standard security measures:</p>
					<ul class="list-disc pl-6 space-y-2">
						<li><strong>AES-256-GCM encryption:</strong> Industry-standard encryption performed entirely in your browser</li>
						<li><strong>Zero-knowledge architecture:</strong> We cannot decrypt your data even if compelled</li>
						<li><strong>HTTPS only:</strong> All data transmitted over encrypted connections</li>
						<li><strong>Security headers:</strong> HSTS, CSP, and other protective headers</li>
						<li><strong>IP address hashing:</strong> Our application only stores one-way SHA-256 hashes of IP addresses</li>
					</ul>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">6. Data Sharing</h2>
					<p>We do not sell, trade, or share your data with third parties except:</p>
					<ul class="list-disc pl-6 space-y-2">
						<li>When required by law or valid legal process</li>
						<li>To protect our rights or prevent abuse</li>
					</ul>
					<p class="mt-2">
						Note: Due to our zero-knowledge architecture, we cannot provide plaintext content even if legally compelled - we simply do not have access to it.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">7. Your Rights</h2>
					<p>Depending on your jurisdiction, you may have rights including:</p>
					<ul class="list-disc pl-6 space-y-2">
						<li><strong>Right to access:</strong> Request information about data we hold</li>
						<li><strong>Right to erasure:</strong> Secrets are automatically deleted; no action needed</li>
						<li><strong>Right to portability:</strong> Not applicable as we don't maintain user accounts</li>
					</ul>
					<p class="mt-2">
						Since we don't collect personal information or require accounts, most data protection rights are automatically satisfied by our architecture.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">8. Cookies</h2>
					<p>
						<strong>We do not use cookies.</strong> PassMyPass operates without cookies, tracking pixels, analytics, or any form of persistent browser storage.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">9. Infrastructure & Hosting</h2>
					<p>
						PassMyPass is hosted on third-party cloud infrastructure. While our application only stores one-way hashes of IP addresses, our <strong>hosting provider may independently log raw IP addresses, request metadata, and other standard server access information</strong> as part of their own infrastructure operations. This is standard practice for cloud hosting and is outside our direct control.
					</p>
					<p class="mt-2">
						We select hosting providers that maintain reasonable security and privacy practices. However, we encourage users who require complete IP anonymity to access the service through a VPN or Tor.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">10. International Data Transfers</h2>
					<p>
						Our servers may be located in various jurisdictions. By using our service, you consent to the transfer of encrypted data to these servers. Remember: we only store encrypted data that we cannot decrypt.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">11. Children's Privacy</h2>
					<p>
						PassMyPass is not intended for use by individuals under the age of 18. We do not knowingly collect information from children.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">12. Changes to This Policy</h2>
					<p>
						We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated revision date.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">13. Contact Us</h2>
					<p>
						For privacy-related questions or concerns, please
						<a href="/contact/" class="text-red-400 hover:text-red-300">contact us</a>.
					</p>
				</section>
			</div>
		</div>
	</main>

	<Footer />
