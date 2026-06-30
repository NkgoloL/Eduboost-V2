"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type TutorMessage = { role: "learner" | "assistant"; content: string };

type Props = {
  learnerId: string;
  lessonId: string;
  topic: string;
  language?: string;
};

function unwrap<T>(payload: unknown): T {
  if (payload && typeof payload === "object" && "data" in payload) {
    return (payload as { data: T }).data;
  }
  return payload as T;
}

export function AiTutorChat({ learnerId, lessonId, topic, language = "en" }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<"idle" | "thinking" | "offline" | "error">("idle");
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => () => abortRef.current?.abort(), []);
  useEffect(() => {
    if (typeof bottomRef.current?.scrollIntoView === "function") {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  async function ensureSession(): Promise<string> {
    if (sessionId) return sessionId;
    const response = await fetch("/api/v2/tutor/sessions", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ learner_id: learnerId, lesson_id: lessonId, language }),
    });
    if (!response.ok) throw new Error("Could not start the tutor session");
    const payload = unwrap<{ session_id: string }>(await response.json());
    setSessionId(payload.session_id);
    return payload.session_id;
  }

  async function send(text: string) {
    const clean = text.trim();
    if (!clean || status === "thinking") return;
    setInput("");
    setMessages((items) => [...items, { role: "learner", content: clean }, { role: "assistant", content: "" }]);
    setStatus("thinking");
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const activeSession = await ensureSession();
      const clientMessageId = `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      const response = await fetch(`/api/v2/tutor/sessions/${activeSession}/messages/stream`, {
        method: "POST",
        credentials: "include",
        signal: controller.signal,
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify({ text: clean, client_message_id: clientMessageId }),
      });
      if (!response.ok || !response.body) throw new Error("Tutor connection failed");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let reply = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const frames = buffer.split("\n\n");
        buffer = frames.pop() || "";
        for (const frame of frames) {
          const event = frame.match(/^event:\s*(.+)$/m)?.[1];
          const raw = frame.match(/^data:\s*(.+)$/m)?.[1];
          if (!raw) continue;
          const data = JSON.parse(raw) as { text?: string; message?: string };
          if (event === "token" && data.text) {
            reply += data.text;
            setMessages((items) => {
              const next = [...items];
              next[next.length - 1] = { role: "assistant", content: reply };
              return next;
            });
          }
          if (event === "error") throw new Error(data.message || "Tutor unavailable");
        }
      }
      setStatus("idle");
    } catch (error) {
      if (controller.signal.aborted) {
        setStatus("idle");
        return;
      }
      const offline = typeof navigator !== "undefined" && !navigator.onLine;
      const message = offline
        ? "You appear to be offline. Your lesson is still available, but the tutor needs a connection."
        : "The tutor is unavailable right now. Please use the worked example or ask an educator for help.";
      setMessages((items) => {
        const next = [...items];
        next[next.length - 1] = { role: "assistant", content: message };
        return next;
      });
      setStatus(offline ? "offline" : "error");
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void send(input);
  }

  return (
    <section aria-labelledby="ai-tutor-title" className="mt-10 rounded-3xl border-2 border-blue-500/30 bg-blue-500/5 p-5">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 id="ai-tutor-title" className="text-2xl font-black text-blue-200">AI Tutor</h2>
          <p className="text-sm text-[var(--muted)]">Ask for a hint about {topic}. The tutor may suggest asking an educator.</p>
        </div>
        {status === "thinking" && (
          <button type="button" onClick={() => abortRef.current?.abort()} className="rounded-lg border px-3 py-2 text-sm" aria-label="Stop tutor response">
            Stop
          </button>
        )}
      </div>

      <div aria-live="polite" aria-relevant="additions text" className="mb-4 max-h-80 space-y-3 overflow-y-auto rounded-2xl bg-[var(--surface)] p-4">
        {messages.length === 0 && <p className="text-sm text-[var(--muted)]">Try “Can you explain this in smaller steps?”</p>}
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={message.role === "learner" ? "ml-8 rounded-xl bg-blue-600 p-3 text-white" : "mr-8 rounded-xl bg-[var(--surface2)] p-3"}>
            <span className="sr-only">{message.role === "learner" ? "You" : "Tutor"}: </span>
            {message.content || (status === "thinking" ? "Thinking…" : "")}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {(status === "offline" || status === "error") && (
        <p role="status" className="mb-3 rounded-lg border border-yellow-400/40 bg-yellow-400/10 p-3 text-sm text-yellow-100">
          {status === "offline" ? "Tutor paused while you are offline." : "Tutor connection paused. Your lesson is still available."}
        </p>
      )}

      <form onSubmit={submit} className="flex flex-col gap-3 sm:flex-row">
        <label htmlFor="tutor-question" className="sr-only">Ask the AI tutor a question</label>
        <input
          id="tutor-question"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          maxLength={600}
          disabled={status === "thinking"}
          placeholder="Ask for a hint…"
          className="min-w-0 flex-1 rounded-xl border bg-[var(--surface)] px-4 py-3"
        />
        <button type="submit" disabled={!input.trim() || status === "thinking"} className="rounded-xl bg-blue-600 px-6 py-3 font-bold text-white disabled:opacity-50">
          Ask
        </button>
      </form>
      <p className="mt-2 text-xs text-[var(--muted)]">Do not share your phone number, email address, ID number, or home address.</p>
    </section>
  );
}
