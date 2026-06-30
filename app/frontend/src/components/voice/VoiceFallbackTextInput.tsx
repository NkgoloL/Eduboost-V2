import React from 'react'

type Props = {
  value?: string
  onChange?: (v: string) => void
}

export default function VoiceFallbackTextInput({ value = '', onChange }: Props) {
  return (
    <div>
      <label htmlFor="voice-fallback">Text fallback</label>
      <textarea id="voice-fallback" value={value} onChange={(e) => onChange?.(e.target.value)} />
    </div>
  )
}
