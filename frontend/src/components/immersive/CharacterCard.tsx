import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Character } from '@/stores/characterStore'
import { Brain, Sparkles, Activity, Zap } from 'lucide-react'
import { useMemo } from 'react'

interface CharacterCardProps {
  character: Character
  index: number
}

// Generate a mystical avatar based on character attributes
const MysticalAvatar = ({ name, archetype }: { name: string; archetype: string }) => {
  // Generate consistent colors based on character name
  const colors = useMemo(() => {
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    const hue1 = (hash * 37) % 360
    const hue2 = (hue1 + 60) % 360
    return {
      primary: `hsl(${hue1}, 70%, 50%)`,
      secondary: `hsl(${hue2}, 60%, 40%)`,
      glow: `hsla(${hue1}, 80%, 60%, 0.4)`,
    }
  }, [name])

  // Different patterns for different archetypes
  const getPattern = () => {
    switch (archetype?.toLowerCase()) {
      case 'wise_mentor':
      case 'mentor':
        return (
          <>
            {/* Wisdom runes circle */}
            <circle cx="50" cy="50" r="35" fill="none" stroke={colors.primary} strokeWidth="0.5" opacity="0.6" />
            <circle cx="50" cy="50" r="28" fill="none" stroke={colors.secondary} strokeWidth="0.3" opacity="0.4" strokeDasharray="3 2" />
            {/* Central eye of wisdom */}
            <ellipse cx="50" cy="50" rx="12" ry="8" fill="none" stroke={colors.primary} strokeWidth="1" />
            <circle cx="50" cy="50" r="4" fill={colors.primary} />
            {/* Radiant lines */}
            {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => (
              <line
                key={i}
                x1="50"
                y1="50"
                x2={50 + Math.cos(angle * Math.PI / 180) * 42}
                y2={50 + Math.sin(angle * Math.PI / 180) * 42}
                stroke={colors.secondary}
                strokeWidth="0.3"
                opacity="0.4"
              />
            ))}
          </>
        )
      case 'hero':
      case 'warrior':
        return (
          <>
            {/* Shield shape */}
            <path d="M50 15 L75 30 L75 55 L50 85 L25 55 L25 30 Z" fill="none" stroke={colors.primary} strokeWidth="1" />
            <path d="M50 25 L65 35 L65 50 L50 70 L35 50 L35 35 Z" fill={`${colors.primary}22`} stroke={colors.secondary} strokeWidth="0.5" />
            {/* Sword cross */}
            <line x1="50" y1="30" x2="50" y2="65" stroke={colors.primary} strokeWidth="1.5" />
            <line x1="40" y1="40" x2="60" y2="40" stroke={colors.primary} strokeWidth="1" />
          </>
        )
      case 'dragon':
      case 'monster':
        return (
          <>
            {/* Dragon eye */}
            <ellipse cx="50" cy="50" rx="25" ry="15" fill="none" stroke={colors.primary} strokeWidth="1.5" />
            <ellipse cx="50" cy="50" rx="8" ry="15" fill={colors.primary} />
            {/* Scales pattern */}
            {[0, 1, 2, 3, 4].map((i) => (
              <path
                key={i}
                d={`M${25 + i * 12} 75 Q${31 + i * 12} 65 ${37 + i * 12} 75`}
                fill="none"
                stroke={colors.secondary}
                strokeWidth="0.5"
                opacity="0.6"
              />
            ))}
            {/* Fire breath hint */}
            <path d="M75 45 Q85 50 75 55" fill="none" stroke={colors.primary} strokeWidth="0.5" opacity="0.8" />
          </>
        )
      case 'elf':
      case 'sage':
        return (
          <>
            {/* Leaf/nature pattern */}
            <path d="M50 20 Q65 35 50 50 Q35 35 50 20" fill={`${colors.primary}22`} stroke={colors.primary} strokeWidth="0.8" />
            <path d="M50 50 Q65 65 50 80 Q35 65 50 50" fill={`${colors.secondary}22`} stroke={colors.secondary} strokeWidth="0.8" />
            {/* Star points */}
            {[0, 72, 144, 216, 288].map((angle, i) => (
              <circle
                key={i}
                cx={50 + Math.cos((angle - 90) * Math.PI / 180) * 38}
                cy={50 + Math.sin((angle - 90) * Math.PI / 180) * 38}
                r="2"
                fill={colors.primary}
                opacity="0.6"
              />
            ))}
          </>
        )
      default:
        return (
          <>
            {/* Default mystical symbol */}
            <circle cx="50" cy="50" r="30" fill="none" stroke={colors.primary} strokeWidth="0.8" />
            <circle cx="50" cy="50" r="20" fill="none" stroke={colors.secondary} strokeWidth="0.5" strokeDasharray="4 2" />
            <polygon points="50,25 65,45 58,70 42,70 35,45" fill="none" stroke={colors.primary} strokeWidth="0.6" />
            <circle cx="50" cy="50" r="5" fill={colors.primary} />
          </>
        )
    }
  }

  return (
    <div className="absolute inset-0 flex items-center justify-center">
      {/* Background glow */}
      <div 
        className="absolute w-40 h-40 rounded-full blur-3xl opacity-30"
        style={{ background: colors.glow }}
      />
      {/* SVG Avatar */}
      <svg viewBox="0 0 100 100" className="w-32 h-32 opacity-60 group-hover:opacity-90 transition-opacity duration-500">
        <defs>
          <filter id={`glow-${name}`}>
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <g filter={`url(#glow-${name})`}>
          {getPattern()}
        </g>
      </svg>
    </div>
  )
}

