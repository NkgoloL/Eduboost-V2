import { PhonicsSegment } from './types'

// Very small helper to create segments for tests and demo. In real content this
// would come from CMS-authored timings.
export function makeSegmentsFromWords(text: string, durationMs = 2000): PhonicsSegment[] {
  const words = text.split(/\s+/).filter(Boolean)
  const per = Math.max(200, Math.floor(durationMs / words.length))
  let t = 0
  return words.map((w, i) => {
    const seg: PhonicsSegment = {
      id: `seg-${i}`,
      text: w,
      startMs: t,
      endMs: t + per,
      emphasis: 'normal',
    }
    t += per
    return seg
  })
}
