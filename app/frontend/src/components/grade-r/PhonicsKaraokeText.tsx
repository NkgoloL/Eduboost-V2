"use client"

import React from 'react'
import { PhonicsSegment } from '../../lib/grade-r/types'

export const PhonicsKaraokeText: React.FC<{
  segments: PhonicsSegment[]
  activeIndex?: number
  reducedMotion?: boolean
}> = ({ segments, activeIndex = 0, reducedMotion = false }) => {
  return (
    <div role="group" aria-label="Phonics karaoke" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {segments.map((s, i) => {
        const isActive = i === activeIndex
        return (
          <span
            key={s.id}
            aria-current={isActive ? 'true' : undefined}
            data-testid={`segment-${i}`}
            style={{
              padding: '8px 12px',
              borderRadius: 8,
              background: isActive ? '#fffbcc' : 'transparent',
              transition: reducedMotion ? 'none' : 'background 150ms ease',
              fontWeight: s.emphasis === 'strong' ? 700 : 400,
              minWidth: 24,
              textAlign: 'center'
            }}
          >
            {s.text}
          </span>
        )
      })}
    </div>
  )
}
