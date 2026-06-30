"use client"

import React from 'react'
import { EarconName } from '../../lib/grade-r/types'
import { playEarcon } from '../../lib/grade-r/earcons'

type ContextValue = {
  enabled: boolean
  setEnabled: (v: boolean) => void
  play: (name: EarconName) => void
}

const EarconContext = React.createContext<ContextValue | null>(null)

export const EarconProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [enabled, setEnabled] = React.useState(false)

  const play = React.useCallback((name: EarconName) => {
    if (!enabled) return
    // must be user-initiated in browsers; callers should invoke from interaction
    playEarcon(name)
  }, [enabled])

  return (
    <EarconContext.Provider value={{ enabled, setEnabled, play }}>
      {children}
    </EarconContext.Provider>
  )
}

export function useEarcons() {
  const ctx = React.useContext(EarconContext)
  if (!ctx) throw new Error('useEarcons must be used within EarconProvider')
  return ctx
}
