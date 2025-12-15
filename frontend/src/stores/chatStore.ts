import { create } from 'zustand'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  characterId?: string
  characterName?: string
  // Character Engine integration
  emotionalState?: string
  emotionIntensity?: number
  retrievedKnowledge?: string[]
  memoryUsed?: boolean
  consistencyScore?: number | null
}

export interface EmotionalStateInfo {
  emotion: string
  intensity: number
  description: string
  // Advanced emotional system data
  advanced?: {
    emotion: string
    emotion_confidence?: number
    valence: number
    arousal: number
    dominance: number
    dominant_system?: string
    system_intensity?: number
    all_systems?: Record<string, number>
  }
}

export interface ChatSession {
  id: string
  characterId: string
  characterName: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
  // Track current emotional state
  currentEmotionalState?: EmotionalStateInfo
}

interface ChatState {
  sessions: ChatSession[]
  activeSession: ChatSession | null
  isConnected: boolean
  isTyping: boolean
  error: string | null
  
  // WebSocket
  socket: WebSocket | null
  
  // Actions
  startSession: (characterId: string, characterName: string) => void
  sendMessage: (content: string) => void
  sendViaRest: (content: string) => Promise<void>
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  endSession: () => void
  clearHistory: () => void
  
  // WebSocket management
  connect: (characterId: string) => void
  disconnect: () => void
  setTyping: (typing: boolean) => void
  clearError: () => void
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WS_BASE = API_BASE.replace('http', 'ws')

// Helper function to get emotion description
function getEmotionDescription(emotion: string, intensity: number): string {
  const intensityLabel = intensity > 0.7 ? 'strongly' : intensity > 0.4 ? 'moderately' : 'slightly'
  const emotionLabels: Record<string, string> = {
    joy: 'joyful',
    sadness: 'sad',
    anger: 'angry',
    fear: 'fearful',
    surprise: 'surprised',
    disgust: 'disgusted',
    trust: 'trusting',
    anticipation: 'anticipating',
    neutral: 'neutral',
    curiosity: 'curious',
    admiration: 'admiring',
    contempt: 'contemptuous',
    hope: 'hopeful',
    pride: 'proud',
    shame: 'ashamed',
    guilt: 'guilty',
    envy: 'envious',
    gratitude: 'grateful',
    serenity: 'serene',
    interest: 'interested',
    amusement: 'amused',
    awe: 'awed',
  }
  const emotionLabel = emotionLabels[emotion?.toLowerCase()] || emotion || 'neutral'
  return emotion === 'neutral' ? 'Neutral' : `Feeling ${intensityLabel} ${emotionLabel}`
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSession: null,
  isConnected: false,
  isTyping: false,
  error: null,
  socket: null,

  startSession: (characterId: string, characterName: string) => {
    const session: ChatSession = {
      id: `session-${Date.now()}`,
      characterId,
      characterName,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    }
    
    set(state => ({
      sessions: [...state.sessions, session],
      activeSession: session
    }))
    
    // Connect WebSocket
    get().connect(characterId)
  },

  sendMessage: (content: string) => {
    const { socket, activeSession, isConnected } = get()
    
    if (!activeSession) {
      set({ error: 'No active chat session' })
      return
    }
    
    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
      characterId: activeSession.characterId
    }
    
    set(state => ({
      activeSession: state.activeSession ? {
        ...state.activeSession,
        messages: [...state.activeSession.messages, userMessage],
        updatedAt: new Date()
      } : null
    }))
    
    // Send via WebSocket if connected
    if (socket && isConnected) {
      socket.send(JSON.stringify({
        type: 'message',
        content,
        character_id: activeSession.characterId
      }))
      set({ isTyping: true })
    } else {
      // Fallback to REST API
      get().sendViaRest(content)
    }
  },

