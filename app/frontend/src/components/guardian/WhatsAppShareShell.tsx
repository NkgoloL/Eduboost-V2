"use client"
import React, { useState } from "react"
import { buildWaMeUrl, shareViaNavigator, emitShareAudit } from "../../lib/share/whatsapp"

type Props = {
  redactedSummary: string
  learnerId?: string
  guardianId?: string
}

export default function WhatsAppShareShell({ redactedSummary, learnerId, guardianId }: Props) {
  const [text, setText] = useState(redactedSummary)
  const [isProcessing, setIsProcessing] = useState(false)

  const onApprove = async () => {
    setIsProcessing(true)
    // Audit attempt metadata-only (do NOT include message body)
    emitShareAudit({ event: "attempt", learnerId, guardianId, timestamp: new Date().toISOString() })

    try {
      const nav = (typeof navigator !== "undefined")
        ? (navigator as unknown as { share?: (data: { text?: string }) => Promise<void> })
        : undefined

      if (nav?.share) {
        await nav.share({ text })
        emitShareAudit({ event: "approved", method: "navigator.share", learnerId, guardianId, timestamp: new Date().toISOString() })
      } else {
        // Build a client-only wa.me link without a phone number
        const url = buildWaMeUrl(text)
        // Only open on explicit user action (no auto-open on render)
        window.open(url, "_blank", "noopener,noreferrer")
        emitShareAudit({ event: "approved", method: "wa.me", learnerId, guardianId, timestamp: new Date().toISOString() })
      }
    } catch (e) {
      emitShareAudit({ event: "blocked", learnerId, guardianId, timestamp: new Date().toISOString() })
    } finally {
      setIsProcessing(false)
    }
  }

  const onCancel = () => {
    // Do not persist message body
    emitShareAudit({ event: "cancelled", learnerId, guardianId, timestamp: new Date().toISOString() })
    setText(redactedSummary)
  }

  return (
    <div aria-label="whatsapp-share-shell">
      <h3>Share summary via WhatsApp</h3>
      <p>This action is guardian-triggered only. The message is editable before sharing.</p>
      <textarea
        aria-label="whatsapp-message"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={6}
        style={{ width: "100%" }}
      />
      <div style={{ marginTop: 8 }}>
        <button aria-label="approve-share" onClick={onApprove} disabled={isProcessing}>
          Approve & Open WhatsApp
        </button>
        <button aria-label="cancel-share" onClick={onCancel} style={{ marginLeft: 8 }}>
          Cancel
        </button>
      </div>
    </div>
  )
}
