import React from 'react'

interface DashboardPanelProps {
  learner?: { nickname?: string; grade?: number } | null;
  onStartLesson?: () => void;
  onStartDiag?: () => void;
}

interface DiagnosticPanelProps {
  learner?: { nickname?: string; grade?: number } | null;
  onBack?: () => void;
}

interface LessonPanelProps {
  onComplete?: () => void;
  onBack?: () => void;
}

export function DashboardPanel({ learner, onStartLesson }: DashboardPanelProps) {
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome, {learner?.nickname || "TestUser"}!</p>
      <p>Mastery estimates and adaptive check-ins are temporarily unavailable while the question bank is reviewed.</p>
      <button onClick={onStartLesson}>Start lesson</button>
    </div>
  )
}

export function DiagnosticPanel({ onBack }: DiagnosticPanelProps) {
  return (
    <div>
      <h2>Check-in unavailable</h2>
      <p>The question bank is being rebuilt and independently reviewed.</p>
      <button onClick={onBack}>Back</button>
    </div>
  )
}

export function LessonPanel({ onComplete, onBack }: LessonPanelProps) {
  return (
    <div>
      <h2>Lesson</h2>
      <button onClick={onComplete}>Complete Lesson</button>
      <button onClick={onBack}>Back</button>
    </div>
  )
}

export default function FeaturePanels() {
  return (
    <div>
      <DashboardPanel />
      <DiagnosticPanel />
    </div>
  )
}
