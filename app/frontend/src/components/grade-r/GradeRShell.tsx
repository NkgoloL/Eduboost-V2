"use client"

import React from 'react'
import { PhonicsKaraokeText } from './PhonicsKaraokeText'
import { EarconButton } from './EarconButton'
import { EarconProvider } from './EarconProvider'
import { makeSegmentsFromWords } from '../../lib/grade-r/phonics'

export const GradeRShell: React.FC<{ text?: string }> = ({ text = 'a ba ca' }) => {
  const segments = React.useMemo(() => makeSegmentsFromWords(text, 1600), [text])
  const [active, setActive] = React.useState(0)

  const next = () => setActive((s) => Math.min(segments.length - 1, s + 1))
  const prev = () => setActive((s) => Math.max(0, s - 1))

  return (
    <EarconProvider>
      <main style={{ padding: 16 }}>
        <header>
          <h1 style={{ fontSize: 24 }}>Grade R mode</h1>
        </header>
        <section style={{ marginTop: 12 }}>
          <PhonicsKaraokeText segments={segments} activeIndex={active} />
        </section>

        <nav style={{ marginTop: 18, display: 'flex', gap: 12 }}>
          <button aria-label="Previous" onClick={prev} style={{ minWidth: 64, minHeight: 64 }}>Prev</button>
          <button aria-label="Next" onClick={next} style={{ minWidth: 64, minHeight: 64 }}>Next</button>
          <EarconButton name="start" label="Play" />
        </nav>
      </main>
    </EarconProvider>
  )
}
