"use client"

import { useCallback, useState } from 'react'
import { askTutorClient } from '../lib/tutor/client'
import type { TutorRequest, TutorResponse } from '../lib/tutor/types'

export function useTutorStream() {
  const [response, setResponse] = useState<TutorResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const sendTutorRequest = useCallback(async (request: TutorRequest) => {
    setLoading(true)
    setError(null)
    try {
      const result = await askTutorClient(request)
      setResponse(result)
      return result
    } catch (caught) {
      const nextError = caught instanceof Error ? caught : new Error('Tutor request failed')
      setError(nextError)
      throw nextError
    } finally {
      setLoading(false)
    }
  }, [])

  return { response, loading, error, sendTutorRequest }
}
