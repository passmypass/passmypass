import { describe, it, expect } from 'vitest';
import {
	encodeBase64Url,
	decodeBase64Url,
	generateEncryptionKey,
	generateNonce,
	generateChatKey,
	encryptSecret,
	decryptSecret,
	isPasswordProtected,
	encryptMessage,
	decryptMessage,
	encrypt,
	decrypt
} from './crypto';

describe('Base64URL encoding', () => {
	it('round-trips random bytes', () => {
		const original = crypto.getRandomValues(new Uint8Array(32));
		const encoded = encodeBase64Url(original);
		const decoded = decodeBase64Url(encoded);
		expect(decoded).toEqual(original);
	});

	it('produces URL-safe characters only', () => {
		const bytes = crypto.getRandomValues(new Uint8Array(64));
		const encoded = encodeBase64Url(bytes);
		expect(encoded).toMatch(/^[A-Za-z0-9_-]+$/);
	});

	it('handles empty array', () => {
		const encoded = encodeBase64Url(new Uint8Array(0));
		const decoded = decodeBase64Url(encoded);
		expect(decoded).toEqual(new Uint8Array(0));
	});
});

describe('Key generation', () => {
	it('generates 32-byte encryption keys', () => {
		const key = generateEncryptionKey();
		expect(key.length).toBe(32);
	});

	it('generates 12-byte nonces', () => {
		const nonce = generateNonce();
		expect(nonce.length).toBe(12);
	});

	it('generates unique keys each time', () => {
		const key1 = generateEncryptionKey();
		const key2 = generateEncryptionKey();
		expect(key1).not.toEqual(key2);
	});

	it('generates 32-byte chat keys', () => {
		const key = generateChatKey();
		expect(key.length).toBe(32);
	});
});

describe('AES-256-GCM encrypt/decrypt', () => {
	it('encrypts and decrypts text correctly', async () => {
		const key = generateEncryptionKey();
		const nonce = generateNonce();
		const plaintext = 'hello world';

		const ciphertext = await encrypt(plaintext, key, nonce);
		const decrypted = await decrypt(ciphertext, key, nonce);
		expect(decrypted).toBe(plaintext);
	});

	it('encrypts and decrypts with AAD', async () => {
		const key = generateEncryptionKey();
		const nonce = generateNonce();
		const aad = new Uint8Array([0x01, 0x00]);
		const plaintext = 'secret with aad';

		const ciphertext = await encrypt(plaintext, key, nonce, aad);
		const decrypted = await decrypt(ciphertext, key, nonce, aad);
		expect(decrypted).toBe(plaintext);
	});

	it('fails to decrypt with wrong key', async () => {
		const key1 = generateEncryptionKey();
		const key2 = generateEncryptionKey();
		const nonce = generateNonce();

		const ciphertext = await encrypt('secret', key1, nonce);
		await expect(decrypt(ciphertext, key2, nonce)).rejects.toThrow();
	});

	it('fails to decrypt with wrong nonce', async () => {
		const key = generateEncryptionKey();
		const nonce1 = generateNonce();
		const nonce2 = generateNonce();

		const ciphertext = await encrypt('secret', key, nonce1);
		await expect(decrypt(ciphertext, key, nonce2)).rejects.toThrow();
	});

	it('fails to decrypt with wrong AAD', async () => {
		const key = generateEncryptionKey();
		const nonce = generateNonce();
		const aad1 = new Uint8Array([0x01, 0x00]);
		const aad2 = new Uint8Array([0x01, 0x01]);

		const ciphertext = await encrypt('secret', key, nonce, aad1);
		await expect(decrypt(ciphertext, key, nonce, aad2)).rejects.toThrow();
	});

	it('ciphertext differs from plaintext', async () => {
		const key = generateEncryptionKey();
		const nonce = generateNonce();
		const plaintext = 'do not store this';

		const ciphertext = await encrypt(plaintext, key, nonce);
		const ciphertextStr = new TextDecoder().decode(ciphertext);
		expect(ciphertextStr).not.toBe(plaintext);
	});
});

