/**
 * Client-side cryptography utilities using WebCrypto API.
 * All encryption/decryption happens in the browser - the server never sees plaintext.
 */

// PBKDF2 iterations for password-based key derivation
const PBKDF2_ITERATIONS = 100000;
const PBKDF2_SALT_LENGTH = 16;

/**
 * Encode bytes to base64url string (no padding).
 */
export function encodeBase64Url(bytes: Uint8Array): string {
	const base64 = btoa(String.fromCharCode(...bytes));
	return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/**
 * Decode base64url string to bytes.
 */
export function decodeBase64Url(str: string): Uint8Array {
	// Add padding if needed
	let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
	const padding = 4 - (base64.length % 4);
	if (padding !== 4) {
		base64 += '='.repeat(padding);
	}
	const binary = atob(base64);
	const bytes = new Uint8Array(binary.length);
	for (let i = 0; i < binary.length; i++) {
		bytes[i] = binary.charCodeAt(i);
	}
	return bytes;
}

/**
 * Generate cryptographically secure random bytes.
 */
export function generateRandomBytes(length: number): Uint8Array {
	return crypto.getRandomValues(new Uint8Array(length));
}

/**
 * Generate a 256-bit AES key (32 bytes).
 */
export function generateEncryptionKey(): Uint8Array {
	return generateRandomBytes(32);
}

/**
 * Generate a 12-byte nonce for AES-GCM.
 */
export function generateNonce(): Uint8Array {
	return generateRandomBytes(12);
}

/**
 * Generate a 32-byte claim token.
 */
export function generateClaimToken(): Uint8Array {
	return generateRandomBytes(32);
}

/**
 * Compute SHA-256 hash of data.
 */
export async function sha256(data: Uint8Array): Promise<Uint8Array> {
	const hashBuffer = await crypto.subtle.digest('SHA-256', data as unknown as BufferSource);
	return new Uint8Array(hashBuffer);
}

/**
 * Import a raw key for AES-GCM operations.
 */
async function importKey(keyBytes: Uint8Array): Promise<CryptoKey> {
	return crypto.subtle.importKey(
		'raw',
		keyBytes as unknown as BufferSource,
		{ name: 'AES-GCM' },
		false,
		['encrypt', 'decrypt']
	);
}

/**
 * Generate a salt for PBKDF2.
 */
export function generateSalt(): Uint8Array {
	return generateRandomBytes(PBKDF2_SALT_LENGTH);
}

/**
 * Derive a 256-bit key from a password using PBKDF2.
 */
export async function deriveKeyFromPassword(
	password: string,
	salt: Uint8Array
): Promise<Uint8Array> {
	const encoder = new TextEncoder();
	const passwordBytes = encoder.encode(password);

	const baseKey = await crypto.subtle.importKey(
		'raw',
		passwordBytes,
		'PBKDF2',
		false,
		['deriveBits']
	);

	const derivedBits = await crypto.subtle.deriveBits(
		{
			name: 'PBKDF2',
			salt: salt as unknown as BufferSource,
			iterations: PBKDF2_ITERATIONS,
			hash: 'SHA-256'
		},
		baseKey,
		256
	);

	return new Uint8Array(derivedBits);
}

/**
 * XOR two byte arrays of equal length.
 */
export function xorBytes(a: Uint8Array, b: Uint8Array): Uint8Array {
	if (a.length !== b.length) {
		throw new Error('Arrays must be the same length');
	}
	const result = new Uint8Array(a.length);
	for (let i = 0; i < a.length; i++) {
		result[i] = a[i] ^ b[i];
	}
	return result;
}

/**
 * AAD Flags
 */
export const AAD_FLAG_PASSWORD_PROTECTED = 0x01;

/**
 * Create Additional Authenticated Data (AAD) for versioned metadata.
 * @param passwordSalt - If provided, indicates password protection and includes the salt
 */
export function createAAD(passwordSalt?: Uint8Array): Uint8Array {
	if (passwordSalt && passwordSalt.length === PBKDF2_SALT_LENGTH) {
		// Version 1, password protected: [version, flags, salt...]
		const aad = new Uint8Array(2 + PBKDF2_SALT_LENGTH);
		aad[0] = 0x01; // version
		aad[1] = AAD_FLAG_PASSWORD_PROTECTED;
		aad.set(passwordSalt, 2);
		return aad;
	}
	// Version 1, no password: [version, flags]
	return new Uint8Array([0x01, 0x00]);
}

/**
 * Parse AAD to extract metadata.
 */
export function parseAAD(aad: Uint8Array): { version: number; passwordProtected: boolean; salt?: Uint8Array } {
	if (aad.length === 1) {
		// Legacy format: just version byte
		return { version: aad[0], passwordProtected: false };
	}
	const version = aad[0];
	const flags = aad[1];
	const passwordProtected = (flags & AAD_FLAG_PASSWORD_PROTECTED) !== 0;

	if (passwordProtected && aad.length >= 2 + PBKDF2_SALT_LENGTH) {
		const salt = aad.slice(2, 2 + PBKDF2_SALT_LENGTH);
		return { version, passwordProtected, salt };
	}

	return { version, passwordProtected };
}

/**
 * Encrypt plaintext using AES-256-GCM.
 * Returns the ciphertext (which includes the auth tag).
 */
export async function encrypt(
	plaintext: string,
	keyBytes: Uint8Array,
	nonce: Uint8Array,
	aad?: Uint8Array
): Promise<Uint8Array> {
	const key = await importKey(keyBytes);
	const encoder = new TextEncoder();
	const plaintextBytes = encoder.encode(plaintext);

	const params: AesGcmParams = {
		name: 'AES-GCM',
		iv: nonce as unknown as BufferSource
	};
	if (aad) {
		params.additionalData = aad as unknown as BufferSource;
	}

	const ciphertext = await crypto.subtle.encrypt(params, key, plaintextBytes);

	return new Uint8Array(ciphertext);
}

/**
 * Decrypt ciphertext using AES-256-GCM.
 * The ciphertext should include the auth tag (as produced by encrypt).
 */
export async function decrypt(
	ciphertext: Uint8Array,
	keyBytes: Uint8Array,
	nonce: Uint8Array,
	aad?: Uint8Array
): Promise<string> {
	const key = await importKey(keyBytes);

	const params: AesGcmParams = {
		name: 'AES-GCM',
		iv: nonce as unknown as BufferSource
	};
	if (aad) {
		params.additionalData = aad as unknown as BufferSource;
	}

	const plaintextBuffer = await crypto.subtle.decrypt(params, key, ciphertext as unknown as BufferSource);

	const decoder = new TextDecoder();
	return decoder.decode(plaintextBuffer);
}

/**
 * Securely clear sensitive data from memory.
 * Note: This is a best-effort approach as JavaScript doesn't guarantee memory clearing.
 */
export function secureWipe(data: Uint8Array | string): void {
	if (data instanceof Uint8Array) {
		crypto.getRandomValues(data);
		data.fill(0);
	}
}

export interface EncryptionResult {
	ciphertext: Uint8Array;
	nonce: Uint8Array;
	aad: Uint8Array;
	encryptionKey: Uint8Array;
	claimToken: Uint8Array;
	claimHash: Uint8Array;
	passwordProtected: boolean;
}

/**
 * Complete encryption workflow for creating a secret.
 * @param plaintext - The secret text to encrypt
 * @param password - Optional password for additional protection
 */
export async function encryptSecret(plaintext: string, password?: string): Promise<EncryptionResult> {
	const randomKey = generateEncryptionKey();
	const nonce = generateNonce();
	const claimToken = generateClaimToken();

	let encryptionKey: Uint8Array;
	let aad: Uint8Array;
	let passwordProtected = false;

	if (password && password.length > 0) {
		// Password protection enabled
		const salt = generateSalt();
		const passwordKey = await deriveKeyFromPassword(password, salt);
		encryptionKey = xorBytes(randomKey, passwordKey);
		aad = createAAD(salt);
		passwordProtected = true;
	} else {
		// No password
		encryptionKey = randomKey;
		aad = createAAD();
	}

	const claimHash = await sha256(claimToken);
	const ciphertext = await encrypt(plaintext, encryptionKey, nonce, aad);

	return {
		ciphertext,
		nonce,
		aad,
		encryptionKey: randomKey, // Always return the random key (stored in URL)
		claimToken,
		claimHash,
		passwordProtected
	};
}

/**
 * Complete decryption workflow for retrieving a secret.
 * @param ciphertext - The encrypted data
 * @param urlKey - The key from the URL fragment
 * @param nonce - The nonce used for encryption
 * @param aad - Additional authenticated data (contains password salt if protected)
 * @param password - Password if the secret is password-protected
 */
export async function decryptSecret(
	ciphertext: Uint8Array,
	urlKey: Uint8Array,
	nonce: Uint8Array,
	aad?: Uint8Array,
	password?: string
): Promise<string> {
	let encryptionKey = urlKey;

	if (aad) {
		const metadata = parseAAD(aad);
		if (metadata.passwordProtected) {
			if (!password) {
				throw new Error('Password required');
			}
			if (!metadata.salt) {
				throw new Error('Invalid AAD: missing salt');
			}
			const passwordKey = await deriveKeyFromPassword(password, metadata.salt);
			encryptionKey = xorBytes(urlKey, passwordKey);
		}
	}

	return decrypt(ciphertext, encryptionKey, nonce, aad);
}

/**
 * Check if AAD indicates password protection.
 */
export function isPasswordProtected(aad: Uint8Array): boolean {
	const metadata = parseAAD(aad);
	return metadata.passwordProtected;
}

/**
 * Generate a 256-bit AES key for chat encryption.
 */
export function generateChatKey(): Uint8Array {
	return generateEncryptionKey();
}

/**
 * Encrypt a chat message using AES-256-GCM with a unique nonce.
 */
export async function encryptMessage(
	plaintext: string,
	keyBytes: Uint8Array
): Promise<{ ciphertext: string; nonce: string }> {
	const nonce = generateNonce();
	const ciphertext = await encrypt(plaintext, keyBytes, nonce);
	return {
		ciphertext: encodeBase64Url(ciphertext),
		nonce: encodeBase64Url(nonce)
	};
}

/**
 * Decrypt a chat message using AES-256-GCM.
 */
export async function decryptMessage(
	ciphertextB64: string,
	nonceB64: string,
	keyBytes: Uint8Array
): Promise<string> {
	const ciphertext = decodeBase64Url(ciphertextB64);
	const nonce = decodeBase64Url(nonceB64);
	return decrypt(ciphertext, keyBytes, nonce);
}

