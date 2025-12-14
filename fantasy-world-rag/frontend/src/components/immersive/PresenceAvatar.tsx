import { motion } from 'framer-motion'

interface PresenceAvatarProps {
  name: string
  avatarUrl?: string
  isSpeaking: boolean
}

const PresenceAvatar = ({ name, avatarUrl, isSpeaking }: PresenceAvatarProps) => {
  return (
    <div className="relative w-full h-full flex items-center justify-center pointer-events-none">
      {/* Ambient Aura */}
      <motion.div
        animate={{ 
          scale: isSpeaking ? [1, 1.2, 1] : 1,
          opacity: isSpeaking ? [0.2, 0.4, 0.2] : 0.1
        }}
        transition={{ duration: 2, repeat: Infinity }}
        className="absolute w-[600px] h-[600px] bg-neon-gold/10 rounded-full blur-[100px]"
      />

      {/* Central Core / Avatar */}
      <div className="relative z-10 w-64 h-64 md:w-96 md:h-96 rounded-full overflow-hidden border border-white/5 bg-black/20 backdrop-blur-sm">
        {avatarUrl ? (
          <img 
            src={avatarUrl} 
            alt={name} 
            className="w-full h-full object-cover opacity-80 mix-blend-luminosity"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-void-surface">
            <span className="text-6xl font-thin text-white/10">{name[0]}</span>
          </div>
        )}
        
        {/* Overlay Glitch Effect (Optional) */}
        <div className="absolute inset-0 bg-gradient-to-t from-void-black via-transparent to-transparent opacity-50" />
      </div>
    </div>
  )
}

export default PresenceAvatar
