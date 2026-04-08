# PassMyPass File Upload - Implementation Specification

> Feature: Encrypted File/Attachment Support

## Overview

Enable users to share files (SSH keys, config files, credentials, etc.) with the same zero-knowledge security as text secrets. Files are encrypted entirely in the browser before upload - the server never sees plaintext content.

---

## Security Model

### Encryption Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. User selects/drops file                                      │
│                    ↓                                             │
│  2. Validate: size ≤ 5MB, allowed extension                      │
│                    ↓                                             │
│  3. Read file as ArrayBuffer                                     │
│                    ↓                                             │
│  4. Generate random 256-bit AES key                              │
│                    ↓                                             │
│  5. (Optional) Derive password key via PBKDF2, XOR with AES key  │
│                    ↓                                             │
│  6. Encrypt file bytes with AES-256-GCM                          │
│  7. Encrypt filename with same key (privacy)                     │
│                    ↓                                             │
│  8. Send to server: ciphertext, nonce, AAD, encrypted filename   │
│                                                                  │
│  ✓ Key stays in URL fragment - NEVER sent to server              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (encrypted data only)
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Stores:                                                         │
│    • ciphertext (encrypted file bytes)                           │
│    • nonce (IV for AES-GCM)                                      │
│    • aad (salt if password protected)                            │
│    • claim_hash (SHA-256 of claim token)                         │
│    • encrypted_filename (encrypted original name)                │
│    • content_type (MIME type for download)                       │
│    • file_size (original size for display)                       │
│                                                                  │
│  Never sees:                                                     │
│    • Plaintext file content                                      │
│    • Original filename                                           │
│    • Encryption key                                              │
│    • Password (if set)                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### What's Encrypted vs Plain

