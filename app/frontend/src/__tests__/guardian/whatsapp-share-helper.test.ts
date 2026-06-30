import { describe, it, expect } from "vitest"
import { buildWaMeUrl } from "../../lib/share/whatsapp"

describe("buildWaMeUrl", () => {
  it("constructs a wa.me url using ?text= and does not include a phone number", () => {
    const url = buildWaMeUrl("Hello guardian")
    expect(url).toContain("https://wa.me/")
    expect(url).toContain("text=")
    // Ensure we did not place digits directly after the host (no phone number path)
    expect(url).toMatch(/^https:\/\/wa\.me\/(\?|$)/)
  })
})
