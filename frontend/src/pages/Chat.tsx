import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Send, Mic, Sparkles, MessageCircle, Brain } from 'lucide-react'
import { useCharacterStore, useChatStore } from '@/stores'
import DialogueStream from '@/components/immersive/DialogueStream'
import PresenceAvatar from '@/components/immersive/PresenceAvatar'
import { EmotionIndicator } from '@/components/chat/EmotionIndicator'
import { AdvancedSoulState, SoulStateCompact } from '@/components/chat/AdvancedSoulState'

// Welcome message component
const WelcomeMessage = ({ characterName, archetype }: { characterName: string; archetype?: string }) => {
  const getWelcomeText = () => {
    const archetypeLower = archetype?.toLowerCase() || ''
    if (archetypeLower.includes('mentor') || archetypeLower.includes('sage') || archetypeLower.includes('wise')) {
      return `The wisdom of ages stirs. ${characterName} senses your presence...`
    }
    if (archetypeLower.includes('dragon') || archetypeLower.includes('monster')) {
      return `Ancient power awakens. ${characterName} turns their gaze upon you...`
    }
    if (archetypeLower.includes('hero') || archetypeLower.includes('warrior')) {
      return `A soul of valor responds. ${characterName} stands ready...`
    }
    if (archetypeLower.includes('elf')) {
      return `Starlight glimmers as ${characterName} acknowledges your presence...`
    }
    return `The veil between worlds thins. ${characterName} awaits your words...`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.6 }}
      className="text-center py-12 px-4"
    >
      {/* Decorative element */}
      <motion.div
        animate={{ rotate: [0, 360] }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="w-16 h-16 mx-auto mb-6 rounded-full border border-white/10 flex items-center justify-center"
      >
        <Sparkles className="w-6 h-6 text-neon-purple/60" />
      </motion.div>
      
      <motion.p 
        className="font-body text-lg md:text-xl text-white/50 italic max-w-md mx-auto leading-relaxed"
        animate={{ opacity: [0.5, 0.7, 0.5] }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        {getWelcomeText()}
      </motion.p>
      
      <motion.div 
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="mt-8 mx-auto w-24 h-px bg-gradient-to-r from-transparent via-neon-purple/30 to-transparent"
      />
      
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-6 flex items-center justify-center gap-2 text-sm font-mono text-white/30"
      >
        <MessageCircle className="w-4 h-4" />
        <span>Begin your communion below</span>
      </motion.p>
    </motion.div>
  )
}

// Loading state when character is being fetched
const CharacterLoading = () => (
  <div className="w-full h-screen bg-void-black flex items-center justify-center">
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="text-center"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="w-12 h-12 mx-auto mb-4 rounded-full border border-neon-purple/30 border-t-neon-purple"
      />
      <p className="font-mono text-sm text-white/40 tracking-wider">SUMMONING...</p>
    </motion.div>
  </div>
)

