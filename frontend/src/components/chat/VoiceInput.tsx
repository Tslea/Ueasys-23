/**
 * Voice Input Component
 * 
 * Records audio from microphone and sends to backend for transcription.
 * Supports push-to-talk and toggle recording modes.
 */

import { useState, useRef, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, Square, Loader2 } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface VoiceInputProps {
  onTranscription: (text: string) => void
  onRecordingStart?: () => void
  onRecordingEnd?: () => void
  disabled?: boolean
  mode?: 'toggle' | 'push-to-talk'
  className?: string
}

interface AudioVisualizerProps {
  audioLevel: number
  isRecording: boolean
}

// Audio level visualizer
const AudioVisualizer = ({ audioLevel, isRecording }: AudioVisualizerProps) => {
  const bars = 5
  
  return (
    <div className="flex items-center justify-center gap-1 h-8">
      {Array.from({ length: bars }).map((_, i) => {
        const baseHeight = 8
        const maxHeight = 32
        const threshold = (i + 1) / bars
        const height = isRecording && audioLevel > threshold * 0.3
          ? baseHeight + (maxHeight - baseHeight) * audioLevel * ((bars - i) / bars)
          : baseHeight
        
        return (
          <motion.div
            key={i}
            className="w-1 rounded-full bg-neon-purple"
            animate={{
              height,
              opacity: isRecording ? 0.6 + audioLevel * 0.4 : 0.3
            }}
            transition={{ duration: 0.1 }}
          />
        )
      })}
    </div>
  )
}

export default function VoiceInput({
  onTranscription,
  onRecordingStart,
  onRecordingEnd,
  disabled = false,
  mode = 'toggle',
  className = ''
}: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const [error, setError] = useState<string | null>(null)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording()
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [])

  // Audio level monitoring
  const startAudioLevelMonitoring = useCallback((stream: MediaStream) => {
    audioContextRef.current = new AudioContext()
    analyserRef.current = audioContextRef.current.createAnalyser()
    const source = audioContextRef.current.createMediaStreamSource(stream)
    source.connect(analyserRef.current)
    analyserRef.current.fftSize = 256
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
    
    const updateLevel = () => {
      if (!analyserRef.current) return
      analyserRef.current.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      setAudioLevel(average / 255)
      animationFrameRef.current = requestAnimationFrame(updateLevel)
    }
    
    updateLevel()
  }, [])

  const stopAudioLevelMonitoring = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    setAudioLevel(0)
  }, [])

  const startRecording = useCallback(async () => {
    try {
      setError(null)
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      })
      
      streamRef.current = stream
      audioChunksRef.current = []
      
      // Start audio level monitoring
      startAudioLevelMonitoring(stream)
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') 
          ? 'audio/webm' 
          : 'audio/mp4'
      })
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = () => {
        processRecording()
      }
      
      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start(100) // Collect data every 100ms
      
      setIsRecording(true)
      onRecordingStart?.()
      
    } catch (err) {
      console.error('Failed to start recording:', err)
      setError('Microphone access denied')
    }
  }, [onRecordingStart, startAudioLevelMonitoring])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      
      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
      
      stopAudioLevelMonitoring()
      setIsRecording(false)
      onRecordingEnd?.()
    }
  }, [isRecording, onRecordingEnd, stopAudioLevelMonitoring])

  const processRecording = useCallback(async () => {
    if (audioChunksRef.current.length === 0) return
    
    setIsProcessing(true)
    
    try {
      const audioBlob = new Blob(audioChunksRef.current, {
        type: mediaRecorderRef.current?.mimeType || 'audio/webm'
      })
      
      // Check minimum size (avoid sending empty/very short recordings)
      if (audioBlob.size < 1000) {
        setError('Recording too short')
        setIsProcessing(false)
        return
      }
      
      // Send to backend for transcription
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      
      const response = await fetch(`${API_BASE}/api/v1/voice/transcribe`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Transcription failed')
      }
      
      const data = await response.json()
      
      if (data.text && data.text.trim()) {
        onTranscription(data.text.trim())
      } else {
        setError('No speech detected')
      }
      
    } catch (err) {
      console.error('Transcription error:', err)
      setError(err instanceof Error ? err.message : 'Transcription failed')
    } finally {
      setIsProcessing(false)
      audioChunksRef.current = []
    }
  }, [onTranscription])

  // Toggle mode handler
  const handleToggleClick = useCallback(() => {
    if (disabled || isProcessing) return
    
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }, [disabled, isProcessing, isRecording, startRecording, stopRecording])

  // Push-to-talk handlers
  const handlePushStart = useCallback(() => {
    if (disabled || isProcessing || isRecording) return
    startRecording()
  }, [disabled, isProcessing, isRecording, startRecording])

  const handlePushEnd = useCallback(() => {
    if (isRecording) {
      stopRecording()
    }
  }, [isRecording, stopRecording])

  // Clear error after 3 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [error])

  return (
    <div className={`relative flex flex-col items-center gap-3 ${className}`}>
      {/* Audio Visualizer */}
      <AnimatePresence>
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
          >
            <AudioVisualizer audioLevel={audioLevel} isRecording={isRecording} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Button */}
      <motion.button
        onClick={mode === 'toggle' ? handleToggleClick : undefined}
        onMouseDown={mode === 'push-to-talk' ? handlePushStart : undefined}
        onMouseUp={mode === 'push-to-talk' ? handlePushEnd : undefined}
        onMouseLeave={mode === 'push-to-talk' && isRecording ? handlePushEnd : undefined}
        onTouchStart={mode === 'push-to-talk' ? handlePushStart : undefined}
        onTouchEnd={mode === 'push-to-talk' ? handlePushEnd : undefined}
        disabled={disabled || isProcessing}
        whileTap={{ scale: 0.95 }}
        className={`
          relative p-6 rounded-full transition-all duration-300
          ${isRecording 
            ? 'bg-red-500/20 border-2 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.5)]' 
            : 'bg-neon-purple/10 border-2 border-neon-purple/30 hover:border-neon-purple/50 hover:bg-neon-purple/20'
          }
          ${disabled || isProcessing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        {/* Pulsing ring when recording */}
        {isRecording && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-red-500"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
        
        {/* Icon */}
        {isProcessing ? (
          <Loader2 className="w-8 h-8 text-neon-purple animate-spin" />
        ) : isRecording ? (
          mode === 'toggle' ? (
            <Square className="w-8 h-8 text-red-500" />
          ) : (
            <Mic className="w-8 h-8 text-red-500" />
          )
        ) : (
          <Mic className="w-8 h-8 text-neon-purple" />
        )}
      </motion.button>

      {/* Status Text */}
      <motion.p
        className="text-sm font-mono text-white/50 h-5"
        animate={{ opacity: error ? 1 : 0.5 }}
      >
        {error ? (
          <span className="text-red-400">{error}</span>
        ) : isProcessing ? (
          'Processing...'
        ) : isRecording ? (
          mode === 'toggle' ? 'Tap to stop' : 'Release to send'
        ) : (
          mode === 'toggle' ? 'Tap to speak' : 'Hold to speak'
        )}
      </motion.p>
    </div>
  )
}