| Field | Encrypted? | Why |
|-------|------------|-----|
| File content | ✅ Yes | Core secret |
| Filename | ✅ Yes | May reveal sensitive info (e.g., `prod-db-creds.json`) |
| File size | ❌ No | Needed for validation and UI display |
| Content type | ❌ No | Needed for proper download headers |
| Encryption key | N/A | Never sent to server (stays in URL #fragment) |

---

## Database Changes

### Migration SQL

```sql
-- Add file-related columns to secrets table
ALTER TABLE secrets
  ADD COLUMN is_file BOOLEAN DEFAULT FALSE,
  ADD COLUMN encrypted_filename BYTEA,
  ADD COLUMN content_type VARCHAR(100),
  ADD COLUMN file_size INTEGER;

-- Index for potential cleanup queries
CREATE INDEX idx_secrets_is_file ON secrets(is_file) WHERE is_file = TRUE;

-- Update constraint: file_size must be set if is_file is true
ALTER TABLE secrets
  ADD CONSTRAINT chk_file_has_size
  CHECK (is_file = FALSE OR file_size IS NOT NULL);
```

### SQLAlchemy Model Update

```python
# server/app/models.py

class Secret(Base):
    __tablename__ = "secrets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ciphertext = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary, nullable=False)
    aad = Column(LargeBinary, nullable=True)
    claim_hash = Column(String(64), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # New file-related columns
    is_file = Column(Boolean, default=False, nullable=False)
    encrypted_filename = Column(LargeBinary, nullable=True)
    content_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)  # Original size in bytes
```

### Pydantic Schema Update

```python
# server/app/schemas.py

class SecretCreate(BaseModel):
    ciphertext: str  # Base64 encoded
    nonce: str       # Base64 encoded
    aad: Optional[str] = None
    claim_hash: str
    ttl_minutes: int = Field(ge=5, le=10080)

    # New file fields
    is_file: bool = False
    encrypted_filename: Optional[str] = None  # Base64 encoded
    content_type: Optional[str] = None
    file_size: Optional[int] = Field(None, le=5_242_880)  # Max 5MB

    @validator('file_size')
    def validate_file_fields(cls, v, values):
        if values.get('is_file') and not v:
            raise ValueError('file_size required for file uploads')
        return v

class SecretResponse(BaseModel):
    id: str
    is_file: bool
    encrypted_filename: Optional[str]
    content_type: Optional[str]
    file_size: Optional[int]
```

---

## Backend Changes

### API Route Updates

```python
# server/app/routes.py

@router.post("/secrets", response_model=SecretCreateResponse)
@limiter.limit("30/minute")
async def create_secret(
    request: Request,
    data: SecretCreate,
    db: AsyncSession = Depends(get_db)
):
    # Validate file size on ciphertext (encrypted size ≈ original + 16 bytes)
    ciphertext_bytes = base64.b64decode(data.ciphertext)
    if len(ciphertext_bytes) > 5_500_000:  # ~5MB + encryption overhead
        raise HTTPException(400, "File too large (max 5MB)")

    secret = Secret(
        ciphertext=ciphertext_bytes,
        nonce=base64.b64decode(data.nonce),
        aad=base64.b64decode(data.aad) if data.aad else None,
        claim_hash=data.claim_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=data.ttl_minutes),
        # File fields
        is_file=data.is_file,
        encrypted_filename=base64.b64decode(data.encrypted_filename) if data.encrypted_filename else None,
        content_type=data.content_type,
        file_size=data.file_size
    )

    db.add(secret)
    await db.commit()

    return SecretCreateResponse(id=str(secret.id))


@router.post("/secrets/{secret_id}/claim", response_model=SecretClaimResponse)
@limiter.limit("60/minute")
async def claim_secret(
    request: Request,
    secret_id: UUID,
    data: SecretClaim,
    db: AsyncSession = Depends(get_db)
):
    # Existing atomic claim logic...
    result = await db.execute(
        update(Secret)
        .where(
            Secret.id == secret_id,
            Secret.claim_hash == data.claim_hash,
            Secret.consumed_at.is_(None),
            Secret.expires_at > datetime.utcnow()
        )
        .values(consumed_at=datetime.utcnow())
        .returning(
            Secret.ciphertext,
            Secret.nonce,
            Secret.aad,
            Secret.is_file,
            Secret.encrypted_filename,
            Secret.content_type,
            Secret.file_size
        )
    )

    row = result.first()
    if not row:
        raise HTTPException(404, "Secret not found or already claimed")

    return SecretClaimResponse(
        ciphertext=base64.b64encode(row.ciphertext).decode(),
        nonce=base64.b64encode(row.nonce).decode(),
        aad=base64.b64encode(row.aad).decode() if row.aad else None,
        is_file=row.is_file,
        encrypted_filename=base64.b64encode(row.encrypted_filename).decode() if row.encrypted_filename else None,
        content_type=row.content_type,
        file_size=row.file_size
    )
```

---

## Frontend Changes

### 1. Crypto Module Extensions

```typescript
// src/lib/crypto.ts

/**
 * Encrypt a file with AES-256-GCM
 * Returns encrypted content + encrypted filename
 */
export async function encryptFile(
  file: File,
  password?: string
): Promise<{
  ciphertext: Uint8Array;
  nonce: Uint8Array;
  aad: Uint8Array | null;
  encryptedFilename: Uint8Array;
  key: Uint8Array;
  claimToken: string;
  contentType: string;
  fileSize: number;
}> {
  // Read file as ArrayBuffer
  const buffer = await file.arrayBuffer();
  const plaintext = new Uint8Array(buffer);

  // Generate random key and claim token
  const key = crypto.getRandomValues(new Uint8Array(32));
  const claimToken = generateClaimToken();
  const nonce = crypto.getRandomValues(new Uint8Array(12));

  let encryptionKey = key;
  let aad: Uint8Array | null = null;

  // If password provided, derive key and XOR with random key
  if (password) {
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const passwordKey = await deriveKeyFromPassword(password, salt);
    encryptionKey = xorKeys(key, passwordKey);
    aad = salt;
  }

  // Import key for encryption
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    encryptionKey,
    { name: 'AES-GCM' },
    false,
    ['encrypt']
  );

  // Encrypt file content
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: nonce, additionalData: aad || new Uint8Array(0) },
      cryptoKey,
      plaintext
    )
  );

  // Encrypt filename separately (for privacy)
  const filenameBytes = new TextEncoder().encode(file.name);
  const filenameNonce = crypto.getRandomValues(new Uint8Array(12));
  const encryptedFilenameContent = new Uint8Array(
    await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: filenameNonce },
      cryptoKey,
      filenameBytes
    )
  );

  // Prepend nonce to encrypted filename
  const encryptedFilename = new Uint8Array(12 + encryptedFilenameContent.length);
  encryptedFilename.set(filenameNonce);
  encryptedFilename.set(encryptedFilenameContent, 12);

  return {
    ciphertext,
    nonce,
    aad,
    encryptedFilename,
    key,
    claimToken,
    contentType: file.type || 'application/octet-stream',
    fileSize: file.size
  };
}

/**
 * Decrypt a file and return as downloadable Blob
 */
export async function decryptFile(
  ciphertext: Uint8Array,
  nonce: Uint8Array,
  encryptedFilename: Uint8Array,
  key: Uint8Array,
  contentType: string,
  aad?: Uint8Array,
  password?: string
): Promise<{ blob: Blob; filename: string }> {
  let decryptionKey = key;

  // If password protected, derive and XOR
  if (password && aad) {
    const passwordKey = await deriveKeyFromPassword(password, aad);
    decryptionKey = xorKeys(key, passwordKey);
  }

  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    decryptionKey,
    { name: 'AES-GCM' },
    false,
    ['decrypt']
  );

  // Decrypt file content
  const plaintext = new Uint8Array(
    await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: nonce, additionalData: aad || new Uint8Array(0) },
      cryptoKey,
      ciphertext
    )
  );

  // Decrypt filename
  const filenameNonce = encryptedFilename.slice(0, 12);
  const filenameContent = encryptedFilename.slice(12);
  const filenameBytes = new Uint8Array(
    await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: filenameNonce },
      cryptoKey,
      filenameContent
    )
  );
  const filename = new TextDecoder().decode(filenameBytes);

  return {
    blob: new Blob([plaintext], { type: contentType }),
    filename
  };
}
```

### 2. API Client Updates

```typescript
// src/lib/api.ts

export interface CreateSecretParams {
  ciphertext: string;  // Base64
  nonce: string;       // Base64
  aad?: string;        // Base64
  claimHash: string;
  ttlMinutes: number;
  // File fields
  isFile?: boolean;
  encryptedFilename?: string;  // Base64
  contentType?: string;
  fileSize?: number;
}

export async function createSecret(params: CreateSecretParams): Promise<{ id: string }> {
  const response = await fetch('/api/secrets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ciphertext: params.ciphertext,
      nonce: params.nonce,
      aad: params.aad,
      claim_hash: params.claimHash,
      ttl_minutes: params.ttlMinutes,
      is_file: params.isFile || false,
      encrypted_filename: params.encryptedFilename,
      content_type: params.contentType,
      file_size: params.fileSize
    })
  });

  if (!response.ok) {
    throw new Error('Failed to create secret');
  }

  return response.json();
}
```

### 3. UI Components

#### File Drop Zone Component

```svelte
<!-- src/lib/components/FileDropZone.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{ file: File }>();

  let isDragging = $state(false);
  let error = $state<string | null>(null);

  const MAX_SIZE = 5 * 1024 * 1024; // 5MB
  const ALLOWED_EXTENSIONS = ['.txt', '.json', '.pem', '.key', '.env', '.xml', '.yaml', '.yml', '.csv', '.log'];

  function validateFile(file: File): string | null {
    if (file.size > MAX_SIZE) {
      return `File too large. Maximum size is 5MB.`;
    }

    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `File type not allowed. Supported: ${ALLOWED_EXTENSIONS.join(', ')}`;
    }

    return null;
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    isDragging = false;

    const file = e.dataTransfer?.files[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      error = validationError;
      return;
    }

    error = null;
    dispatch('file', file);
  }

  function handleFileSelect(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      error = validationError;
      return;
    }

    error = null;
    dispatch('file', file);
  }
</script>

<div
  class="drop-zone"
  class:dragging={isDragging}
  ondragover={(e) => { e.preventDefault(); isDragging = true; }}
  ondragleave={() => isDragging = false}
  ondrop={handleDrop}
  role="button"
  tabindex="0"
>
  <input
    type="file"
    accept={ALLOWED_EXTENSIONS.join(',')}
    onchange={handleFileSelect}
    class="hidden"
    id="file-input"
  />

  <label for="file-input" class="cursor-pointer">
    <div class="icon">📁</div>
    <p>Drop a file here or click to browse</p>
    <p class="hint">Max 5MB · .txt, .json, .pem, .key, .env, .xml, .yaml</p>
  </label>

  {#if error}
    <p class="error">{error}</p>
  {/if}
</div>

<style>
  .drop-zone {
    border: 2px dashed var(--border-color);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    transition: all 0.2s;
  }

  .drop-zone.dragging {
    border-color: var(--primary);
    background: var(--primary-bg);
  }

  .hint {
    font-size: 0.875rem;
    color: var(--text-muted);
  }

  .error {
    color: var(--error);
    margin-top: 0.5rem;
  }
</style>
```

#### File Preview Component

```svelte
<!-- src/lib/components/FilePreview.svelte -->
<script lang="ts">
  interface Props {
    file: File;
    onRemove: () => void;
  }

  let { file, onRemove }: Props = $props();

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }

  function getFileIcon(type: string): string {
    if (type.includes('json')) return '📋';
    if (type.includes('text')) return '📄';
    if (file.name.endsWith('.pem') || file.name.endsWith('.key')) return '🔑';
    if (file.name.endsWith('.env')) return '⚙️';
    return '📁';
  }
</script>

<div class="file-preview">
  <span class="icon">{getFileIcon(file.type)}</span>
  <div class="info">
    <span class="name">{file.name}</span>
    <span class="size">{formatSize(file.size)}</span>
  </div>
  <button onclick={onRemove} class="remove" aria-label="Remove file">×</button>
</div>

<style>
  .file-preview {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid var(--border-color);
  }

  .icon {
    font-size: 1.5rem;
  }

  .info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .name {
    font-weight: 500;
    word-break: break-all;
  }

  .size {
    font-size: 0.875rem;
    color: var(--text-muted);
  }

  .remove {
    padding: 0.25rem 0.5rem;
    font-size: 1.25rem;
    line-height: 1;
    background: transparent;
    border: none;
    cursor: pointer;
    opacity: 0.5;
  }

  .remove:hover {
    opacity: 1;
  }
</style>
```

### 4. Main Page Updates

```svelte
<!-- src/routes/+page.svelte (partial update) -->
<script lang="ts">
  import FileDropZone from '$lib/components/FileDropZone.svelte';
  import FilePreview from '$lib/components/FilePreview.svelte';
  import { encryptFile, encryptText } from '$lib/crypto';

  type InputMode = 'text' | 'file';

  let inputMode = $state<InputMode>('text');
  let secretText = $state('');
  let selectedFile = $state<File | null>(null);
  let password = $state('');
  let ttlMinutes = $state(60);

  async function handleSubmit() {
    if (inputMode === 'file' && selectedFile) {
      await createFileSecret();
    } else {
      await createTextSecret();
    }
  }

  async function createFileSecret() {
    if (!selectedFile) return;

    const encrypted = await encryptFile(selectedFile, password || undefined);

    const { id } = await createSecret({
      ciphertext: base64Encode(encrypted.ciphertext),
      nonce: base64Encode(encrypted.nonce),
      aad: encrypted.aad ? base64Encode(encrypted.aad) : undefined,
      claimHash: await sha256(encrypted.claimToken),
      ttlMinutes,
      isFile: true,
      encryptedFilename: base64Encode(encrypted.encryptedFilename),
      contentType: encrypted.contentType,
      fileSize: encrypted.fileSize
    });

    // Build URL with key in fragment
    const fragment = `${base64Encode(encrypted.key)}.${encrypted.claimToken}`;
    shareUrl = `${window.location.origin}/s/${id}#${fragment}`;
  }
