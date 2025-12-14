import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Send, Mic } from 'lucide-react'
import { useCharacterStore, useChatStore } from '@/stores'
import DialogueStream from '@/components/immersive/DialogueStream'
import PresenceAvatar from '@/components/immersive/PresenceAvatar'
import { EmotionIndicator } from '@/components/chat/EmotionIndicator'

export default function ChatPage() {
  const { characterId } = useParams<{ characterId: string }>()
  const navigate = useNavigate()
  
  const { selectedCharacter, fetchCharacter } = useCharacterStore()
  const { 
    activeSession, 
    isTyping, 
    startSession, 
    sendMessage, 
    endSession
  } = useChatStore()
  
  const [inputValue, setInputValue] = useState('')
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
    if (!inputValue.trim()) return
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

  if (!selectedCharacter) return null

  return (
    <div className="relative w-full h-screen bg-void-black overflow-hidden flex flex-col">
      {/* Background Layer */}
      <div className="absolute inset-0 z-0">
        <PresenceAvatar 
          name={selectedCharacter.name} 
          avatarUrl={selectedCharacter.avatar_url}
          isSpeaking={isTyping}
        />
      </div>

      {/* Top Navigation (Floating) */}
      <div className="absolute top-8 left-8 right-8 z-50 flex items-center justify-between">
        <button 
          onClick={handleBack}
          className="group flex items-center gap-2 text-white/50 hover:text-white transition-colors"
        >
          <div className="p-2 rounded-full bg-white/5 border border-white/10 group-hover:border-white/30 transition-all">
            <ArrowLeft className="w-5 h-5" />
          </div>
          <span className="text-xs font-mono tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">
            DISCONNECT
          </span>
        </button>
        
        {/* Current Emotional State */}
        {activeSession?.currentEmotionalState && (
          <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
            <span className="text-[10px] font-mono text-white/40 uppercase tracking-widest">
              {selectedCharacter?.name}'s State
            </span>
            <EmotionIndicator
              emotion={activeSession.currentEmotionalState.emotion}
              intensity={activeSession.currentEmotionalState.intensity}
              size="sm"
              showLabel={false}
            />
          </div>
        )}
      </div>

      {/* Main Chat Area (Overlay) */}
      <div className="relative z-10 flex-1 flex flex-col justify-end pb-32 bg-gradient-to-t from-void-black via-void-black/80 to-transparent">
        <DialogueStream 
          messages={activeSession?.messages || []} 
          isTyping={isTyping} 
        />
      </div>

      {/* Input Area (Bottom Fixed) */}
      <div className="absolute bottom-0 left-0 w-full p-8 z-50 bg-gradient-to-t from-void-black via-void-black to-transparent">
        <div className="max-w-3xl mx-auto relative">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Transmit thought..."
            className="w-full bg-transparent border-b border-white/20 py-4 pl-4 pr-12 text-xl font-light text-white placeholder-white/20 focus:border-neon-blue focus:outline-none transition-colors"
            autoFocus
          />
          
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-4">
            <button className="text-white/20 hover:text-white transition-colors">
              <Mic className="w-5 h-5" />
            </button>
            <button 
              onClick={handleSend}
              disabled={!inputValue.trim()}
              className="text-neon-blue hover:text-white transition-colors disabled:opacity-30"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