  // Internal REST fallback
  sendViaRest: async (content: string) => {
    const { activeSession } = get()
    if (!activeSession) return
    
    set({ isTyping: true })
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/chat/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: activeSession.characterId,
          message: content,
          context: activeSession.messages.slice(-10).map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      })
      
      if (!response.ok) throw new Error('Failed to send message')
      
      const data = await response.json()
      
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        characterId: activeSession.characterId,
        characterName: activeSession.characterName,
        // Character Engine data
        emotionalState: data.emotional_state,
        emotionIntensity: data.emotion_intensity,
        retrievedKnowledge: data.retrieved_knowledge,
        memoryUsed: data.memory_used,
        consistencyScore: data.consistency_score
      }
      
      // Update emotional state for session
      const emotionalStateInfo: EmotionalStateInfo = {
        emotion: data.emotional_state || 'neutral',
        intensity: data.emotion_intensity || 0.5,
        description: getEmotionDescription(data.emotional_state, data.emotion_intensity),
        // Include advanced emotional data if available
        advanced: data.advanced_emotions || data.metadata?.advanced_emotions,
      }
      
      set(state => ({
        activeSession: state.activeSession ? {
          ...state.activeSession,
          messages: [...state.activeSession.messages, assistantMessage],
          updatedAt: new Date(),
          currentEmotionalState: emotionalStateInfo
        } : null,
        isTyping: false
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to send message',
        isTyping: false
      })
    }
  },

  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const fullMessage: ChatMessage = {
      ...message,
      id: `msg-${Date.now()}`,
      timestamp: new Date()
    }
    
    set(state => ({
      activeSession: state.activeSession ? {
        ...state.activeSession,
        messages: [...state.activeSession.messages, fullMessage],
        updatedAt: new Date()
      } : null
    }))
  },

  endSession: () => {
    get().disconnect()
    set(state => ({
      sessions: state.activeSession 
        ? state.sessions.map(s => 
            s.id === state.activeSession?.id ? state.activeSession : s
          )
        : state.sessions,
      activeSession: null
    }))
  },

  clearHistory: () => {
    set(state => ({
      activeSession: state.activeSession ? {
        ...state.activeSession,
        messages: []
      } : null
    }))
  },

  connect: (characterId: string) => {
    const { socket } = get()
    
    // Close existing connection
    if (socket) {
      socket.close()
    }
    
    try {
      const ws = new WebSocket(`${WS_BASE}/api/v1/chat/ws/${characterId}`)
      
      ws.onopen = () => {
        set({ isConnected: true, socket: ws })
        console.log('WebSocket connected')
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'response') {
            const assistantMessage: ChatMessage = {
              id: `msg-${Date.now()}`,
              role: 'assistant',
              content: data.content,
              timestamp: new Date(),
              characterId,
              characterName: data.character_name,
              // Character Engine data
              emotionalState: data.emotional_state,
              emotionIntensity: data.emotion_intensity,
              retrievedKnowledge: data.retrieved_knowledge,
              memoryUsed: data.memory_used,
              consistencyScore: data.consistency_score
            }
            
            // Update emotional state for session
            const emotionalStateInfo: EmotionalStateInfo = {
              emotion: data.emotional_state || 'neutral',
              intensity: data.emotion_intensity || 0.5,
              description: getEmotionDescription(data.emotional_state, data.emotion_intensity),
              // Include advanced emotional data if available
              advanced: data.advanced_emotions || data.metadata?.advanced_emotions,
            }
            
            set(state => ({
              activeSession: state.activeSession ? {
                ...state.activeSession,
                messages: [...state.activeSession.messages, assistantMessage],
                updatedAt: new Date(),
                currentEmotionalState: emotionalStateInfo
              } : null,
              isTyping: false
            }))
          } else if (data.type === 'typing') {
            set({ isTyping: data.is_typing !== false })
          } else if (data.type === 'error') {
            set({ error: data.message || data.content, isTyping: false })
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        set({ error: 'Connection error', isConnected: false })
      }
      
      ws.onclose = () => {
        set({ isConnected: false, socket: null })
        console.log('WebSocket disconnected')
      }
      
      set({ socket: ws })
    } catch (error) {
      set({ error: 'Failed to connect', isConnected: false })
    }
  },

  disconnect: () => {
    const { socket } = get()
    if (socket) {
      socket.close()
      set({ socket: null, isConnected: false })
    }
  },

  setTyping: (typing: boolean) => set({ isTyping: typing }),
  
  clearError: () => set({ error: null })
}))
