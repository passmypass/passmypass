// Crypto utilities
export {
	encodeBase64Url,
	decodeBase64Url,
	generateEncryptionKey,
	generateNonce,
	generateChatKey,
	encryptSecret,
	decryptSecret,
	encryptMessage,
	decryptMessage,
	isPasswordProtected,
	secureWipe,
	encrypt,
	decrypt,
	type EncryptionResult
} from './crypto';

// API client
export {
	createSecret,
	getSecretStatus,
	claimSecret,
	getChatWsUrl,
	createChatRoom,
	ApiError,
	type CreateSecretRequest,
	type CreateSecretResponse,
	type SecretStatusResponse,
	type ClaimSecretRequest,
	type ClaimSecretResponse
} from './api';

// Components
export { default as Footer } from './components/Footer.svelte';
export { default as Navbar } from './components/Navbar.svelte';
