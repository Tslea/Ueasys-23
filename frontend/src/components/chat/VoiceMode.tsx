/**
 * Voice Mode Component
 * 
 * Full voice-only interface for chat - no text input/output.
 * User speaks → Transcription → LLM → TTS → Audio playback
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Mic, Volume2, VolumeX, Loader2, 
  MessageSquare, Radio, Sparkles,
  AlertCircle
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface VoiceModeProps {
  characterId: string
  characterName: string
  onTextFallback?: () => void
  className?: string
}

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking' | 'error'

interface ConversationTurn {
  id: string
  userText: string
  assistantText: string
  timestamp: Date
}

export default function VoiceMode({
  characterId,
  characterName,
  onTextFallback,
  className = ''
}: VoiceModeProps) {
  const [state, setState] = useState<VoiceState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [isMuted, setIsMuted] = useState(false)
  const [lastTranscription, setLastTranscription] = useState<string | null>(null)
  const [lastResponse, setLastResponse] = useState<string | null>(null)
  const [conversationHistory, setConversationHistory] = useState<ConversationTurn[]>([])
  const [audioLevel, setAudioLevel] = useState(0)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanup()
    }
  }, [])

  const cleanup = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
    if (audioRef.current) {
      audioRef.current.pause()
    }
  }, [])

  // Start listening
  const startListening = useCallback(async () => {
    try {
      setError(null)
      setState('listening')
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      })
      
      streamRef.current = stream
      audioChunksRef.current = []
      
      // Audio level monitoring
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)
      analyserRef.current.fftSize = 256
      
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
      
      const updateLevel = () => {
        if (!analyserRef.current || state !== 'listening') return
        analyserRef.current.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        setAudioLevel(average / 255)
        animationFrameRef.current = requestAnimationFrame(updateLevel)
      }
      updateLevel()
      
      // Setup MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      })
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }
      
      mediaRecorder.onstop = () => processVoiceInput()
      
      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start(100)
      
    } catch (err) {
      console.error('Microphone error:', err)
      setError('Microphone access denied')
      setState('error')
    }
  }, [])

  // Stop listening
  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && state === 'listening') {
      mediaRecorderRef.current.stop()
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
        audioContextRef.current = null
      }
      
      setAudioLevel(0)
    }
  }, [state])

  // Process voice input: Transcribe → Chat → TTS → Play
  const processVoiceInput = useCallback(async () => {
    if (audioChunksRef.current.length === 0) {
      setState('idle')
      return
    }
    
    setState('processing')
    
    try {
      // 1. Transcribe audio
      const audioBlob = new Blob(audioChunksRef.current, {
        type: mediaRecorderRef.current?.mimeType || 'audio/webm'
      })
      
      if (audioBlob.size < 1000) {
        setError('Recording too short')
        setState('idle')
        return
      }
      
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      
      const transcribeResponse = await fetch(`${API_BASE}/api/v1/voice/transcribe`, {
        method: 'POST',
        body: formData
      })
      
      if (!transcribeResponse.ok) throw new Error('Transcription failed')
      
      const transcribeData = await transcribeResponse.json()
      const userText = transcribeData.text?.trim()
      
      if (!userText) {
        setError('No speech detected')
        setState('idle')
        return
      }
      
      setLastTranscription(userText)
      
      // 2. Send to chat endpoint
      const chatResponse = await fetch(`${API_BASE}/api/v1/chat/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: characterId,
          message: userText,
          context: conversationHistory.slice(-5).map(turn => ([
            { role: 'user', content: turn.userText },
            { role: 'assistant', content: turn.assistantText }
          ])).flat()
        })
      })
      
      if (!chatResponse.ok) throw new Error('Chat request failed')
      
      const chatData = await chatResponse.json()
      const assistantText = chatData.response
      
      setLastResponse(assistantText)
      
      // Add to history
      setConversationHistory(prev => [...prev, {
        id: `turn-${Date.now()}`,
        userText,
        assistantText,
        timestamp: new Date()
      }])
      
      // 3. Generate TTS and play
      if (!isMuted) {
        setState('speaking')
        
        const ttsResponse = await fetch(`${API_BASE}/api/v1/voice/speak`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: assistantText,
            character_id: characterId
          })
        })
        
        if (!ttsResponse.ok) throw new Error('TTS failed')
        
        const audioBlob = await ttsResponse.blob()
        const audioUrl = URL.createObjectURL(audioBlob)
        
        audioRef.current = new Audio(audioUrl)
        audioRef.current.onended = () => {
          setState('idle')
          URL.revokeObjectURL(audioUrl)
        }
        audioRef.current.onerror = () => {
          setState('idle')
          setError('Audio playback failed')
        }
        
        await audioRef.current.play()
      } else {
        setState('idle')
      }
      
    } catch (err) {
      console.error('Voice processing error:', err)
      setError(err instanceof Error ? err.message : 'Processing failed')
      setState('error')
      
      // Auto-recover after error
      setTimeout(() => {
        if (state === 'error') setState('idle')
      }, 3000)
    } finally {
      audioChunksRef.current = []
    }
  }, [characterId, conversationHistory, isMuted, state])

  // Main button handler
  const handleMainButton = useCallback(() => {
    if (state === 'listening') {
      stopListening()
    } else if (state === 'idle' || state === 'error') {
      startListening()
    } else if (state === 'speaking' && audioRef.current) {
      audioRef.current.pause()
      setState('idle')
    }
  }, [state, startListening, stopListening])

  // Clear error after delay
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  // Get status text
  const getStatusText = () => {
    switch (state) {
      case 'listening': return 'Listening...'
      case 'processing': return 'Processing...'
      case 'speaking': return `${characterName} is speaking...`
      case 'error': return error || 'Error occurred'
      default: return 'Tap to speak'
    }
  }

  // Get button icon
  const getButtonIcon = () => {
    switch (state) {
      case 'listening': return <Radio className="w-12 h-12 text-red-500" />
      case 'processing': return <Loader2 className="w-12 h-12 text-neon-purple animate-spin" />
      case 'speaking': return <Volume2 className="w-12 h-12 text-neon-gold" />
      case 'error': return <AlertCircle className="w-12 h-12 text-red-500" />
      default: return <Mic className="w-12 h-12 text-neon-purple" />
    }
  }

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      {/* Last exchange display */}
      <AnimatePresence>
        {(lastTranscription || lastResponse) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full max-w-md mb-8 space-y-4"
          >
            {lastTranscription && (
              <div className="text-right">
                <p className="inline-block px-4 py-2 rounded-2xl rounded-tr-sm bg-neon-purple/20 text-white/80 text-sm">
                  {lastTranscription}
                </p>
              </div>
            )}
            {lastResponse && state !== 'processing' && (
              <div className="text-left">
                <p className="inline-block px-4 py-2 rounded-2xl rounded-tl-sm bg-white/10 text-white/80 text-sm max-w-xs">
                  {lastResponse.length > 150 ? lastResponse.substring(0, 150) + '...' : lastResponse}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Audio level visualization */}
      <AnimatePresence>
        {state === 'listening' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="mb-6 flex items-center justify-center gap-1 h-16"
          >
            {Array.from({ length: 7 }).map((_, i) => (
              <motion.div
                key={i}
                className="w-2 rounded-full bg-neon-purple"
                animate={{
                  height: 16 + audioLevel * 48 * Math.sin((i / 7) * Math.PI),
                  opacity: 0.5 + audioLevel * 0.5
                }}
                transition={{ duration: 0.1 }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Speaking animation */}
      <AnimatePresence>
        {state === 'speaking' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mb-6"
          >
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="flex items-center gap-2 text-neon-gold"
            >
              <Sparkles className="w-5 h-5" />
              <span className="text-sm font-mono">{characterName}</span>
              <Sparkles className="w-5 h-5" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Voice Button */}
      <motion.button
        onClick={handleMainButton}
        disabled={state === 'processing'}
        whileTap={{ scale: 0.95 }}
        className={`
          relative p-8 rounded-full transition-all duration-500
          ${state === 'listening' 
            ? 'bg-red-500/20 border-4 border-red-500 shadow-[0_0_60px_rgba(239,68,68,0.6)]' 
            : state === 'speaking'
            ? 'bg-neon-gold/20 border-4 border-neon-gold shadow-[0_0_60px_rgba(251,191,36,0.6)]'
            : state === 'error'
            ? 'bg-red-500/10 border-4 border-red-500/50'
            : 'bg-neon-purple/10 border-4 border-neon-purple/30 hover:border-neon-purple/60 hover:shadow-[0_0_40px_rgba(168,85,247,0.4)]'
          }
          ${state === 'processing' ? 'opacity-70 cursor-wait' : 'cursor-pointer'}
        `}
      >
        {/* Pulsing rings */}
        {state === 'listening' && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-red-500"
              animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-red-500"
              animate={{ scale: [1, 1.3], opacity: [0.4, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }}
            />
          </>
        )}
        
        {state === 'speaking' && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-neon-gold"
            animate={{ scale: [1, 1.2], opacity: [0.5, 0] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
        
        {getButtonIcon()}
      </motion.button>

      {/* Status text */}
      <motion.p
        className={`mt-6 text-lg font-mono ${
          state === 'error' ? 'text-red-400' : 'text-white/50'
        }`}
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: state === 'listening' ? Infinity : 0 }}
      >
        {getStatusText()}
      </motion.p>

      {/* Controls */}
      <div className="mt-8 flex items-center gap-6">
        {/* Mute toggle */}
        <button
          onClick={() => setIsMuted(!isMuted)}
          className={`p-3 rounded-full transition-all ${
            isMuted 
              ? 'bg-red-500/20 text-red-400' 
              : 'bg-white/5 text-white/40 hover:text-white/60'
          }`}
        >
          {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
        </button>
        
        {/* Text mode fallback */}
        {onTextFallback && (
          <button
            onClick={onTextFallback}
            className="p-3 rounded-full bg-white/5 text-white/40 hover:text-white/60 transition-all"
          >
            <MessageSquare className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Instructions */}
      <p className="mt-8 text-xs font-mono text-white/30 text-center max-w-xs">
        {state === 'idle' && 'Tap the orb and speak to begin your conversation'}
        {state === 'listening' && 'Tap again when finished speaking'}
      </p>
    </div>
  )
}
