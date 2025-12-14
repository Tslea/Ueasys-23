import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Map, Plus, Shield } from 'lucide-react'
import { useCharacterStore } from '@/stores'
import CharacterCard from '@/components/immersive/CharacterCard'
import { Link } from 'react-router-dom'

export default function Home() {
  const { characters, fetchCharacters, isLoading } = useCharacterStore()
  const [showAdmin, setShowAdmin] = useState(false)

  useEffect(() => {
    fetchCharacters()
  }, [fetchCharacters])

  return (
    <div className="h-full w-full flex flex-col items-center justify-center p-8">
      {/* The Nexus Title */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="absolute top-24 left-0 w-full text-center pointer-events-none z-0"
      >
        <h2 className="text-[10vw] font-bold text-white/[0.02] tracking-widest uppercase select-none">
          Nexus
        </h2>
      </motion.div>

      {/* Character Gallery (Horizontal Scroll / Grid) */}
      <div className="relative z-10 w-full max-w-7xl">
        {isLoading ? (
          <div className="flex justify-center items-center h-[400px]">
            <div className="w-12 h-12 border-2 border-neon-blue border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="flex flex-wrap justify-center gap-8 perspective-1000">
            {characters.map((char, idx) => (
              <CharacterCard key={char.id} character={char} index={idx} />
            ))}
            
            {/* Add New Character (Admin Only - Hidden by default) */}
            {showAdmin && (
              <Link to="/admin/characters/new">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-[300px] h-[450px] rounded-2xl border-2 border-dashed border-white/10 flex flex-col items-center justify-center gap-4 text-gray-500 hover:text-neon-gold hover:border-neon-gold/50 transition-colors cursor-pointer bg-white/[0.02]"
                >
                  <Plus className="w-12 h-12" />
                  <span className="font-mono text-sm">FORGE NEW SOUL</span>
                </motion.div>
              </Link>
            )}
          </div>
        )}
      </div>

      {/* Bottom Controls */}
      <div className="fixed bottom-12 left-0 w-full flex justify-center items-center gap-8 z-20">
        {/* World Map (Coming Soon) */}
        <div className="group relative">
          <button disabled className="p-4 rounded-full bg-white/5 border border-white/10 text-gray-500 cursor-not-allowed group-hover:border-white/20 transition-all">
            <Map className="w-6 h-6" />
          </button>
          <span className="absolute -top-8 left-1/2 -translate-x-1/2 text-xs font-mono text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            WORLD MAP [OFFLINE]
          </span>
        </div>

        {/* Admin Toggle */}
        <button 
          onClick={() => setShowAdmin(!showAdmin)}
          className={`p-4 rounded-full border transition-all ${
            showAdmin 
              ? 'bg-neon-gold/10 border-neon-gold text-neon-gold' 
              : 'bg-white/5 border-white/10 text-gray-500 hover:text-white'
          }`}
        >
          <Shield className="w-6 h-6" />
        </button>
      </div>
    </div>
  )
}
