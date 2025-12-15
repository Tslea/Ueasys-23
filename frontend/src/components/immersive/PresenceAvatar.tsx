import { motion } from 'framer-motion'
import { useMemo } from 'react'

interface PresenceAvatarProps {
  name: string
  avatarUrl?: string
  isSpeaking: boolean
}

const PresenceAvatar = ({ name, avatarUrl, isSpeaking }: PresenceAvatarProps) => {
  // Generate consistent colors based on character name
  const colors = useMemo(() => {
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    const hue1 = (hash * 37) % 360
    const hue2 = (hue1 + 45) % 360
    const hue3 = (hue1 + 180) % 360
    return {
      primary: `hsl(${hue1}, 60%, 50%)`,
      secondary: `hsl(${hue2}, 50%, 40%)`,
      accent: `hsl(${hue3}, 70%, 60%)`,
      glow: `hsla(${hue1}, 70%, 50%, 0.15)`,
      glowIntense: `hsla(${hue1}, 80%, 60%, 0.25)`,
    }
  }, [name])

  return (
    <div className="relative w-full h-full flex items-center justify-center pointer-events-none overflow-hidden">
      {/* Deep background gradient */}
      <div 
        className="absolute inset-0"
        style={{
          background: `radial-gradient(ellipse at 50% 30%, ${colors.glow} 0%, transparent 50%)`,
        }}
      />
      
      {/* Outer Aura Ring - Slow rotation */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
        className="absolute w-[500px] h-[500px] md:w-[700px] md:h-[700px] rounded-full"
        style={{
          background: `conic-gradient(from 0deg, transparent, ${colors.glow}, transparent, ${colors.glow}, transparent)`,
          opacity: isSpeaking ? 0.4 : 0.2,
        }}
      />
      
      {/* Middle Aura - Breathing effect */}
      <motion.div
        animate={{ 
          scale: isSpeaking ? [1, 1.15, 1] : [1, 1.05, 1],
          opacity: isSpeaking ? [0.2, 0.35, 0.2] : [0.1, 0.15, 0.1],
        }}
        transition={{ duration: isSpeaking ? 2 : 4, repeat: Infinity, ease: "easeInOut" }}
        className="absolute w-[400px] h-[400px] md:w-[550px] md:h-[550px] rounded-full blur-[80px]"
        style={{ background: colors.glow }}
      />
      
      {/* Inner Aura - Pulsing when speaking */}
      <motion.div
        animate={{ 
          scale: isSpeaking ? [1, 1.3, 1] : 1,
          opacity: isSpeaking ? [0.3, 0.5, 0.3] : 0.2,
        }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        className="absolute w-[250px] h-[250px] md:w-[350px] md:h-[350px] rounded-full blur-[60px]"
        style={{ background: colors.glowIntense }}
      />

      {/* Particle ring when speaking */}
      {isSpeaking && (
        <div className="absolute w-[300px] h-[300px] md:w-[400px] md:h-[400px]">
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1.5 h-1.5 rounded-full"
              style={{
                background: i % 2 === 0 ? colors.primary : colors.accent,
                top: '50%',
                left: '50%',
              }}
              animate={{
                x: [0, Math.cos((i * 45) * Math.PI / 180) * 150],
                y: [0, Math.sin((i * 45) * Math.PI / 180) * 150],
                opacity: [0.8, 0],
                scale: [1, 0.5],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.2,
                ease: "easeOut",
              }}
            />
          ))}
        </div>
      )}

      {/* Central Core / Avatar Container */}
      <motion.div 
        className="relative z-10"
        animate={isSpeaking ? { scale: [1, 1.02, 1] } : {}}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        {/* Outer ring */}
        <div 
          className="absolute -inset-4 rounded-full opacity-30"
          style={{
            background: `conic-gradient(from 0deg, ${colors.primary}, ${colors.secondary}, ${colors.primary})`,
            filter: 'blur(8px)',
          }}
        />
        
        {/* Avatar Circle */}
        <div 
          className="relative w-48 h-48 md:w-72 md:h-72 lg:w-80 lg:h-80 rounded-full overflow-hidden"
          style={{
            border: `1px solid ${colors.primary}33`,
            boxShadow: `0 0 60px ${colors.glow}, inset 0 0 40px rgba(0,0,0,0.5)`,
          }}
        >
          {avatarUrl ? (
            <img 
              src={avatarUrl} 
              alt={name} 
              className="w-full h-full object-cover opacity-70 mix-blend-luminosity"
            />
          ) : (
            // Procedural mystical symbol when no avatar
            <div 
              className="w-full h-full flex items-center justify-center"
              style={{ background: `radial-gradient(circle at center, ${colors.glow} 0%, var(--void-black) 70%)` }}
            >
              <svg viewBox="0 0 100 100" className="w-2/3 h-2/3 opacity-40">
                <defs>
                  <filter id="avatar-glow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <g filter="url(#avatar-glow)">
                  {/* Outer circle */}
                  <circle cx="50" cy="50" r="45" fill="none" stroke={colors.primary} strokeWidth="0.5" opacity="0.6" />
                  {/* Inner symbol based on first letter */}
                  <text 
                    x="50" 
                    y="55" 
                    textAnchor="middle" 
                    fill={colors.primary}
                    fontSize="32"
                    fontFamily="serif"
                    opacity="0.8"
                  >
                    {name[0]}
                  </text>
                  {/* Decorative lines */}
                  {[0, 60, 120, 180, 240, 300].map((angle, i) => (
                    <line
                      key={i}
                      x1={50 + Math.cos((angle - 90) * Math.PI / 180) * 35}
                      y1={50 + Math.sin((angle - 90) * Math.PI / 180) * 35}
                      x2={50 + Math.cos((angle - 90) * Math.PI / 180) * 42}
                      y2={50 + Math.sin((angle - 90) * Math.PI / 180) * 42}
                      stroke={colors.secondary}
                      strokeWidth="1"
                      opacity="0.4"
                    />
                  ))}
                </g>
              </svg>
            </div>
          )}
          
          {/* Overlay gradients */}
          <div className="absolute inset-0 bg-gradient-to-t from-void-black/60 via-transparent to-void-black/30" />
          <div className="absolute inset-0 bg-gradient-to-r from-void-black/20 via-transparent to-void-black/20" />
        </div>
      </motion.div>
      
      {/* Character name below avatar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="absolute bottom-[15%] md:bottom-[20%] text-center"
      >
        <h2 
          className="font-display text-2xl md:text-3xl tracking-wide"
          style={{ 
            color: colors.primary,
            textShadow: `0 0 30px ${colors.glow}`,
            opacity: 0.6,
          }}
        >
          {name}
        </h2>
      </motion.div>
    </div>
  )
}

export default PresenceAvatar
