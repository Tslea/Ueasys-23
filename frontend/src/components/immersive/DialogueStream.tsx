import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChatMessage } from '@/stores/chatStore'
import { EmotionBadge } from '@/components/chat/EmotionIndicator'
import { KnowledgeSources, MemoryBadge } from '@/components/chat/KnowledgeSources'
import { User, Sparkles } from 'lucide-react'

interface DialogueStreamProps {
  messages: ChatMessage[]
  isTyping: boolean
}

// Elegant typing indicator
const TypingIndicator = ({ characterName }: { characterName?: string }) => (
  <motion.div 
    initial={{ opacity: 0, y: 10 }} 
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="flex items-start gap-3"
  >
    {/* Character indicator */}
    <div className="w-8 h-8 rounded-full bg-neon-purple/10 border border-neon-purple/20 flex items-center justify-center flex-shrink-0">
      <Sparkles className="w-4 h-4 text-neon-purple/60" />
    </div>
    
    <div className="flex flex-col gap-2">
      <span className="text-[10px] font-mono text-neon-gold/50 uppercase tracking-widest">
        {characterName || 'Entity'}
      </span>
      <div className="flex items-center gap-1.5 px-4 py-3 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2 h-2 rounded-full bg-neon-gold/60"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [0.4, 1, 0.4],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </div>
  </motion.div>
)

const DialogueStream = ({ messages, isTyping }: DialogueStreamProps) => {
  const bottomRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const lastCharacterName = messages.filter(m => m.role === 'assistant').pop()?.characterName

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <div 
      ref={containerRef}
      className="w-full max-w-3xl mx-auto h-full overflow-y-auto px-4 md:px-6 py-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent"
    >
      <AnimatePresence initial={false} mode="popLayout">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user'
          
          return (
            <motion.div
              key={msg.id || idx}
              initial={{ opacity: 0, y: 15, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              layout
              className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar indicator */}
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                isUser 
                  ? 'bg-neon-blue/10 border border-neon-blue/20' 
                  : 'bg-neon-purple/10 border border-neon-purple/20'
              }`}>
                {isUser ? (
                  <User className="w-4 h-4 text-neon-blue/60" />
                ) : (
                  <Sparkles className="w-4 h-4 text-neon-purple/60" />
                )}
              </div>

              {/* Message bubble */}
              <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Role Label */}
                <span className={`text-[10px] font-mono uppercase tracking-widest mb-1.5 ${
                  isUser ? 'text-neon-blue/50' : 'text-neon-gold/50'
                }`}>
                  {isUser ? 'You' : msg.characterName || 'Entity'}
                </span>

                {/* Message Content */}
                <div className={`relative px-4 py-3 rounded-2xl ${
                  isUser 
                    ? 'bg-neon-blue/[0.08] border border-neon-blue/10 text-white/80' 
                    : 'bg-white/[0.03] border border-white/[0.06] text-white/90'
                }`}>
                  <p className={`text-base md:text-lg font-body leading-relaxed ${
                    !isUser ? 'text-glow' : ''
                  }`}>
                    {msg.content}
                  </p>
                </div>
                
                {/* Character Engine Data - Only for assistant messages */}
                {!isUser && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="mt-2 space-y-2"
                  >
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
                        <span className="text-[9px] text-white/25 font-mono px-2 py-0.5 rounded-full bg-white/[0.02]">
                          ✓ {Math.round(msg.consistencyScore * 100)}%
                        </span>
                      )}
                    </div>
                    
                    {/* Knowledge sources */}
                    {msg.retrievedKnowledge && msg.retrievedKnowledge.length > 0 && (
                      <KnowledgeSources sources={msg.retrievedKnowledge} />
                    )}
                  </motion.div>
                )}
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>

      {/* Typing Indicator */}
      <AnimatePresence>
        {isTyping && (
          <TypingIndicator characterName={lastCharacterName} />
        )}
      </AnimatePresence>
      
      <div ref={bottomRef} className="h-4" />
    </div>
  )
}

export default DialogueStream
