import type { TutorAuditEvent } from './types'

const auditEvents: TutorAuditEvent[] = []

export async function auditEventStub(event: Record<string, unknown>) {
  try {
    const rest = { ...event } as Record<string, unknown>
    // Log for server operators; tests do not rely on console output.
    // eslint-disable-next-line no-console
    console.info('[audit] tutor event', JSON.stringify(rest))
    // keep in-memory trail for tests
    const lessonIdVal = rest['lessonId'] ?? rest['lesson_id']
    if (typeof lessonIdVal === 'string') {
      const evt = typeof rest['event'] === 'string' ? rest['event'] as string : typeof rest['eventType'] === 'string' ? rest['eventType'] as string : 'event'
      auditEvents.push({ lessonId: lessonIdVal, eventType: evt, timestamp: new Date().toISOString(), safe: true, metadata: {} })
    }
  } catch (e) {
    // swallow
  }
}

export function recordTutorAuditEvent(event: TutorAuditEvent) {
  auditEvents.push(event)
}

export function getTutorAuditEvents(): TutorAuditEvent[] {
  return [...auditEvents]
}

export function clearTutorAuditEvents() {
  auditEvents.length = 0
}
