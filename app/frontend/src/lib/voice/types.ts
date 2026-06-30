export type VoiceCapability = {
  supported: boolean
  recognitionApi: 'webkit' | 'standard' | null
}

export type ConsentState = {
  learnerId?: string
  consented: boolean
}
