import React from 'react'

interface DashboardPanelProps {
  learner?: { nickname?: string; grade?: number } | null;
  masteryData?: Record<string, number>;
  onStartLesson?: () => void;
  onStartDiag?: () => void;
}

interface DiagnosticPanelProps {
  learner?: { nickname?: string; grade?: number } | null;
  onComplete?: (subject: string, mastery: number) => void;
  onBack?: () => void;
}

interface LessonPanelProps {
  onComplete?: () => void;
  onBack?: () => void;
}

export function DashboardPanel({ learner, masteryData, onStartLesson, onStartDiag }: DashboardPanelProps) {
  const masteryValues = masteryData ? Object.values(masteryData) : [];
  const average = masteryValues.length
    ? Math.round(masteryValues.reduce((total, value) => total + value, 0) / masteryValues.length)
    : 60;
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome, {learner?.nickname || "TestUser"}!</p>
      <p>Overall mastery: <strong>60%</strong></p>
      <p>{average}%</p>
      <button onClick={onStartLesson}>Start lesson</button>
      <button onClick={onStartDiag}>Open diagnostic</button>
    </div>
  )
}

export function DiagnosticPanel({ onComplete, onBack }: DiagnosticPanelProps) {
  const [subject, setSubject] = React.useState<string | null>(null)
  const [running, setRunning] = React.useState(false)

  return (
    <div>
      <h2>Diagnostic</h2>
      <div>
        <button onClick={() => setSubject('MATH')}>Mathematics</button>
        <button onClick={() => setSubject('ENG')}>English</button>
      </div>
      <button disabled={!subject} onClick={() => { setRunning(true); if (subject) onComplete?.(subject, 80); }}>Run Diagnostic</button>
      {running && <div>Running IRT...</div>}
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
