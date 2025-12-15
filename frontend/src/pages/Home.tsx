import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Map, Plus, Shield, Compass, BookOpen } from 'lucide-react'
import { useCharacterStore } from '@/stores'
import CharacterCard from '@/components/immersive/CharacterCard'
import { Link } from 'react-router-dom'

// Elegant loading animation (simplified for performance)
const LoadingOrb = () => (
  <div className="flex flex-col items-center justify-center gap-6">
    <div className="relative">
      {/* Simple spinning ring */}
      <div className="w-16 h-16 rounded-full border-2 border-neon-purple/20 border-t-neon-purple animate-spin" />
      {/* Center dot */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-2 h-2 rounded-full bg-neon-purple/60 animate-pulse" />
      </div>
    </div>
    <span className="text-sm font-mono text-white/40 tracking-widest animate-pulse">
      AWAKENING SOULS...
    </span>
  </div>
)

export default function Home() {
  const { characters, fetchCharacters, isLoading } = useCharacterStore()
  const [showAdmin, setShowAdmin] = useState(false)

  useEffect(() => {
    fetchCharacters()
  }, [fetchCharacters])

  return (
    <div className="h-full w-full flex flex-col items-center p-4 md:p-8 overflow-y-auto no-scrollbar">
      {/* Hero Section with Title */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center mb-8 md:mb-12 relative z-10"
      >
        {/* Background Title - Decorative */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none -z-10">
          <h2 className="text-[15vw] md:text-[12vw] font-display font-bold text-white/[0.015] tracking-[0.2em] uppercase select-none">
            Nexus
          </h2>
        </div>
        
        {/* Main Title */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <h1 className="font-display text-4xl md:text-5xl lg:text-6xl text-white/90 tracking-wide mb-3">
            The <span className="gradient-text">Nexus</span>
          </h1>
          <p className="font-body text-base md:text-lg text-white/40 max-w-lg mx-auto leading-relaxed">
            Where ancient souls await communion. Choose a presence to begin your journey.
          </p>
        </motion.div>
        
        {/* Decorative line */}
        <motion.div 
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="mt-6 mx-auto w-32 h-px bg-gradient-to-r from-transparent via-neon-purple/50 to-transparent"
        />
      </motion.div>

      {/* Character Gallery */}
      <div className="relative z-10 w-full max-w-7xl flex-1">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex justify-center items-center h-[400px]"
            >
              <LoadingOrb />
            </motion.div>
          ) : characters.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-[400px] gap-4"
            >
              <BookOpen className="w-16 h-16 text-white/20" />
              <p className="text-white/40 font-body text-lg">No souls have been summoned yet</p>
              <Link 
                to="/admin/characters/new"
                className="mt-4 px-6 py-3 rounded-full bg-neon-purple/10 border border-neon-purple/30 text-neon-purple hover:bg-neon-purple/20 transition-colors font-mono text-sm"
              >
                Summon First Soul
              </Link>
            </motion.div>
          ) : (
            <motion.div
              key="characters"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-wrap justify-center gap-6 md:gap-8 perspective-1000 pb-24"
            >
              {characters.map((char, idx) => (
                <CharacterCard key={char.id} character={char} index={idx} />
              ))}
              
              {/* Add New Character Card (Admin Mode) */}
              <AnimatePresence>
                {showAdmin && (
                  <Link to="/admin/characters/new">
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      whileHover={{ scale: 1.02, y: -5 }}
                      className="w-[280px] md:w-[300px] h-[420px] md:h-[450px] rounded-2xl border-2 border-dashed border-white/10 flex flex-col items-center justify-center gap-4 text-white/30 hover:text-neon-gold hover:border-neon-gold/40 hover:bg-neon-gold/[0.02] transition-colors duration-300 cursor-pointer backdrop-blur-sm"
                    >
                      <Plus className="w-14 h-14" strokeWidth={1} />
                      <span className="font-mono text-sm tracking-wider">FORGE NEW SOUL</span>
                    </motion.div>
                  </Link>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Bottom Controls */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="fixed bottom-8 left-0 w-full flex justify-center items-center gap-4 z-20"
      >
        <div className="flex items-center gap-3 px-4 py-3 rounded-full glass-panel">
          {/* World Map (Coming Soon) */}
          <div className="group relative">
            <button 
              disabled 
              className="p-3 rounded-full bg-white/[0.03] border border-white/[0.08] text-white/30 cursor-not-allowed hover:bg-white/[0.05] transition-all"
            >
              <Map className="w-5 h-5" />
            </button>
            <span className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1.5 rounded-lg bg-void-surface border border-white/10 text-[10px] font-mono text-white/50 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
              WORLD MAP [SEALED]
            </span>
          </div>
          
          {/* Compass (Decorative) */}
          <div className="group relative">
            <button 
              disabled
              className="p-3 rounded-full bg-white/[0.03] border border-white/[0.08] text-white/30 cursor-not-allowed hover:bg-white/[0.05] transition-all"
            >
              <Compass className="w-5 h-5" />
            </button>
            <span className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1.5 rounded-lg bg-void-surface border border-white/10 text-[10px] font-mono text-white/50 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
              QUESTS [COMING]
            </span>
          </div>

          {/* Divider */}
          <div className="w-px h-6 bg-white/10" />

          {/* Admin Toggle */}
          <button 
            onClick={() => setShowAdmin(!showAdmin)}
            className={`p-3 rounded-full border transition-all duration-300 ${
              showAdmin 
                ? 'bg-neon-gold/15 border-neon-gold/50 text-neon-gold shadow-glow-gold' 
                : 'bg-white/[0.03] border-white/[0.08] text-white/40 hover:text-white/60 hover:bg-white/[0.05]'
            }`}
          >
            <Shield className="w-5 h-5" />
          </button>
        </div>
      </motion.div>
    </div>
  )
}
