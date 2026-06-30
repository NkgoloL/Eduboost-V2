export type WhatsAppShareEvent = "attempt" | "approved" | "cancelled" | "blocked"

export type WhatsAppShareMetadata = {
  event: WhatsAppShareEvent
  method?: "wa.me" | "navigator.share" | "unknown"
  learnerId?: string
  guardianId?: string
  timestamp: string
}
