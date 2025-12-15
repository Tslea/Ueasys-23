import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { useState } from 'react'
import { ChevronDown, Brain, Heart, Activity, Zap } from 'lucide-react'

interface AdvancedEmotionalState {
  emotion: string
  emotion_confidence?: number
  valence: number      // -1 to 1: unpleasant to pleasant
  arousal: number      // -1 to 1: calm to activated
  dominance: number    // -1 to 1: submissive to dominant
  dominant_system?: string  // Panksepp's affective system
  system_intensity?: number
  all_systems?: Record<string, number>
}

interface SoulStateProps {
  emotionalState: {
    emotion: string
    intensity: number
    advanced?: AdvancedEmotionalState
  }
  size?: 'sm' | 'md' | 'lg'
  expanded?: boolean
  className?: string
}

// Map emotions to colors and icons
const emotionVisuals: Record<string, { color: string; icon: string; gradient: string }> = {
  joy: { color: '#FFD700', icon: '✨', gradient: 'from-yellow-500 to-amber-500' },
  excitement: { color: '#FF6B35', icon: '🔥', gradient: 'from-orange-500 to-red-500' },
  enthusiasm: { color: '#FF8C00', icon: '⚡', gradient: 'from-amber-500 to-orange-500' },
  contentment: { color: '#4ECDC4', icon: '🌿', gradient: 'from-teal-500 to-cyan-500' },
  serenity: { color: '#87CEEB', icon: '🌊', gradient: 'from-cyan-400 to-blue-400' },
  calm: { color: '#B8D4E3', icon: '☁️', gradient: 'from-blue-300 to-slate-400' },
  peace: { color: '#E6E6FA', icon: '🕊️', gradient: 'from-indigo-300 to-purple-300' },
  anger: { color: '#DC143C', icon: '🔥', gradient: 'from-red-600 to-red-800' },
  frustration: { color: '#CD5C5C', icon: '😤', gradient: 'from-red-500 to-orange-600' },
  fear: { color: '#4B0082', icon: '👁️', gradient: 'from-purple-800 to-indigo-900' },
  anxiety: { color: '#663399', icon: '💫', gradient: 'from-purple-600 to-violet-700' },
  panic: { color: '#2F0037', icon: '💀', gradient: 'from-purple-900 to-black' },
  sadness: { color: '#4169E1', icon: '💧', gradient: 'from-blue-500 to-indigo-600' },
  grief: { color: '#191970', icon: '🌙', gradient: 'from-indigo-800 to-blue-900' },
  melancholy: { color: '#6A5ACD', icon: '🌑', gradient: 'from-slate-600 to-indigo-700' },
  love: { color: '#FF69B4', icon: '💖', gradient: 'from-pink-500 to-rose-500' },
  compassion: { color: '#FFB6C1', icon: '💝', gradient: 'from-pink-400 to-rose-400' },
  curiosity: { color: '#9932CC', icon: '🔮', gradient: 'from-violet-500 to-purple-600' },
  interest: { color: '#8A2BE2', icon: '📜', gradient: 'from-violet-600 to-purple-500' },
  surprise: { color: '#FFD700', icon: '❗', gradient: 'from-yellow-400 to-amber-500' },
  disgust: { color: '#228B22', icon: '🌿', gradient: 'from-green-600 to-emerald-700' },
  contempt: { color: '#708090', icon: '⚔️', gradient: 'from-slate-500 to-gray-600' },
  pride: { color: '#DAA520', icon: '👑', gradient: 'from-amber-500 to-yellow-600' },
  shame: { color: '#8B4513', icon: '🥀', gradient: 'from-rose-700 to-rose-900' },
  hope: { color: '#98FB98', icon: '🌟', gradient: 'from-emerald-400 to-green-500' },
  determination: { color: '#FF4500', icon: '🎯', gradient: 'from-orange-600 to-red-600' },
  awe: { color: '#00CED1', icon: '✴️', gradient: 'from-cyan-500 to-teal-500' },
  gratitude: { color: '#FF1493', icon: '💝', gradient: 'from-pink-500 to-fuchsia-500' },
  neutral: { color: '#808080', icon: '◈', gradient: 'from-slate-500 to-gray-500' },
}

