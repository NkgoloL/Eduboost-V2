import type { WhatsAppShareMetadata } from "./types"

// Build a wa.me link without including a phone number on the URL.
// Use the `?text=` form so no recipient phone is embedded by us.
export function buildWaMeUrl(text: string): string {
  const encoded = encodeURIComponent(text)
  return `https://wa.me/?text=${encoded}`
}

export async function shareViaNavigator(text: string): Promise<void> {
  const nav = (typeof navigator !== "undefined")
    ? (navigator as unknown as { share?: (data: { text?: string }) => Promise<void> })
    : undefined

  if (nav?.share) {
    // This is a client-side native share; message content is handled by the platform.
    // We intentionally do not record message contents.
    await nav.share({ text })
  } else {
    throw new Error("navigator.share not available")
  }
}

// Metadata-only audit emitter. Does NOT persist message body or recipient phone.
export function emitShareAudit(metadata: WhatsAppShareMetadata) {
  try {
    // Dispatch a non-persistent client-side event for telemetry consumers.
    const ev = new CustomEvent("whatsapp-share-event", { detail: metadata })
    if (typeof window !== "undefined") window.dispatchEvent(ev)
    // Also log locally for debug; do NOT include message text here.
    // In production, hook this to a privacy-safe audit pipeline that stores metadata-only.
    // eslint-disable-next-line no-console
    console.info("whatsapp-share-audit", metadata)
  } catch (_e) {
    // swallow errors to avoid disrupting the share UX
  }
}
