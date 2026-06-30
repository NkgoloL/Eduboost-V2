import React, { useState, useEffect } from 'react'
import { detectVoiceSupport } from '@/lib/voice/capability'
import { getGuardianConsent, setGuardianConsent as persistGuardianConsent } from '@/lib/voice/consent'
import { canUseVoice } from '@/lib/voice/guardrails'

type Props = { learnerId?: string }

export default function VoiceInputShell({ learnerId }: Props) {
  const [cap, setCap] = useState(() => detectVoiceSupport())
  const [consent, setConsent] = useState(() => getGuardianConsent(learnerId).consented)
  const [online, setOnline] = useState(() => typeof navigator !== 'undefined' ? navigator.onLine : true)
  const [listening, setListening] = useState(false)

  useEffect(() => {
    function handleOnline() { setOnline(true) }
    function handleOffline() { setOnline(false) }
    if (typeof window !== 'undefined') {
      window.addEventListener('online', handleOnline)
      window.addEventListener('offline', handleOffline)
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('online', handleOnline)
        window.removeEventListener('offline', handleOffline)
      }
    }
  }, [])

  useEffect(() => {
    // reflect updated consent in local storage when changed
    if (learnerId) persistGuardianConsent(learnerId, consent)
  }, [consent, learnerId])

  const guard = canUseVoice(cap, consent, online)

  // no-op local setter; persistence handled in effect

  function handleStartClick() {
    // Explicit user action only — do not request permission on mount.
    if (!guard.allowed) return
    setListening(true)
    // Start recognition only when supported; leave implementation minimal
    // Actual SpeechRecognition usage should be initiated here by the platform
    // on user action. We deliberately do not persist any audio.
  }

  return (
    <div>
      <div>Voice support: {cap.supported ? 'yes' : 'no'}</div>
      <div>Online: {online ? 'yes' : 'no'}</div>
      <div>
        Guardian consent:
        <button onClick={() => setConsent(!consent)}>{consent ? 'Revoke' : 'Give consent'}</button>
      </div>
      <div>
        <button disabled={!guard.allowed || listening} onClick={handleStartClick}>Start Voice Input</button>
        {listening && <div>Listening...</div>}
      </div>
    </div>
  )
}
