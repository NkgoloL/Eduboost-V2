# FE-SPIKE-005: AI Tutor Streaming Safety and Latency

## 1. Streaming Architecture
- **Proxy Server Route:** Client calls Next.js `/api/tutor` route, which securely holds the Claude API keys.
- **Server-Sent Events (SSE):** Next.js API acts as an Edge/Node proxy, streaming Claude tokens back to the client token-by-token.
- **State Management:** The client receives SSE streams and accumulates tokens in a React state hook (`useTutorStream`) to animate the AI typing effect.

## 2. Latency Measurements (Estimated)
- **Time to First Token (TTFT):** ~800ms - 1.5s via Claude 3 API depending on JNB Edge routing.
- **Streaming Speed:** ~20-30 tokens per second.
- **Perceived Latency:** By streaming instantly, the Grade R learner perceives a reaction within < 1 second. Adding a "thinking" earcon covers this initial TTFT gap gracefully.

## 3. Moderation & Safety Boundaries
- **System Prompt:** Strictly bounds the model to act as a CAPS-aligned Grade R tutor. It must refuse to discuss off-topic subjects (politics, violence, non-educational topics).
- **Output Filtering:** PII scrubbers run on the server *before* sending context to Claude.
- **Refusal Gracefulness:** If asked an inappropriate question, the bot redirects: *"I'm here to help you learn! Let's talk about [current lesson topic]."*

## 4. Parent-Review Implications
- All sessions must be logged in a pseudonymous format to the database for parent review via the Parent Portal.
- This creates transparency and satisfies POPIA compliance for AI usage with minors.
- **Retention:** Tutor session history is retained for 30 days and accessible only by authenticated guardians.

## 5. Rate-Limit Behavior
- To prevent abuse and manage API costs, learners are limited to 5 turns per lesson.
- Exceeding the rate limit returns a 429 status and gracefully disables the tutor input, displaying: *"EduBot needs a rest! Let's continue with the lesson."*

## 6. Audit Event Requirements
- `tutor.session_started`
- `tutor.turn_completed`
- `tutor.rate_limit_exceeded`
- `tutor.safety_filter_triggered` (Critical severity alert)

## 7. Verdict
**PROCEED WITH CONDITIONS — pending reviewer acceptance**

## Hard Constraints
- No unrestricted free-chat.
- Server-only provider keys.
- Input filtering required.
- Output filtering required.
- Prompt boundary required.
- Rate limits required.
- Audit events required.
- Parent-review schema required before storing tutor history.
- Retention policy required before tutor history is enabled.
- Voice integration blocked until FE-SPIKE-004 is accepted.

*The streaming architecture provides acceptable latency, and the safety boundaries/parent review model fulfill the compliance requirements. Rate limits and audit hooks must be strictly enforced in implementation.*
