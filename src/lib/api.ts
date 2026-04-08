/**
 * API client for communicating with the backend.
 */

// In production, use the API subdomain; in development, use the proxy
const API_HOST = import.meta.env.PROD ? 'https://api.passmypass.com' : '';
const API_BASE = `${API_HOST}/api/secrets`;

export interface CreateSecretRequest {
	ciphertext_b64u: string;
	nonce_b64u: string;
	aad_b64u?: string;
	claim_hash_b64u: string;
	expires_in_seconds: number;
}

export interface CreateSecretResponse {
	id: string;
	expires_at: string;
}

export interface SecretStatusResponse {
	exists: boolean;
	consumed: boolean;
	expired: boolean;
	expires_at: string | null;
}

export interface ClaimSecretRequest {
	claim_token_b64u: string;
}

export interface ClaimSecretResponse {
	ciphertext_b64u: string;
	nonce_b64u: string;
	aad_b64u: string | null;
}

export class ApiError extends Error {
	constructor(
		public status: number,
		message: string
	) {
		super(message);
		this.name = 'ApiError';
	}
}

async function handleResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		let message = 'An error occurred';
		try {
			const data = await response.json();
			message = data.detail || message;
		} catch {
			// Ignore JSON parse errors
		}
		throw new ApiError(response.status, message);
	}
	return response.json();
}

/**
 * Create a new one-time secret.
 */
export async function createSecret(request: CreateSecretRequest): Promise<CreateSecretResponse> {
	const response = await fetch(API_BASE, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(request)
	});

	return handleResponse<CreateSecretResponse>(response);
}

/**
 * Check the status of a secret (non-consuming).
 */
export async function getSecretStatus(secretId: string): Promise<SecretStatusResponse> {
	const response = await fetch(`${API_BASE}/${secretId}/status`);
	return handleResponse<SecretStatusResponse>(response);
}

/**
 * Claim and retrieve a secret (one-time operation).
 */
export async function claimSecret(
	secretId: string,
	request: ClaimSecretRequest
): Promise<ClaimSecretResponse> {
	const response = await fetch(`${API_BASE}/${secretId}/claim`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(request)
	});

	return handleResponse<ClaimSecretResponse>(response);
}

/**
 * Get WebSocket URL for chat room.
 */
export function getChatWsUrl(roomId: string): string {
	if (import.meta.env.PROD) {
		return `wss://api.passmypass.com/api/chat/rooms/${roomId}/ws`;
	}
	const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
	return `${protocol}//${window.location.host}/api/chat/rooms/${roomId}/ws`;
}

/**
 * Create a new chat room.
 */
export async function createChatRoom(): Promise<{ room_id: string }> {
	const host = import.meta.env.PROD ? 'https://api.passmypass.com' : '';
	const response = await fetch(`${host}/api/chat/rooms`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		}
	});

	return handleResponse<{ room_id: string }>(response);
}
