import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeAll } from "vitest";

import { AiTutorChat } from "../AiTutorChat";

describe("AiTutorChat", () => {
  beforeAll(() => {
    window.HTMLElement.prototype.scrollIntoView = vi.fn();
  });
  it("has an accessible question input and privacy notice", () => {
    render(<AiTutorChat learnerId="learner-1" lessonId="lesson-1" topic="fractions" />);
    expect(screen.getByLabelText(/ask the ai tutor/i)).toBeInTheDocument();
    expect(screen.getByText(/do not share your phone number/i)).toBeInTheDocument();
  });

  it("does not submit an empty question", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    render(<AiTutorChat learnerId="learner-1" lessonId="lesson-1" topic="fractions" />);
    fireEvent.click(screen.getByRole("button", { name: "Ask" }));
    expect(fetchMock).not.toHaveBeenCalled();
    vi.unstubAllGlobals();
  });
});