export default function ChatPage() {
  const { characterId } = useParams<{ characterId: string }>()
  const navigate = useNavigate()
  
  const { selectedCharacter, fetchCharacter, isLoading: characterLoading } = useCharacterStore()
  const { 
    activeSession, 
    isTyping, 
    startSession, 
    sendMessage, 
    endSession
  } = useChatStore()
  
  const [inputValue, setInputValue] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (characterId) {
      fetchCharacter(characterId)
    }
  }, [characterId, fetchCharacter])

  useEffect(() => {
    if (selectedCharacter && !activeSession) {
      startSession(selectedCharacter.id, selectedCharacter.name)
    }
  }, [selectedCharacter, activeSession, startSession])

  const handleSend = () => {
    if (!inputValue.trim() || isTyping) return
    sendMessage(inputValue.trim())
    setInputValue('')
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleBack = () => {
    endSession()
    navigate('/')
  }

  // Loading state
  if (characterLoading || !selectedCharacter) {
    return <CharacterLoading />
  }

  const hasMessages = activeSession?.messages && activeSession.messages.length > 0

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="relative w-full h-screen bg-void-black overflow-hidden flex flex-col"
    >
      {/* Background Layer - Presence Avatar */}
      <div className="absolute inset-0 z-0">
        <PresenceAvatar 
          name={selectedCharacter.name} 
          avatarUrl={selectedCharacter.avatar_url}
          isSpeaking={isTyping}
        />
        {/* Additional atmospheric overlay */}
        <div className="absolute inset-0 bg-gradient-radial from-transparent via-void-black/30 to-void-black/70" />
      </div>

      {/* Top Navigation (Floating) */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="absolute top-6 left-6 right-6 z-50 flex items-center justify-between"
      >
        <button 
          onClick={handleBack}
          className="group flex items-center gap-3 text-white/50 hover:text-white transition-colors"
        >
          <div className="p-2.5 rounded-full glass-panel group-hover:border-white/20 transition-all">
            <ArrowLeft className="w-5 h-5" />
          </div>
          <span className="text-xs font-mono tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">
            RETURN
          </span>
        </button>
        
        {/* Character Info & Emotional State */}
        <div className="flex items-center gap-4">
          {/* Character name badge */}
          <div className="hidden md:flex items-center gap-3 px-4 py-2 rounded-full glass-panel">
            <span className="font-display text-lg text-white/80">
              {selectedCharacter.name}
            </span>
          </div>
          
          {/* Advanced Emotional State Indicator */}
          <AnimatePresence>
            {activeSession?.currentEmotionalState && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="relative"
              >
                {/* Compact view with advanced data popup */}
                <SoulStateCompact
                  emotionalState={{
                    emotion: activeSession.currentEmotionalState.emotion,
                    intensity: activeSession.currentEmotionalState.intensity,
                  }}
                  onClick={() => {
                    // Toggle expanded soul state modal/panel
                    const panel = document.getElementById('soul-state-panel')
                    if (panel) {
                      panel.classList.toggle('hidden')
                    }
                  }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Floating Soul State Panel (hidden by default) */}
      <AnimatePresence>
        {activeSession?.currentEmotionalState && (
          <motion.div
            id="soul-state-panel"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="hidden absolute top-20 right-4 z-50 w-80"
          >
            <AdvancedSoulState
              emotionalState={{
                emotion: activeSession.currentEmotionalState.emotion,
                intensity: activeSession.currentEmotionalState.intensity,
                advanced: activeSession.currentEmotionalState.advanced,
              }}
              expanded={true}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="relative z-10 flex-1 flex flex-col justify-end pb-28 md:pb-32 min-h-0">
        {/* Gradient overlay for readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-void-black via-void-black/90 to-transparent pointer-events-none" />
        
        {/* Messages or Welcome */}
        <div className="relative z-10 flex-1 min-h-0 overflow-hidden">
          <AnimatePresence mode="wait">
            {!hasMessages ? (
              <WelcomeMessage 
                key="welcome"
                characterName={selectedCharacter.name} 
                archetype={selectedCharacter.archetype}
              />
            ) : (
              <motion.div
                key="messages"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="h-full overflow-y-auto"
              >
                <DialogueStream 
                  messages={activeSession?.messages || []} 
                  isTyping={isTyping} 
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Input Area (Bottom Fixed) */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="absolute bottom-0 left-0 w-full p-4 md:p-6 z-50"
      >
        {/* Gradient fade above input */}
        <div className="absolute inset-x-0 bottom-full h-20 bg-gradient-to-t from-void-black to-transparent pointer-events-none" />
        
        <div className="max-w-3xl mx-auto relative">
          {/* Input container with glass effect */}
          <div className={`relative rounded-2xl glass-panel transition-all duration-300 ${
            isFocused ? 'border-neon-purple/30 shadow-glow-purple' : 'border-white/[0.06]'
          }`}>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Speak your thoughts..."
              disabled={isTyping}
              className="w-full bg-transparent py-4 pl-5 pr-24 text-lg font-body text-white placeholder-white/25 focus:outline-none disabled:opacity-50"
              autoFocus
            />
            
            {/* Action buttons */}
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
              {/* Voice button (decorative) */}
              <button 
                className="p-2 rounded-full text-white/20 hover:text-white/40 hover:bg-white/5 transition-all disabled:opacity-30"
                disabled
              >
                <Mic className="w-5 h-5" />
              </button>
              
              {/* Send button */}
              <button 
                onClick={handleSend}
                disabled={!inputValue.trim() || isTyping}
                className={`p-2.5 rounded-full transition-all duration-300 ${
                  inputValue.trim() && !isTyping
                    ? 'bg-neon-purple/20 text-neon-purple hover:bg-neon-purple/30 hover:shadow-glow-purple' 
                    : 'text-white/20'
                } disabled:opacity-30 disabled:cursor-not-allowed`}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          {/* Typing indicator below input */}
          <AnimatePresence>
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="absolute -top-8 left-5 flex items-center gap-2 text-xs font-mono text-neon-gold/60"
              >
                <motion.span
                  animate={{ opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  {selectedCharacter.name} is contemplating...
                </motion.span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  )
}
