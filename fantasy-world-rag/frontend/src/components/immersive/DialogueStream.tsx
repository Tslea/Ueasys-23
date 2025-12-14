import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChatMessage } from '@/stores/chatStore'
import { EmotionBadge } from '@/components/chat/EmotionIndicator'
import { KnowledgeSources, MemoryBadge } from '@/components/chat/KnowledgeSources'

interface DialogueStreamProps {
  messages: ChatMessage[]
  isTyping: boolean
}

const DialogueStream = ({ messages, isTyping }: DialogueStreamProps) => {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <div className="w-full max-w-3xl mx-auto h-full overflow-y-auto px-4 py-8 space-y-8 no-scrollbar">
      <AnimatePresence initial={false}>
        {messages.map((msg, idx) => (
          <motion.div
            key={msg.id || idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div className={`max-w-[80%] ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
              {/* Role Label */}
              <span className={`text-[10px] font-mono uppercase tracking-widest mb-1 block ${
                msg.role === 'user' ? 'text-neon-blue/50' : 'text-neon-gold/50'
              }`}>
                {msg.role === 'user' ? 'YOU' : msg.characterName || 'ENTITY'}
              </span>

              {/* Message Content */}
              <div className={`text-lg md:text-xl font-light leading-relaxed ${
                msg.role === 'user' ? 'text-white/80' : 'text-white text-glow'
              }`}>
                {msg.content}
              </div>
              
              {/* Character Engine Data - Only for assistant messages */}
              {msg.role === 'assistant' && (
                <div className="mt-3 space-y-2">
                  {/* Emotion and Memory badges */}
                  <div className="flex items-center gap-2 flex-wrap">
                    {msg.emotionalState && msg.emotionalState !== 'neutral' && (
                      <EmotionBadge 
                        emotion={msg.emotionalState} 
                        intensity={msg.emotionIntensity || 0.5} 
                      />
                    )}
                    {msg.memoryUsed && <MemoryBadge used={true} />}
                    {msg.consistencyScore !== null && msg.consistencyScore !== undefined && (
                      <span className="text-[10px] text-white/30 font-mono">
                        Consistency: {Math.round(msg.consistencyScore * 100)}%
                      </span>
                    )}
                  </div>
                  
                  {/* Knowledge sources */}
                  {msg.retrievedKnowledge && msg.retrievedKnowledge.length > 0 && (
                    <KnowledgeSources sources={msg.retrievedKnowledge} />
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Typing Indicator */}
      {isTyping && (
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }}
          className="flex items-center gap-2 text-neon-gold/50 text-xs font-mono"
        >
          <div className="w-1.5 h-1.5 bg-neon-gold rounded-full animate-bounce" />
          <div className="w-1.5 h-1.5 bg-neon-gold rounded-full animate-bounce delay-100" />
          <div className="w-1.5 h-1.5 bg-neon-gold rounded-full animate-bounce delay-200" />
          <span className="ml-2">PROCESSING THOUGHTS...</span>
        </motion.div>
      )}
      
      <div ref={bottomRef} />
    </div>
  )
}

export default DialogueStream
