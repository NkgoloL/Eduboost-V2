"use client"

import React from 'react'
import { useEarcons } from './EarconProvider'
import { playEarcon } from '../../lib/grade-r/earcons'
import { EarconName } from '../../lib/grade-r/types'

export const EarconButton: React.FC<{ name: EarconName; label?: string }> = ({ name, label }) => {
  const { play, enabled, setEnabled } = useEarcons()

  const handleClick = () => {
    // if user hasn't enabled, turn on (user action)
    if (!enabled) {
      setEnabled(true)
      try { playEarcon(name) } catch (e) { /* degrade silently */ }
      return
    }
    // play via provider when already enabled
    try { play(name) } catch (e) { /* degrade silently */ }
  }

  return (
    <button
      aria-label={label || `Play sound ${name}`}
      onClick={handleClick}
      style={{ minWidth: 64, minHeight: 64, padding: 12, borderRadius: 12 }}
    >
      {label || name}
    </button>
  )
}