// Archetype to display name mapping
const archetypeLabels: Record<string, string> = {
  wise_mentor: 'Sage',
  mentor: 'Mentor',
  hero: 'Hero',
  warrior: 'Warrior',
  dragon: 'Dragon',
  monster: 'Beast',
  elf: 'Elven',
  sage: 'Sage',
  trickster: 'Trickster',
}

const CharacterCard = ({ character, index }: CharacterCardProps) => {
  const archetypeLabel = archetypeLabels[character.archetype?.toLowerCase()] || character.archetype || 'Unknown'
  
  return (
    <Link to={`/chat/${character.id}`}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: index * 0.08 }}
        whileHover={{ scale: 1.02, y: -5 }}
        className="group relative w-[280px] md:w-[300px] h-[420px] md:h-[450px] rounded-2xl overflow-hidden cursor-pointer"
      >
        {/* Card Background with gradient border effect */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-void-surface via-void-deep to-void-black border border-white/[0.06] group-hover:border-white/[0.12] transition-colors duration-300">
          {/* Mystical Avatar */}
          <MysticalAvatar name={character.name} archetype={character.archetype} />
          
          {/* Top gradient fade */}
          <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-void-black/60 to-transparent" />
          
          {/* Bottom gradient for content */}
          <div className="absolute inset-x-0 bottom-0 h-3/4 bg-gradient-to-t from-void-black via-void-black/95 to-transparent" />
          
          {/* Hover glow effect - simplified */}
          <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
            style={{
              background: 'radial-gradient(circle at 50% 30%, rgba(178, 77, 255, 0.1) 0%, transparent 50%)',
            }}
          />
        </div>

        {/* Content */}
        <div className="absolute inset-0 p-5 md:p-6 flex flex-col justify-between">
          {/* Top Section - Status */}
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] backdrop-blur-sm">
              <div className={`w-1.5 h-1.5 rounded-full ${character.status === 'active' ? 'bg-neon-emerald animate-pulse' : 'bg-gray-500'}`} />
              <span className={`text-[10px] font-mono tracking-wider ${character.status === 'active' ? 'text-neon-emerald/80' : 'text-gray-500'}`}>
                {character.status === 'active' ? 'AWAKENED' : 'DORMANT'}
              </span>
            </div>
            
            {/* Archetype Badge */}
            <div className="px-2.5 py-1 rounded-full bg-neon-purple/10 border border-neon-purple/20">
              <span className="text-[10px] font-mono text-neon-purple/80 tracking-wider uppercase">
                {archetypeLabel}
              </span>
            </div>
          </div>

          {/* Bottom Section - Character Info */}
          <div className="space-y-4 transform transition-transform duration-400 group-hover:translate-y-[-8px]">
            {/* Character Name */}
            <div>
              <h3 className="font-display text-3xl md:text-4xl text-white tracking-wide group-hover:text-glow transition-all duration-300">
                {character.name}
              </h3>
              {character.alignment && (
                <span className="text-xs font-body text-white/40 italic tracking-wide">
                  {character.alignment.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
              )}
            </div>

            {/* Description */}
            <p className="text-sm font-body text-white/50 line-clamp-2 leading-relaxed group-hover:text-white/70 transition-colors duration-300">
              {character.description}
            </p>

            {/* Stats Bar */}
            <div className="pt-4 border-t border-white/[0.06] flex justify-between items-center">
              <div className="flex gap-5">
                <div className="flex flex-col items-center gap-1.5 group/stat">
                  <Brain className="w-4 h-4 text-neon-purple/60 group-hover/stat:text-neon-purple transition-colors" />
                  <span className="text-[9px] font-mono text-white/30 tracking-wider">WISDOM</span>
                </div>
                <div className="flex flex-col items-center gap-1.5 group/stat">
                  <Sparkles className="w-4 h-4 text-neon-gold/60 group-hover/stat:text-neon-gold transition-colors" />
                  <span className="text-[9px] font-mono text-white/30 tracking-wider">MEMORY</span>
                </div>
                <div className="flex flex-col items-center gap-1.5 group/stat">
                  <Zap className="w-4 h-4 text-neon-blue/60 group-hover/stat:text-neon-blue transition-colors" />
                  <span className="text-[9px] font-mono text-white/30 tracking-wider">SOUL</span>
                </div>
              </div>
              
              {/* Connect CTA */}
              <motion.div 
                className="flex items-center gap-2 text-neon-blue/70 group-hover:text-neon-blue transition-colors"
                whileHover={{ x: 3 }}
              >
                <span className="text-xs font-mono tracking-wider">COMMUNE</span>
                <Activity className="w-4 h-4" />
              </motion.div>
            </div>
          </div>
        </div>
      </motion.div>
    </Link>
  )
}

export default CharacterCard
