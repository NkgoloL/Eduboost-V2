const PII_PATTERNS: Array<{ name: string; pattern: RegExp; replacement: string }> = [
  { name: "email", pattern: /[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g, replacement: "[email]" },
  { name: "za-id", pattern: /\b\d{13}\b/g, replacement: "[za-id]" },
  { name: "phone", pattern: /(\+27|0)[6-8]\d[\s\-]?\d{3}[\s\-]?\d{4}/g, replacement: "[phone]" },
  { name: "uuid", pattern: /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, replacement: "[id]" },
];

export function scrubPii(value: string): string {
  return PII_PATTERNS.reduce((acc, { pattern, replacement }) => acc.replace(pattern, replacement), value);
}

export function scrubPiiFromObject(obj: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [
      k,
      typeof v === "string" ? scrubPii(v) : v,
    ])
  );
}

export interface MonitoringEvent {
  message: string;
  level: "error" | "warning" | "info";
  tags?: Record<string, string>;
  extra?: Record<string, unknown>;
}

type MonitoringBackend = {
  captureEvent: (event: MonitoringEvent) => void;
  captureException: (error: Error, context?: Record<string, unknown>) => void;
};

let _backend: MonitoringBackend | null = null;

export function registerMonitoringBackend(backend: MonitoringBackend) {
  _backend = backend;
}

export function captureException(error: Error, context?: Record<string, unknown>) {
  const scrubbedMessage = scrubPii(error.message);
  const scrubbedContext = context ? scrubPiiFromObject(context as Record<string, unknown>) : undefined;

  if (_backend) {
    const safeError = new Error(scrubbedMessage);
    safeError.stack = error.stack;
    _backend.captureException(safeError, scrubbedContext);
  } else {
    if (process.env.NODE_ENV !== "production") {
      console.error("[monitoring]", scrubbedMessage, scrubbedContext ?? "");
    }
  }
}

export function captureEvent(event: MonitoringEvent) {
  const scrubbedEvent: MonitoringEvent = {
    ...event,
    message: scrubPii(event.message),
    tags: event.tags ? (scrubPiiFromObject(event.tags as Record<string, unknown>) as Record<string, string>) : undefined,
    extra: event.extra ? scrubPiiFromObject(event.extra) : undefined,
  };

  if (_backend) {
    _backend.captureEvent(scrubbedEvent);
  } else if (process.env.NODE_ENV !== "production") {
    const fallback = scrubbedEvent.level === "error" ? console.error : console.warn;
    fallback(`[monitoring:${scrubbedEvent.level}]`, scrubbedEvent.message);
  }
}

export function captureTestEvent() {
  captureEvent({
    level: "info",
    message: "synthetic-test-event: monitoring pipeline verified",
    tags: { source: "instrumentation-check" },
  });
}
