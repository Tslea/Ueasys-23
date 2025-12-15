import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface EmotionIndicatorProps {
  emotion: string
  intensity: number
  description?: string
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  className?: string
}

// Emotion to color mapping with fantasy themes
const emotionColors: Record<string, { bg: string; glow: string; icon: string }> = {
  joy: { bg: 'bg-yellow-500/20', glow: 'shadow-yellow-500/50', icon: '✨' },
  happiness: { bg: 'bg-yellow-400/20', glow: 'shadow-yellow-400/50', icon: '☀️' },
  serenity: { bg: 'bg-cyan-400/20', glow: 'shadow-cyan-400/50', icon: '🌊' },
  sadness: { bg: 'bg-blue-600/20', glow: 'shadow-blue-600/50', icon: '💧' },
  melancholy: { bg: 'bg-indigo-600/20', glow: 'shadow-indigo-600/50', icon: '🌙' },
  anger: { bg: 'bg-red-600/20', glow: 'shadow-red-600/50', icon: '🔥' },
  rage: { bg: 'bg-red-700/20', glow: 'shadow-red-700/50', icon: '⚡' },
  fear: { bg: 'bg-purple-700/20', glow: 'shadow-purple-700/50', icon: '👁️' },
  terror: { bg: 'bg-purple-900/20', glow: 'shadow-purple-900/50', icon: '💀' },
  surprise: { bg: 'bg-amber-500/20', glow: 'shadow-amber-500/50', icon: '❗' },
  amazement: { bg: 'bg-amber-400/20', glow: 'shadow-amber-400/50', icon: '⭐' },
  disgust: { bg: 'bg-green-700/20', glow: 'shadow-green-700/50', icon: '🌿' },
  trust: { bg: 'bg-teal-500/20', glow: 'shadow-teal-500/50', icon: '🛡️' },
  admiration: { bg: 'bg-teal-400/20', glow: 'shadow-teal-400/50', icon: '👑' },
  anticipation: { bg: 'bg-orange-500/20', glow: 'shadow-orange-500/50', icon: '🎯' },
  curiosity: { bg: 'bg-violet-500/20', glow: 'shadow-violet-500/50', icon: '🔮' },
  interest: { bg: 'bg-violet-400/20', glow: 'shadow-violet-400/50', icon: '📜' },
  contempt: { bg: 'bg-slate-600/20', glow: 'shadow-slate-600/50', icon: '⚔️' },
  hope: { bg: 'bg-emerald-400/20', glow: 'shadow-emerald-400/50', icon: '🌟' },
  pride: { bg: 'bg-amber-600/20', glow: 'shadow-amber-600/50', icon: '🦁' },
  shame: { bg: 'bg-rose-700/20', glow: 'shadow-rose-700/50', icon: '🥀' },
  guilt: { bg: 'bg-gray-600/20', glow: 'shadow-gray-600/50', icon: '⚖️' },
  envy: { bg: 'bg-lime-600/20', glow: 'shadow-lime-600/50', icon: '🐍' },
  gratitude: { bg: 'bg-pink-400/20', glow: 'shadow-pink-400/50', icon: '💝' },
  amusement: { bg: 'bg-fuchsia-400/20', glow: 'shadow-fuchsia-400/50', icon: '🎭' },
  awe: { bg: 'bg-sky-400/20', glow: 'shadow-sky-400/50', icon: '✴️' },
  neutral: { bg: 'bg-slate-400/20', glow: 'shadow-slate-400/50', icon: '◈' },
}

const sizeClasses = {
  sm: 'w-6 h-6 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-14 h-14 text-base',
}

export function EmotionIndicator({
  emotion,
  intensity,
  description,
  size = 'md',
  showLabel = true,
  className,
}: EmotionIndicatorProps) {
  const emotionKey = emotion.toLowerCase()
  const colors = emotionColors[emotionKey] || emotionColors.neutral
  const pulseSpeed = 3 - intensity * 2 // Higher intensity = faster pulse
  
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <motion.div
        className={cn(
          'relative rounded-full flex items-center justify-center',
          colors.bg,
          sizeClasses[size],
          'border border-white/20'
        )}
        animate={{
          boxShadow: [
            `0 0 ${4 + intensity * 8}px ${colors.glow.replace('shadow-', '')}`,
            `0 0 ${8 + intensity * 16}px ${colors.glow.replace('shadow-', '')}`,
            `0 0 ${4 + intensity * 8}px ${colors.glow.replace('shadow-', '')}`,
          ],
        }}
        transition={{
          duration: pulseSpeed,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <span className="drop-shadow-lg">{colors.icon}</span>
        
        {/* Intensity ring */}
        <motion.div
          className={cn(
            'absolute inset-0 rounded-full border-2',
            'border-white/30'
          )}
          style={{
            clipPath: `inset(${100 - intensity * 100}% 0 0 0)`,
          }}
        />
      </motion.div>
      
      {showLabel && (
        <div className="flex flex-col">
          <span className="text-sm font-medium text-white/90 capitalize">
            {emotion}
          </span>
          {description && (
            <span className="text-xs text-white/50">
              {description}
            </span>
          )}
          <div className="h-1 w-16 bg-white/10 rounded-full mt-1 overflow-hidden">
            <motion.div
              className={cn('h-full rounded-full', colors.bg.replace('/20', ''))}
              initial={{ width: 0 }}
              animate={{ width: `${intensity * 100}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

// Compact version for inline use in messages
export function EmotionBadge({
  emotion,
  intensity,
  className,
}: {
  emotion: string
  intensity: number
  className?: string
}) {
  const emotionKey = emotion.toLowerCase()
  const colors = emotionColors[emotionKey] || emotionColors.neutral
  
  return (
    <motion.span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs',
        colors.bg,
        'border border-white/10',
        className
      )}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <span>{colors.icon}</span>
      <span className="capitalize">{emotion}</span>
      <span className="text-white/40">
        {Math.round(intensity * 100)}%
      </span>
    </motion.span>
  )
}
