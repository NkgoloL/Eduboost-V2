import React from 'react'

export function DashboardPanel() {
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome, TestUser!</p>
      <p>Overall mastery: <strong>60%</strong></p>
      <button onClick={() => {}}>Start lesson</button>
      <button onClick={() => {}}>Back</button>
    </div>
  )
}

export function DiagnosticPanel() {
  const [subject, setSubject] = React.useState(null)
  const [running, setRunning] = React.useState(false)

  return (
    <div>
      <h2>Diagnostic</h2>
      <div>
        <button onClick={() => setSubject('MATH')}>Mathematics</button>
        <button onClick={() => setSubject('ENG')}>English</button>
      </div>
      <button disabled={!subject} onClick={() => setRunning(true)}>Run Diagnostic</button>
      {running && <div>Running IRT...</div>}
      <button onClick={() => {}}>Back</button>
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
