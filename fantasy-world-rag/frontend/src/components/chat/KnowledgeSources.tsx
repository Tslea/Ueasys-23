import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface KnowledgeSourcesProps {
  sources: string[]
  className?: string
  maxVisible?: number
}

export function KnowledgeSources({
  sources,
  className,
  maxVisible = 2,
}: KnowledgeSourcesProps) {
  const [expanded, setExpanded] = useState(false)
  
  if (!sources || sources.length === 0) {
    return null
  }
  
  const visibleSources = expanded ? sources : sources.slice(0, maxVisible)
  const hiddenCount = sources.length - maxVisible
  
  return (
    <div className={cn('mt-2', className)}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs text-white/40 hover:text-white/60 transition-colors"
      >
        <span className="text-amber-400">📚</span>
        <span>Knowledge sources ({sources.length})</span>
        {hiddenCount > 0 && !expanded && (
          <span className="text-white/30">+{hiddenCount} more</span>
        )}
        <motion.span
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▼
        </motion.span>
      </button>
      
      <AnimatePresence>
        {(expanded || visibleSources.length > 0) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-2 space-y-1"
          >
            {visibleSources.map((source, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={cn(
                  'text-xs p-2 rounded-lg',
                  'bg-white/5 border border-white/10',
                  'text-white/60'
                )}
              >
                <div className="flex items-start gap-2">
                  <span className="text-amber-400/60 mt-0.5">◈</span>
                  <p className="flex-1 line-clamp-3">{source}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Compact badge for showing knowledge was used
export function MemoryBadge({ 
  used, 
  className 
}: { 
  used: boolean
  className?: string 
}) {
  if (!used) return null
  
  return (
    <motion.span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs',
        'bg-amber-500/10 border border-amber-500/20',
        'text-amber-400/70',
        className
      )}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <span>📚</span>
      <span>Memory</span>
    </motion.span>
  )
}
