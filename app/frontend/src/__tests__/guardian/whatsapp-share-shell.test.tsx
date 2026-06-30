import React from "react"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import "@testing-library/jest-dom"
import { describe, it, expect, vi } from "vitest"
import WhatsAppShareShell from "../../components/guardian/WhatsAppShareShell"

describe("WhatsAppShareShell", () => {
  it("does not auto-open and only opens on approve click, emitting metadata-only audit events", async () => {
    const redacted = "Redacted summary"

    // Mock window.open
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null as unknown as Window | null)

    // Listen for audit events
    const events: Array<Record<string, unknown>> = []
    const handler = (e: Event) => {
      const ce = e as CustomEvent<Record<string, unknown>>
      events.push(ce.detail)
    }
    window.addEventListener("whatsapp-share-event", handler)

    render(<WhatsAppShareShell redactedSummary={redacted} learnerId="learner-1" guardianId="g-1" />)

    // Ensure no auto-open occurred
    expect(openSpy).not.toHaveBeenCalled()

    // Approve click should trigger the open and audit events
    const approve = screen.getByLabelText("approve-share")
    fireEvent.click(approve)

    await waitFor(() => {
      expect(openSpy).toHaveBeenCalled()
      expect(events.length).toBeGreaterThanOrEqual(1)
      // Ensure audit metadata does not include message content
      expect(events[0]).toHaveProperty("event")
      expect(events[0]).not.toHaveProperty("message")
    })

    window.removeEventListener("whatsapp-share-event", handler)
    openSpy.mockRestore()
  })
})
