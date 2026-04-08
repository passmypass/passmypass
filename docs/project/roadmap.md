# PassMyPass - Feature Roadmap & Recommendations

> Generated: January 2026 | Status: Planning

## Current State Summary

PassMyPass v1 is a solid, security-focused one-time secret sharing app with:
- End-to-end AES-256-GCM encryption (client-side)
- Zero-knowledge architecture (server never sees plaintext)
- Atomic one-time retrieval
- 5-60 minute expiry options
- Clean, responsive UI

---

## High-Impact Features

### 1. Password Protection (Priority: High)

**Why:** Users often want an extra layer of security beyond the link itself.

**Implementation:**
- Add optional password field on create page
- Derive encryption key from password using PBKDF2/Argon2
- Combine with generated key for double encryption
- Recipient must enter password before reveal

**Impact:** Significantly increases security for sensitive secrets shared via insecure channels.

---

### 2. File/Attachment Support (Priority: High)

**Why:** Users frequently need to share files (keys, configs, credentials files), not just text.

**Implementation:**
- Accept file uploads (drag & drop)
- Encrypt file binary with same AES-256-GCM
- Store encrypted blob
- Size limit: 5MB (keep infrastructure simple)
- Support common formats: .txt, .json, .pem, .key, .env

**Impact:** Major functionality expansion - addresses a very common use case.

---

### 3. QR Code Generation (Priority: High)

**Why:** Makes sharing links in person or on mobile much easier.

**Implementation:**
- Generate QR code after secret creation
- Include full URL with fragment
- Add "Download QR" button
- Mobile-optimized scanning

**Impact:** Great for in-person secret sharing, presentations, printed materials.

---

### 4. Longer Expiry Options (Priority: Medium)

**Why:** Current max of 60 minutes is limiting for async communication.

**New Options:**
- 1 hour (current max)
- 6 hours
- 24 hours
- 7 days

**Implementation:**
- Update expiry dropdown options
- Update backend TTL validation
- Consider warning users about longer expiry security implications

**Impact:** Flexibility for users in different timezones or async workflows.

---

### 5. Burn After Reading Confirmation (Priority: Medium)

**Why:** Senders often want confirmation that their secret was received.

**Implementation:**
- Optional email notification on creation
- Send email when secret is claimed (no content, just timestamp)
- Privacy-preserving: only notify that it was viewed, not by whom

**Impact:** Adds trust layer for sensitive communications.

---

### 6. Custom Slug/Vanity URLs (Priority: Medium)

**Why:** Branded or memorable links build trust and look professional.

**Implementation:**
- Optional custom slug field: `passmypass.com/s/my-secret-abc`
- Validation: alphanumeric + hyphens, 4-32 chars
- Check availability before creation
- Premium feature potential

**Impact:** Professional appearance, easier to communicate verbally.

---

### 7. API Access / Programmatic Use (Priority: Medium)

**Why:** Developers want to integrate secret sharing into their workflows.

**Implementation:**
- Public API documentation
- Optional API key authentication
- Rate limits per API key
- CLI tool (`npx passmypass "secret"`)

**Impact:** Opens B2B/developer market, enables integrations.

---

### 8. Multiple Recipients (Priority: Low)

**Why:** Sometimes need to share the same secret with several people, each with one-time access.

**Implementation:**
- Generate N unique links for same encrypted content
- Each link has unique claim token
- Track which links were consumed

**Impact:** Useful for team credential distribution.

---

## UI/UX Improvements

### High Priority

#### 1. Toast Notifications
Replace abrupt state changes with smooth toast notifications for:
- "Copied to clipboard"
- "Secret will auto-clear in 60s"
- "Link created successfully"

#### 2. Keyboard Shortcuts
- `Cmd/Ctrl + Enter` - Create secret
- `Cmd/Ctrl + C` on success screen - Copy link
- `Escape` - Close/reset

#### 3. Better Mobile Experience
- Larger tap targets on mobile (44px minimum)
- Full-width buttons on small screens
- Swipe gestures for clearing

#### 4. Loading States
- Skeleton loaders instead of spinners
- Progress indication during encryption
- Smooth transitions between states

### Medium Priority

#### 5. Dark/Light Theme Toggle
- System preference detection (already dark)
- Manual toggle in footer
- Persist preference in localStorage

#### 6. Animations & Transitions
- Fade in/out between states
- Micro-interactions on buttons
- Reveal animation for secret content

#### 7. Accessibility (a11y)
- ARIA labels on all interactive elements
- Focus management between states
- Screen reader announcements for state changes
- High contrast mode support

#### 8. Success Page Improvements
- More prominent copy button
- Visual confirmation animation
- Add "Share via..." buttons (copy to clipboard done, add email/SMS)

### Low Priority

#### 9. Empty State Illustrations
- Custom illustrations for different states
- Branded visual identity
- Error state illustrations

#### 10. Onboarding Flow
- First-time user tutorial
- Tooltips explaining security features
- "How secure is this?" expandable section

---

## Technical Improvements

### Performance
- [ ] Lazy load QR code library
- [ ] Service worker for offline create page
- [ ] Image optimization for any future assets

### Security
- [ ] Subresource Integrity (SRI) for any CDN assets
- [ ] Content Security Policy reporting endpoint
- [ ] Rate limit bypass protection (IP rotation detection)

### Monitoring
- [ ] Privacy-preserving analytics (Plausible/Fathom)
- [ ] Error tracking (Sentry with PII filtering)
- [ ] Uptime monitoring

---

## Implementation Priority Matrix

| Feature | Impact | Effort | Priority | Status |
|---------|--------|--------|----------|--------|
| QR Code Generation | High | Low | **P1** | |
| Password Protection | High | Medium | **P1** | **Done** |
| Longer Expiry Options | Medium | Low | **P1** | |
| Toast Notifications | Medium | Low | **P1** | |
| Keyboard Shortcuts | Medium | Low | **P1** | |
| File Support | High | High | **P2** | |
| Mobile UX Improvements | Medium | Medium | **P2** | **Done** |
| Dark/Light Toggle | Low | Low | **P2** | |
| Burn Confirmation | Medium | Medium | **P3** | |
| Custom Slugs | Medium | Medium | **P3** | |
| API Access | Medium | High | **P3** | |
| Multiple Recipients | Low | High | **P4** | |

---

## Recommended Next Steps

### Sprint 1: Quick Wins
1. Add QR code generation (use `qrcode` library)
2. Implement toast notification system
3. Add keyboard shortcuts
4. Extend expiry options to 24h/7d

### Sprint 2: Security Enhancement
1. Password protection feature
2. Accessibility audit and fixes
3. Loading state improvements

### Sprint 3: Major Feature
1. File upload support
2. Mobile UX overhaul
3. Animations and transitions

---

## Competitive Differentiation

Current competitors (OneTimeSecret, PrivateBin, etc.) lack:
- **Modern UI**: PassMyPass has cleaner design
- **True zero-knowledge**: Many store keys server-side
- **QR codes**: Few offer this natively
- **Password + link**: Double-layer security

Focus on these differentiators to stand out.

---

## Revenue Opportunities (Future)

1. **Premium tiers**: Custom slugs, longer expiry, higher limits
2. **Team plans**: Shared workspace, usage analytics
3. **Enterprise**: Self-hosted option, SSO, audit logs
4. **API pricing**: Usage-based for high-volume integrators

---

*This document should be reviewed and updated quarterly.*