</script>

<!-- Mode Toggle -->
<div class="mode-toggle">
  <button
    class:active={inputMode === 'text'}
    onclick={() => inputMode = 'text'}
  >
    Text
  </button>
  <button
    class:active={inputMode === 'file'}
    onclick={() => inputMode = 'file'}
  >
    File
  </button>
</div>

<!-- Conditional Input -->
{#if inputMode === 'text'}
  <textarea bind:value={secretText} placeholder="Enter your secret..."></textarea>
{:else}
  {#if selectedFile}
    <FilePreview file={selectedFile} onRemove={() => selectedFile = null} />
  {:else}
    <FileDropZone onfile={(e) => selectedFile = e.detail} />
  {/if}
{/if}
```

### 5. Retrieve Page Updates

```svelte
<!-- src/routes/s/[id]/+page.svelte (partial update) -->
<script lang="ts">
  import { decryptFile, decryptText } from '$lib/crypto';

  let isFile = $state(false);
  let decryptedBlob = $state<Blob | null>(null);
  let decryptedFilename = $state<string>('');

  async function revealSecret() {
    const response = await claimSecret(secretId, claimHash);

    isFile = response.is_file;

    if (isFile) {
      const { blob, filename } = await decryptFile(
        base64Decode(response.ciphertext),
        base64Decode(response.nonce),
        base64Decode(response.encrypted_filename),
        key,
        response.content_type,
        response.aad ? base64Decode(response.aad) : undefined,
        password || undefined
      );

      decryptedBlob = blob;
      decryptedFilename = filename;
    } else {
      // Existing text decryption logic
    }
  }

  function downloadFile() {
    if (!decryptedBlob || !decryptedFilename) return;

    const url = URL.createObjectURL(decryptedBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = decryptedFilename;
    a.click();
    URL.revokeObjectURL(url);
  }
</script>

{#if isFile && decryptedBlob}
  <div class="file-result">
    <p>File decrypted successfully</p>
    <p class="filename">{decryptedFilename}</p>
    <button onclick={downloadFile}>Download File</button>
  </div>
{:else if decryptedText}
  <!-- Existing text display -->
{/if}
```

---

## Validation Rules

### File Constraints

| Constraint | Value | Reason |
|------------|-------|--------|
| Max file size | 5 MB | Keep infrastructure simple, prevent abuse |
| Allowed extensions | .txt, .json, .pem, .key, .env, .xml, .yaml, .yml, .csv, .log | Security-focused file types |
| Filename max length | 255 chars | Filesystem compatibility |

### Blocked File Types

- Executables: .exe, .bat, .sh, .cmd, .msi, .app
- Archives: .zip, .tar, .gz, .rar (can hide executables)
- Scripts: .js, .py, .rb, .php (prevent malware distribution)
- Documents: .doc, .pdf (use dedicated services for these)

---

## Implementation Checklist

### Phase 1: Backend
- [ ] Add database migration for new columns
- [ ] Update SQLAlchemy model
- [ ] Update Pydantic schemas
- [ ] Modify create endpoint to accept file metadata
- [ ] Modify claim endpoint to return file metadata
- [ ] Add file size validation
- [ ] Write backend tests

### Phase 2: Frontend Crypto
- [ ] Implement `encryptFile()` function
- [ ] Implement `decryptFile()` function
- [ ] Implement filename encryption/decryption
- [ ] Add password support for files
- [ ] Write crypto tests

### Phase 3: Frontend UI
- [ ] Create FileDropZone component
- [ ] Create FilePreview component
- [ ] Add mode toggle (text/file) to create page
- [ ] Update create page state management
- [ ] Update API client
- [ ] Update retrieve page for file display
- [ ] Add download button functionality
- [ ] Test drag & drop on mobile

### Phase 4: Polish
- [ ] Loading states during encryption/upload
- [ ] Progress indicator for large files
- [ ] Error handling and user feedback
- [ ] Accessibility audit
- [ ] Mobile responsiveness check

---

## Testing Plan

### Unit Tests

```typescript
// crypto.test.ts
describe('File Encryption', () => {
  it('encrypts and decrypts file correctly', async () => {
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const encrypted = await encryptFile(file);
    const decrypted = await decryptFile(
      encrypted.ciphertext,
      encrypted.nonce,
      encrypted.encryptedFilename,
      encrypted.key,
      encrypted.contentType
    );

    expect(decrypted.filename).toBe('test.txt');
    expect(await decrypted.blob.text()).toBe('test content');
  });

  it('encrypts and decrypts with password', async () => {
    const file = new File(['secret'], 'secret.key');
    const encrypted = await encryptFile(file, 'password123');
    const decrypted = await decryptFile(
      encrypted.ciphertext,
      encrypted.nonce,
      encrypted.encryptedFilename,
      encrypted.key,
      encrypted.contentType,
      encrypted.aad!,
      'password123'
    );

    expect(await decrypted.blob.text()).toBe('secret');
  });

  it('fails with wrong password', async () => {
    const file = new File(['secret'], 'secret.key');
    const encrypted = await encryptFile(file, 'password123');

    await expect(decryptFile(
      encrypted.ciphertext,
      encrypted.nonce,
      encrypted.encryptedFilename,
      encrypted.key,
      encrypted.contentType,
      encrypted.aad!,
      'wrongpassword'
    )).rejects.toThrow();
  });
});
```

### Integration Tests

```python
# test_file_upload.py
async def test_file_upload_flow():
    # Create file secret
    response = await client.post("/api/secrets", json={
        "ciphertext": base64_encode(encrypted_content),
        "nonce": base64_encode(nonce),
        "claim_hash": claim_hash,
        "ttl_minutes": 60,
        "is_file": True,
        "encrypted_filename": base64_encode(enc_filename),
        "content_type": "text/plain",
        "file_size": 100
    })
    assert response.status_code == 201

    # Claim and verify
    secret_id = response.json()["id"]
    claim_response = await client.post(f"/api/secrets/{secret_id}/claim", json={
        "claim_hash": claim_hash
    })
    assert claim_response.json()["is_file"] == True
    assert claim_response.json()["file_size"] == 100
```

---

## Performance Considerations

### Large File Handling

For files approaching 5MB:

1. **Chunked Reading**: Read file in chunks to avoid memory spikes
2. **Progress Indicator**: Show encryption progress for UX
3. **Web Worker**: Offload encryption to avoid UI blocking

```typescript
// Using Web Worker for encryption (optional optimization)
const worker = new Worker('/crypto-worker.js');

worker.postMessage({ type: 'encrypt', file, password });
worker.onmessage = (e) => {
  if (e.data.type === 'progress') {
    progressPercent = e.data.percent;
  } else if (e.data.type === 'complete') {
    encryptedData = e.data.result;
  }
};
```

---

## Security Reminders

1. **Never log file content** - not even encrypted
2. **Validate on both client and server** - never trust client
3. **Filename is sensitive** - always encrypt it
4. **Clear memory after decryption** - sensitive data shouldn't linger
5. **No file preview** - don't render file content (XSS risk)

---

*Last updated: January 2026*