// Panksepp's systems visualizations
const systemVisuals: Record<string, { icon: string; color: string; label: string }> = {
  seeking: { icon: '🔍', color: 'text-violet-400', label: 'Esplorazione' },
  rage: { icon: '⚡', color: 'text-red-500', label: 'Rabbia' },
  fear: { icon: '👁️', color: 'text-purple-600', label: 'Paura' },
  lust: { icon: '💫', color: 'text-pink-500', label: 'Attrazione' },
  care: { icon: '💖', color: 'text-rose-400', label: 'Cura' },
  panic_grief: { icon: '💧', color: 'text-blue-500', label: 'Dolore' },
  play: { icon: '🎭', color: 'text-yellow-400', label: 'Gioco' },
}

// Dimension bar component
function DimensionBar({ 
  value, 
  label, 
  leftLabel, 
  rightLabel,
  color = 'purple',
}: { 
  value: number
  label: string
  leftLabel: string
  rightLabel: string
  color?: string
}) {
  const percentage = ((value + 1) / 2) * 100  // Convert -1..1 to 0..100
  
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] text-white/40 font-mono">
        <span>{leftLabel}</span>
        <span className="text-white/60">{label}</span>
        <span>{rightLabel}</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden relative">
        {/* Center marker */}
        <div className="absolute inset-y-0 left-1/2 w-px bg-white/20" />
        
        {/* Value indicator */}
        <motion.div
          className={cn(
            'absolute h-full rounded-full',
            value >= 0 
              ? `bg-gradient-to-r from-${color}-500/50 to-${color}-400`
              : `bg-gradient-to-l from-${color}-500/50 to-${color}-400`
          )}
          style={{
            left: value >= 0 ? '50%' : `${percentage}%`,
            width: value >= 0 ? `${percentage - 50}%` : `${50 - percentage}%`,
          }}
          initial={{ width: 0 }}
          animate={{ 
            width: value >= 0 ? `${percentage - 50}%` : `${50 - percentage}%`,
            left: value >= 0 ? '50%' : `${percentage}%`,
          }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
        
        {/* Current position marker */}
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-white shadow-glow"
          animate={{ left: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{ marginLeft: '-4px' }}
        />
      </div>
    </div>
  )
}

