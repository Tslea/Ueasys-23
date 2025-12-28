/**
 * Voice Output Component
 * 
 * Plays audio responses from the character using TTS.
 * Handles audio playback with visual feedback.
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Volume2, VolumeX, Loader2, Play, Pause, RotateCcw } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface VoiceOutputProps {
  text: string
  characterId: string
  autoPlay?: boolean
  onPlayStart?: () => void
  onPlayEnd?: () => void
  onError?: (error: string) => void
  className?: string
}

interface AudioWaveformProps {
  isPlaying: boolean
  progress: number
}

// Animated waveform during playback
const AudioWaveform = ({ isPlaying, progress }: AudioWaveformProps) => {
  const bars = 20
  
  return (
    <div className="flex items-center justify-center gap-0.5 h-12 w-full max-w-xs mx-auto">
      {Array.from({ length: bars }).map((_, i) => {
        const isPast = i / bars < progress
        const isCurrent = Math.abs(i / bars - progress) < 0.1
        
        return (
          <motion.div
            key={i}
            className={`w-1 rounded-full ${isPast ? 'bg-neon-purple' : 'bg-white/20'}`}
            animate={{
              height: isPlaying && isCurrent
                ? [8, 24, 16, 32, 12, 28, 8]
                : isPast ? 16 : 8,
              opacity: isPast ? 1 : 0.4
            }}
            transition={{
              duration: isPlaying && isCurrent ? 0.5 : 0.2,
              repeat: isPlaying && isCurrent ? Infinity : 0,
              repeatType: 'reverse'
            }}
          />
        )
      })}
    </div>
  )
}

export default function VoiceOutput({
  text,
  characterId,
  autoPlay = true,
  onPlayStart,
  onPlayEnd,
  onError,
  className = ''
}: VoiceOutputProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [progress, setProgress] = useState(0)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [hasError, setHasError] = useState(false)
  
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Fetch audio from TTS endpoint
  const fetchAudio = useCallback(async () => {
    if (!text || !characterId) return
    
    setIsLoading(true)
    setHasError(false)
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/voice/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          character_id: characterId
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to generate speech')
      }
      
      const audioBlob = await response.blob()
      const url = URL.createObjectURL(audioBlob)
      
      // Cleanup previous URL
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }
      
      setAudioUrl(url)
      
      // Auto-play if enabled
      if (autoPlay) {
        playAudio(url)
      }
      
    } catch (err) {
      console.error('TTS error:', err)
      setHasError(true)
      onError?.(err instanceof Error ? err.message : 'TTS failed')
    } finally {
      setIsLoading(false)
    }
  }, [text, characterId, autoPlay, onError])

  // Play audio
  const playAudio = useCallback((url?: string) => {
    const audioSrc = url || audioUrl
    if (!audioSrc) return
    
    if (!audioRef.current) {
      audioRef.current = new Audio()
    }
    
    audioRef.current.src = audioSrc
    audioRef.current.muted = isMuted
    
    audioRef.current.onplay = () => {
      setIsPlaying(true)
      onPlayStart?.()
      
      // Progress tracking
      progressIntervalRef.current = setInterval(() => {
        if (audioRef.current) {
          const prog = audioRef.current.currentTime / audioRef.current.duration
          setProgress(isNaN(prog) ? 0 : prog)
        }
      }, 100)
    }
    
    audioRef.current.onended = () => {
      setIsPlaying(false)
      setProgress(1)
      onPlayEnd?.()
      
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
      }
    }
    
    audioRef.current.onerror = () => {
      setIsPlaying(false)
      setHasError(true)
      onError?.('Audio playback failed')
    }
    
    audioRef.current.play().catch(err => {
      console.error('Playback error:', err)
      setHasError(true)
    })
  }, [audioUrl, isMuted, onPlayStart, onPlayEnd, onError])

  // Pause audio
  const pauseAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      setIsPlaying(false)
      
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
      }
    }
  }, [])

  // Toggle play/pause
  const togglePlayPause = useCallback(() => {
    if (isPlaying) {
      pauseAudio()
    } else if (audioUrl) {
      audioRef.current?.play()
    } else {
      fetchAudio()
    }
  }, [isPlaying, audioUrl, pauseAudio, fetchAudio])

  // Toggle mute
  const toggleMute = useCallback(() => {
    setIsMuted(prev => {
      if (audioRef.current) {
        audioRef.current.muted = !prev
      }
      return !prev
    })
  }, [])

  // Replay audio
  const replay = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0
      setProgress(0)
      audioRef.current.play()
    }
  }, [])

  // Fetch audio when text changes (if autoPlay)
  useEffect(() => {
    if (autoPlay && text && characterId) {
      fetchAudio()
    }
  }, [text, characterId])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
      }
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

  // Update mute state when it changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.muted = isMuted
    }
  }, [isMuted])

  return (
    <div className={`relative ${className}`}>
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center gap-2 py-4"
          >
            <Loader2 className="w-5 h-5 text-neon-purple animate-spin" />
            <span className="text-sm font-mono text-white/50">Generating voice...</span>
          </motion.div>
        ) : hasError ? (
          <motion.div
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center gap-2 py-4"
          >
            <VolumeX className="w-5 h-5 text-red-400" />
            <span className="text-sm font-mono text-red-400">Voice unavailable</span>
            <button
              onClick={fetchAudio}
              className="p-1 rounded hover:bg-white/10 transition-colors"
            >
              <RotateCcw className="w-4 h-4 text-white/50" />
            </button>
          </motion.div>
        ) : audioUrl ? (
          <motion.div
            key="player"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-3"
          >
            {/* Waveform */}
            <AudioWaveform isPlaying={isPlaying} progress={progress} />
            
            {/* Controls */}
            <div className="flex items-center justify-center gap-4">
              {/* Play/Pause */}
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={togglePlayPause}
                className="p-3 rounded-full bg-neon-purple/20 border border-neon-purple/30 hover:bg-neon-purple/30 transition-colors"
              >
                {isPlaying ? (
                  <Pause className="w-5 h-5 text-neon-purple" />
                ) : (
                  <Play className="w-5 h-5 text-neon-purple ml-0.5" />
                )}
              </motion.button>
              
              {/* Replay */}
              <button
                onClick={replay}
                disabled={!audioUrl}
                className="p-2 rounded-full hover:bg-white/10 transition-colors disabled:opacity-30"
              >
                <RotateCcw className="w-4 h-4 text-white/50" />
              </button>
              
              {/* Mute */}
              <button
                onClick={toggleMute}
                className="p-2 rounded-full hover:bg-white/10 transition-colors"
              >
                {isMuted ? (
                  <VolumeX className="w-4 h-4 text-white/50" />
                ) : (
                  <Volume2 className="w-4 h-4 text-white/50" />
                )}
              </button>
            </div>
          </motion.div>
        ) : !autoPlay ? (
          <motion.button
            key="generate"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            whileTap={{ scale: 0.95 }}
            onClick={fetchAudio}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-neon-purple/10 border border-neon-purple/30 hover:bg-neon-purple/20 transition-colors"
          >
            <Volume2 className="w-4 h-4 text-neon-purple" />
            <span className="text-sm font-mono text-neon-purple">Play voice</span>
          </motion.button>
        ) : null}
      </AnimatePresence>
    </div>
  )
}

// Hook for managing voice output in chat
export function useVoiceOutput() {
  const [isEnabled, setIsEnabled] = useState(true)
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null)
  
  const playMessage = useCallback(async (
    messageId: string,
    text: string,
    characterId: string
  ) => {
    if (!isEnabled) return
    
    setCurrentlyPlaying(messageId)
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/voice/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, character_id: characterId })
      })
      
      if (!response.ok) throw new Error('TTS failed')
      
      const blob = await response.blob()
      const audio = new Audio(URL.createObjectURL(blob))
      
      audio.onended = () => {
        setCurrentlyPlaying(null)
        URL.revokeObjectURL(audio.src)
      }
      
      await audio.play()
      
    } catch (err) {
      console.error('Voice playback error:', err)
      setCurrentlyPlaying(null)
    }
  }, [isEnabled])
  
  return {
    isEnabled,
    setIsEnabled,
    currentlyPlaying,
    playMessage
  }
}
