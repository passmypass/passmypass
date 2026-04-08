<script lang="ts">
	import { Footer } from '$lib';
</script>

<svelte:head>
	<title>Terms of Service - PassMyPass</title>
	<meta name="description" content="PassMyPass Terms of Service - Read our terms and conditions for using the secure one-time secret sharing service." />
	<link rel="canonical" href="https://passmypass.com/terms/" />

	<!-- Open Graph -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://passmypass.com/terms/" />
	<meta property="og:title" content="Terms of Service - PassMyPass" />
	<meta property="og:description" content="Read the terms and conditions for using PassMyPass secure one-time secret sharing service." />
	<meta property="og:site_name" content="PassMyPass" />

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Terms of Service - PassMyPass" />
	<meta name="twitter:description" content="Read the terms and conditions for using PassMyPass secure one-time secret sharing service." />
</svelte:head>

	<main class="flex-1">
		<div class="container mx-auto max-w-3xl px-4 py-8 sm:py-12">
			<h1 class="mb-6 text-3xl font-bold sm:text-4xl">Terms of Service</h1>
			<p class="mb-8 text-sm text-neutral-400">Last updated: April 2026</p>

			<div class="prose prose-invert prose-neutral max-w-none space-y-8 text-neutral-300">
				<section>
					<h2 class="text-xl font-semibold text-white">1. Acceptance of Terms</h2>
					<p>
						By accessing or using PassMyPass ("the Service"), you agree to be bound by these Terms of Service. If you do not agree to these terms, you may not use the Service.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">2. Service Description</h2>
					<p>
						PassMyPass provides a one-time encrypted secret sharing service and an ephemeral encrypted chat service. The Service allows users to:
					</p>
					<ul class="list-disc pl-6 space-y-2">
						<li>Share sensitive text that can only be viewed once before being permanently deleted</li>
						<li>Create ephemeral 1-on-1 encrypted chat rooms that auto-destruct after 10 minutes</li>
						<li>All data is encrypted in your browser using AES-256-GCM encryption</li>
						<li>Encryption keys never leave your device</li>
					</ul>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">3. Eligibility</h2>
					<p>
						You must be at least <strong>18 years of age</strong> to use this Service. By using the Service, you represent and warrant that you meet this age requirement and have the legal capacity to enter into these Terms.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">4. Acceptable Use</h2>
					<p>You agree to use the Service only for lawful purposes. You may NOT use the Service to:</p>
					<ul class="list-disc pl-6 space-y-2">
						<li>Share illegal content or information</li>
						<li>Distribute malware, viruses, or malicious code</li>
						<li>Share content that exploits or harms minors in any way</li>
						<li>Engage in harassment, threats, or intimidation</li>
						<li>Share content that infringes intellectual property rights</li>
						<li>Facilitate fraud, scams, or deceptive practices</li>
						<li>Share content related to terrorism or violent extremism</li>
						<li>Circumvent security measures or attempt to access systems without authorization</li>
						<li>Abuse or overload the Service infrastructure</li>
					</ul>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">5. Content Responsibility</h2>
					<p>
						<strong>You are solely responsible for the content you share through the Service.</strong> Due to our zero-knowledge encryption architecture, we cannot monitor, review, or access the plaintext content of secrets or chat messages.
					</p>
					<p class="mt-2">
						By using the Service, you acknowledge that you may receive content from others that you find offensive or objectionable. You agree that PassMyPass is not responsible for such content.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">6. No Guarantees</h2>
					<p>While we strive to provide a reliable service, we cannot guarantee:</p>
					<ul class="list-disc pl-6 space-y-2">
						<li>100% uptime or availability</li>
						<li>That secrets will remain accessible until viewed or expired</li>
						<li>Recovery of secrets if the link is lost</li>
						<li>Protection against all security threats</li>
					</ul>
					<p class="mt-2">
						<strong>Important:</strong> If you lose a secret link, it cannot be recovered. We do not have access to your encryption keys.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">7. Disclaimer of Warranties</h2>
					<p>
						THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
					</p>
					<p class="mt-2">
						WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, SECURE, OR ERROR-FREE.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">8. Limitation of Liability</h2>
					<p>
						TO THE MAXIMUM EXTENT PERMITTED BY LAW, PASSMYPASS AND ITS OPERATORS SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO:
					</p>
					<ul class="list-disc pl-6 space-y-2">
						<li>Loss of data or secrets</li>
						<li>Unauthorized access to or disclosure of your transmissions or data</li>
						<li>Business interruption</li>
						<li>Any other damages arising from the use or inability to use the Service</li>
					</ul>
					<p class="mt-2">
						Since the Service is provided free of charge, our total liability to you shall not exceed $0.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">9. Indemnification</h2>
					<p>
						You agree to indemnify, defend, and hold harmless PassMyPass and its operators from any claims, damages, losses, or expenses (including reasonable attorney fees) arising from:
					</p>
					<ul class="list-disc pl-6 space-y-2">
						<li>Your use of the Service</li>
						<li>Your violation of these Terms</li>
						<li>Content you share through the Service</li>
						<li>Your violation of any third-party rights</li>
					</ul>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">10. Service Modifications</h2>
					<p>
						We reserve the right to modify, suspend, or discontinue the Service at any time without notice. We may also modify these Terms from time to time. Continued use of the Service after changes constitutes acceptance of the new Terms.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">11. Termination</h2>
					<p>
						We may terminate or restrict your access to the Service at any time, without notice, for any reason, including but not limited to violation of these Terms or suspected abuse of the Service.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">12. Governing Law</h2>
					<p>
						These Terms shall be governed by and construed in accordance with applicable laws, without regard to conflict of law principles.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">13. Severability</h2>
					<p>
						If any provision of these Terms is found to be unenforceable, the remaining provisions will continue in full force and effect.
					</p>
				</section>

				<section>
					<h2 class="text-xl font-semibold text-white">14. Contact</h2>
					<p>
						For questions about these Terms or to report abuse, please
						<a href="/contact/" class="text-red-400 hover:text-red-300">contact us</a>.
					</p>
				</section>
			</div>
		</div>
	</main>

	<Footer />