export function AdvancedSoulState({
  emotionalState,
  expanded: initialExpanded = false,
  className,
}: SoulStateProps) {
  const [isExpanded, setIsExpanded] = useState(initialExpanded)
  
  const emotion = emotionalState.emotion.toLowerCase()
  const visuals = emotionVisuals[emotion] || emotionVisuals.neutral
  const advanced = emotionalState.advanced
  
  // Get system info if available
  const dominantSystem = advanced?.dominant_system
  const systemInfo = dominantSystem ? systemVisuals[dominantSystem] : null
  
  return (
    <motion.div
      className={cn(
        'rounded-xl glass-panel overflow-hidden',
        className
      )}
      layout
    >
      {/* Header - always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          {/* Emotion icon with pulsing effect */}
          <motion.div
            className={cn(
              'w-10 h-10 rounded-full flex items-center justify-center',
              `bg-gradient-to-br ${visuals.gradient}`,
            )}
            animate={{
              boxShadow: [
                `0 0 8px ${visuals.color}40`,
                `0 0 20px ${visuals.color}60`,
                `0 0 8px ${visuals.color}40`,
              ],
            }}
            transition={{
              duration: 2 - emotionalState.intensity,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            <span className="text-lg drop-shadow-lg">{visuals.icon}</span>
          </motion.div>
          
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-white capitalize">
                {emotionalState.emotion}
              </span>
              {systemInfo && (
                <span className={cn('text-xs', systemInfo.color)}>
                  {systemInfo.icon}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <div className="w-16 h-1 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full bg-gradient-to-r ${visuals.gradient}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${emotionalState.intensity * 100}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <span className="text-[10px] text-white/40 font-mono">
                {Math.round(emotionalState.intensity * 100)}%
              </span>
            </div>
          </div>
        </div>
        
        <ChevronDown 
          className={cn(
            'w-4 h-4 text-white/40 transition-transform',
            isExpanded && 'rotate-180'
          )} 
        />
      </button>
      
      {/* Expanded details */}
      <AnimatePresence>
        {isExpanded && advanced && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-white/10"
          >
            <div className="p-4 space-y-4">
              {/* VAD Model visualization */}
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs text-white/60 font-mono">
                  <Brain className="w-3 h-3" />
                  <span>MODELLO DIMENSIONALE</span>
                </div>
                
                <DimensionBar
                  value={advanced.valence}
                  label="Valenza"
                  leftLabel="−"
                  rightLabel="+"
                  color="emerald"
                />
                
                <DimensionBar
                  value={advanced.arousal}
                  label="Attivazione"
                  leftLabel="Calmo"
                  rightLabel="Attivo"
                  color="orange"
                />
                
                <DimensionBar
                  value={advanced.dominance}
                  label="Controllo"
                  leftLabel="−"
                  rightLabel="+"
                  color="violet"
                />
              </div>
              
              {/* Panksepp's Systems */}
              {advanced.all_systems && Object.keys(advanced.all_systems).length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs text-white/60 font-mono">
                    <Activity className="w-3 h-3" />
                    <span>SISTEMI AFFETTIVI</span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(advanced.all_systems)
                      .sort(([, a], [, b]) => b - a)
                      .map(([system, intensity]) => {
                        const sysInfo = systemVisuals[system]
                        if (!sysInfo) return null
                        
                        return (
                          <div 
                            key={system}
                            className="flex items-center gap-2 text-xs"
                          >
                            <span className={sysInfo.color}>{sysInfo.icon}</span>
                            <span className="text-white/60 flex-1">{sysInfo.label}</span>
                            <div className="w-12 h-1 bg-white/10 rounded-full overflow-hidden">
                              <motion.div
                                className={cn('h-full rounded-full', sysInfo.color.replace('text-', 'bg-'))}
                                initial={{ width: 0 }}
                                animate={{ width: `${intensity * 100}%` }}
                              />
                            </div>
                          </div>
                        )
                      })}
                  </div>
                </div>
              )}
              
              {/* Quick stats */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-white/5">
                <div className="text-center">
                  <Heart className={cn(
                    'w-4 h-4 mx-auto mb-1',
                    advanced.valence > 0 ? 'text-rose-400' : 'text-blue-400'
                  )} />
                  <span className="text-[10px] text-white/40 block">
                    {advanced.valence > 0.3 ? 'Positivo' : advanced.valence < -0.3 ? 'Negativo' : 'Neutro'}
                  </span>
                </div>
                <div className="text-center">
                  <Zap className={cn(
                    'w-4 h-4 mx-auto mb-1',
                    advanced.arousal > 0 ? 'text-yellow-400' : 'text-slate-400'
                  )} />
                  <span className="text-[10px] text-white/40 block">
                    {advanced.arousal > 0.3 ? 'Attivato' : advanced.arousal < -0.3 ? 'Calmo' : 'Bilanciato'}
                  </span>
                </div>
                <div className="text-center">
                  <Activity className={cn(
                    'w-4 h-4 mx-auto mb-1',
                    advanced.dominance > 0 ? 'text-violet-400' : 'text-gray-400'
                  )} />
                  <span className="text-[10px] text-white/40 block">
                    {advanced.dominance > 0.3 ? 'Dominante' : advanced.dominance < -0.3 ? 'Sottomesso' : 'Equilibrato'}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Compact version for the chat header
export function SoulStateCompact({
  emotionalState,
  onClick,
  className,
}: {
  emotionalState: { emotion: string; intensity: number }
  onClick?: () => void
  className?: string
}) {
  const emotion = emotionalState.emotion.toLowerCase()
  const visuals = emotionVisuals[emotion] || emotionVisuals.neutral
  
  return (
    <motion.button
      onClick={onClick}
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded-full glass-panel',
        'hover:bg-white/10 transition-colors',
        className
      )}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <span className="text-[10px] font-mono text-white/40 uppercase tracking-widest">
        Soul
      </span>
      <motion.span
        className="text-sm"
        animate={{
          textShadow: [
            `0 0 4px ${visuals.color}`,
            `0 0 8px ${visuals.color}`,
            `0 0 4px ${visuals.color}`,
          ],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        {visuals.icon}
      </motion.span>
      <span className="text-xs text-white/70 capitalize hidden sm:inline">
        {emotionalState.emotion}
      </span>
    </motion.button>
  )
}
