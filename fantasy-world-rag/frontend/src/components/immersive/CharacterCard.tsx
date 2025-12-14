import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Character } from '@/stores/characterStore'
import { Brain, Sparkles, Activity } from 'lucide-react'

interface CharacterCardProps {
  character: Character
  index: number
}

const CharacterCard = ({ character, index }: CharacterCardProps) => {
  return (
    <Link to={`/chat/${character.id}`}>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: index * 0.1 }}
        whileHover={{ scale: 1.02, y: -5 }}
        className="group relative w-[300px] h-[450px] rounded-2xl overflow-hidden cursor-pointer"
      >
        {/* Background Image / Gradient */}
        <div className="absolute inset-0 bg-void-surface border border-white/5 group-hover:border-neon-blue/50 transition-colors duration-500">
          {/* Placeholder for Avatar if no URL */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-void-black/50 to-void-black" />
          
          {/* Dynamic Glow on Hover */}
          <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-t from-neon-blue/10 via-transparent to-transparent" />
        </div>

        {/* Content */}
        <div className="absolute inset-0 p-6 flex flex-col justify-end">
          {/* Status Indicator */}
          <div className="absolute top-6 right-6 flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${character.status === 'active' ? 'bg-green-500' : 'bg-gray-500'} animate-pulse`} />
            <span className={`text-xs font-mono ${character.status === 'active' ? 'text-green-500/80' : 'text-gray-500'}`}>
              {character.status === 'active' ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>

          {/* Character Info */}
          <div className="space-y-3 transform transition-transform duration-300 group-hover:translate-y-[-10px]">
            <h3 className="text-3xl font-light text-white tracking-wide group-hover:text-neon-blue transition-colors">
              {character.name}
            </h3>
            
            <div className="flex items-center gap-3 text-xs font-mono text-gray-400">
              <span className="px-2 py-1 rounded bg-white/5 border border-white/10 capitalize">
                {character.archetype}
              </span>
              <span className="px-2 py-1 rounded bg-white/5 border border-white/10 capitalize">
                {character.alignment?.replace('_', ' ') || 'Neutral'}
              </span>
            </div>

            <p className="text-sm text-gray-400 line-clamp-3 leading-relaxed opacity-80 group-hover:opacity-100 transition-opacity">
              {character.description}
            </p>
          </div>

          {/* Stats / Metrics (Decorative) */}
          <div className="mt-6 pt-6 border-t border-white/10 flex justify-between items-center opacity-0 group-hover:opacity-100 transition-all duration-500 delay-100">
            <div className="flex gap-4">
              <div className="flex flex-col items-center gap-1">
                <Brain className="w-4 h-4 text-neon-purple" />
                <span className="text-[10px] text-gray-500">INT</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <Sparkles className="w-4 h-4 text-neon-gold" />
                <span className="text-[10px] text-gray-500">MEM</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <Activity className="w-4 h-4 text-neon-blue" />
                <span className="text-[10px] text-gray-500">SYNC</span>
              </div>
            </div>
            <span className="text-xs text-neon-blue font-mono">CONNECT &rarr;</span>
          </div>
        </div>
      </motion.div>
    </Link>
  )
}

export default CharacterCard
