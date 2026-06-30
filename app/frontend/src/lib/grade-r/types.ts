export type PhonicsSegment = {
  id: string
  text: string
  startMs: number
  endMs: number
  emphasis?: 'normal' | 'strong'
}

export type EarconName = 'success' | 'retry' | 'start' | 'complete' | 'attention'