describe('Full secret encryption workflow', () => {
	it('encrypts and decrypts without password', async () => {
		const result = await encryptSecret('my-api-key-123');
		expect(result.passwordProtected).toBe(false);
		expect(result.encryptionKey.length).toBe(32);
		expect(result.claimToken.length).toBe(32);
		expect(result.claimHash.length).toBe(32);
		expect(result.nonce.length).toBe(12);

		const decrypted = await decryptSecret(
			result.ciphertext,
			result.encryptionKey,
			result.nonce,
			result.aad
		);
		expect(decrypted).toBe('my-api-key-123');
	});

	it('encrypts and decrypts with password', async () => {
		const result = await encryptSecret('password-protected-secret', 'mypassword');
		expect(result.passwordProtected).toBe(true);

		const decrypted = await decryptSecret(
			result.ciphertext,
			result.encryptionKey,
			result.nonce,
			result.aad,
			'mypassword'
		);
		expect(decrypted).toBe('password-protected-secret');
	});

	it('fails to decrypt password-protected secret without password', async () => {
		const result = await encryptSecret('secret', 'pass123');

		await expect(
			decryptSecret(result.ciphertext, result.encryptionKey, result.nonce, result.aad)
		).rejects.toThrow('Password required');
	});

	it('fails to decrypt with wrong password', async () => {
		const result = await encryptSecret('secret', 'correct-password');

		await expect(
			decryptSecret(
				result.ciphertext,
				result.encryptionKey,
				result.nonce,
				result.aad,
				'wrong-password'
			)
		).rejects.toThrow();
	});

	it('detects password protection from AAD', async () => {
		const withPassword = await encryptSecret('s', 'p');
		const withoutPassword = await encryptSecret('s');

		expect(isPasswordProtected(withPassword.aad)).toBe(true);
		expect(isPasswordProtected(withoutPassword.aad)).toBe(false);
	});
});

describe('Chat message encryption', () => {
	it('encrypts and decrypts chat messages', async () => {
		const key = generateChatKey();
		const message = 'hello from chat';

		const encrypted = await encryptMessage(message, key);
		expect(encrypted.ciphertext).toBeTruthy();
		expect(encrypted.nonce).toBeTruthy();

		const decrypted = await decryptMessage(encrypted.ciphertext, encrypted.nonce, key);
		expect(decrypted).toBe(message);
	});

	it('each message gets a unique nonce', async () => {
		const key = generateChatKey();
		const enc1 = await encryptMessage('msg1', key);
		const enc2 = await encryptMessage('msg2', key);
		expect(enc1.nonce).not.toBe(enc2.nonce);
	});

	it('cannot decrypt with wrong key', async () => {
		const key1 = generateChatKey();
		const key2 = generateChatKey();

		const encrypted = await encryptMessage('secret message', key1);
		await expect(decryptMessage(encrypted.ciphertext, encrypted.nonce, key2)).rejects.toThrow();
	});
});

describe('Edge cases', () => {
	it('handles empty string encryption', async () => {
		const result = await encryptSecret('');
		const decrypted = await decryptSecret(
			result.ciphertext,
			result.encryptionKey,
			result.nonce,
			result.aad
		);
		expect(decrypted).toBe('');
	});

	it('handles unicode content', async () => {
		const unicode = 'Hello! Привет! こんにちは! 🔐🔑';
		const result = await encryptSecret(unicode);
		const decrypted = await decryptSecret(
			result.ciphertext,
			result.encryptionKey,
			result.nonce,
			result.aad
		);
		expect(decrypted).toBe(unicode);
	});

	it('handles large content', async () => {
		const large = 'A'.repeat(10000);
		const result = await encryptSecret(large);
		const decrypted = await decryptSecret(
			result.ciphertext,
			result.encryptionKey,
			result.nonce,
			result.aad
		);
		expect(decrypted).toBe(large);
	});
});
