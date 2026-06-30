# PWA Offline Behavior Plan

**Date**: 2026-06-12  
**Status**: Assessment Required  
**Scope**: Service worker, cache strategy, offline lesson access

---

## Current State

The EduBoost frontend (Next.js) has PWA configuration but offline behavior is **unverified**.

- `next.config.js` has PWA settings
- Service worker may be registered
- Cache strategy is not documented

---

## Verification Checklist

### Service Worker

- [ ] Service worker registers successfully
- [ ] SW responds to fetch events
- [ ] SW updates on new deployment

### Cache Strategy

- [ ] Static assets cached (JS, CSS, images)
- [ ] API responses NOT cached (stale)
- [ ] Lessons cached for offline access

### Offline Lesson Access

- [ ] Downloaded lessons available without network
- [ ] Progress saved locally when offline
- [ ] Sync when network restored

---

## Recommended Cache Strategy

### Tier 1: Static Assets (Always Cache)

```javascript
// next.config.js
workbox: {
  globPatterns: ['**/*.{js,css,png,svg,ico}'],
  runtimeCaching: [{
    urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com/,
    handler: 'CacheFirst',
  }],
}
```

### Tier 2: API Responses (Network First)

```javascript
{
  urlPattern: /\/api\/v2\/.*/,
  handler: 'NetworkFirst',
  options: {
    cacheName: 'api-cache',
    networkTimeoutSeconds: 3,
    expiration: { maxEntries: 50, maxAgeSeconds: 3600 },
  },
}
```

### Tier 3: Lessons (Stale While Revalidate)

```javascript
{
  urlPattern: /\/api\/v2\/lessons\/.*/,
  handler: 'StaleWhileRevalidate',
  options: {
    cacheName: 'lessons-cache',
    expiration: { maxEntries: 20, maxAgeSeconds: 86400 * 7 }, // 7 days
  },
}
```

---

## Offline Testing

### Manual Test

1. Open DevTools → Application → Service Workers
2. Check "Offline" in Network tab
3. Navigate to a downloaded lesson
4. Verify content renders

### Automated Test (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test('lesson works offline', async ({ page }) => {
  await page.goto('/lessons/123');
  await page.evaluate(() => {
    return navigator.onLine;
  }, false); // Force offline
  
  const content = await page.locator('.lesson-content').textContent();
  expect(content).toBeTruthy();
});
```

---

## Known Gaps

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| No offline lesson download UI | Medium | Add "Download for Offline" button |
| Progress not persisted offline | High | Use IndexedDB for offline progress |
| No sync queue | High | Queue offline actions for later sync |

---

## Implementation Plan

### Phase 1: Verification (Priority)

- [ ] Verify service worker registration
- [ ] Test static asset caching
- [ ] Document current behavior

### Phase 2: Enhancement (Next Sprint)

- [ ] Add offline lesson download feature
- [ ] Implement IndexedDB for progress
- [ ] Add sync queue for offline actions

### Phase 3: Production (Q4 2026)

- [ ] Lighthouse PWA score ≥ 90
- [ ] Full offline flow tested
- [ ] User documentation

---

## Success Metrics

- Lighthouse PWA score: ≥ 90
- Offline lesson load time: < 500ms
- Sync success rate: > 95%

---

## References

- Next.js PWA: https://next-pwa-docs.vercel.app/
- Workbox: https://developer.chrome.com/docs/workbox/
- Service Worker API: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API