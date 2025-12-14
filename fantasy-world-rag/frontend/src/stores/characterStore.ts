import { create } from 'zustand'

// Character types matching backend models
export interface CharacterPersonality {
  traits: string[]
  values: string[]
  fears: string[]
  desires: string[]
  speaking_style: string
  quirks: string[]
}

export interface CharacterBackground {
  origin: string
  history: string
  key_events: string[]
  relationships: Record<string, string>
}

export interface CharacterKnowledge {
  expertise: string[]
  secrets: string[]
  beliefs: string[]
  opinions: Record<string, string>
}

export interface CharacterBehavior {
  goals: string[]
  motivations: string[]
  reactions: Record<string, string>
  decision_patterns: string[]
}

export interface Character {
  id: string
  name: string
  title?: string
  description?: string
  archetype: string
  alignment: string
  status: string
  avatar_url?: string
  
  personality: Record<string, any>
  speaking_style: Record<string, any>
  background: Record<string, any>
  
  // Legacy compatibility
  race?: string
  class_type?: string
  is_active?: boolean
  
  created_at: string
  updated_at: string
}

export interface CharacterDraft {
  name: string
  title?: string
  description: string
  archetype: string
  alignment: string
  avatar_url: string
  
  personality: Record<string, any>
  speaking_style: Record<string, any>
  background: Record<string, any>
}

interface CharacterState {
  characters: Character[]
  selectedCharacter: Character | null
  draft: CharacterDraft
  isLoading: boolean
  error: string | null
  
  // Actions
  fetchCharacters: () => Promise<void>
  fetchCharacter: (id: string) => Promise<void>
  createCharacter: (character: CharacterDraft) => Promise<Character>
  updateCharacter: (id: string, updates: Partial<CharacterDraft>) => Promise<void>
  deleteCharacter: (id: string) => Promise<void>
  
  // Draft management
  setDraft: (draft: Partial<CharacterDraft>) => void
  updateDraftSection: <K extends keyof CharacterDraft>(
    section: K, 
    data: CharacterDraft[K]
  ) => void
  resetDraft: () => void
  populateDraftFromAI: (extracted: Partial<CharacterDraft>) => void
  
  // Selection
  selectCharacter: (character: Character | null) => void
  clearError: () => void
}

const initialDraft: CharacterDraft = {
  name: '',
  title: '',
  description: '',
  archetype: 'hero',
  alignment: 'true_neutral',
  avatar_url: '',
  personality: {},
  speaking_style: {},
  background: {}
}

// API Base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useCharacterStore = create<CharacterState>((set) => ({
  characters: [],
  selectedCharacter: null,
  draft: { ...initialDraft },
  isLoading: false,
  error: null,

  fetchCharacters: async () => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/characters`)
      if (!response.ok) throw new Error('Failed to fetch characters')
      
      const data = await response.json()
      // Handle paginated response from backend
      const characters = data.items || data
      set({ characters, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch characters',
        isLoading: false
      })
    }
  },

  fetchCharacter: async (id: string) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/characters/${id}`)
      if (!response.ok) throw new Error('Character not found')
      
      const data = await response.json()
      set({ selectedCharacter: data, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch character',
        isLoading: false
      })
    }
  },

  createCharacter: async (character: CharacterDraft) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/characters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(character)
      })
      
      if (!response.ok) throw new Error('Failed to create character')
      
      const newCharacter = await response.json()
      
      set(state => ({
        characters: [...state.characters, newCharacter],
        isLoading: false
      }))
      
      return newCharacter
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create character',
        isLoading: false
      })
      throw error
    }
  },

  updateCharacter: async (id: string, updates: Partial<CharacterDraft>) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/characters/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      
      if (!response.ok) throw new Error('Failed to update character')
      
      const updated = await response.json()
      
      set(state => ({
        characters: state.characters.map(c => c.id === id ? updated : c),
        selectedCharacter: state.selectedCharacter?.id === id ? updated : state.selectedCharacter,
        isLoading: false
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update character',
        isLoading: false
      })
      throw error
    }
  },

  deleteCharacter: async (id: string) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/characters/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Failed to delete character')
      
      set(state => ({
        characters: state.characters.filter(c => c.id !== id),
        selectedCharacter: state.selectedCharacter?.id === id ? null : state.selectedCharacter,
        isLoading: false
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete character',
        isLoading: false
      })
      throw error
    }
  },

  setDraft: (draft: Partial<CharacterDraft>) => {
    set(state => ({
      draft: { ...state.draft, ...draft }
    }))
  },

  updateDraftSection: <K extends keyof CharacterDraft>(
    section: K,
    data: CharacterDraft[K]
  ) => {
    set(state => ({
      draft: { ...state.draft, [section]: data }
    }))
  },

  resetDraft: () => {
    set({ draft: { ...initialDraft } })
  },

  populateDraftFromAI: (extracted: Partial<CharacterDraft>) => {
    set(state => ({
      draft: {
        ...state.draft,
        ...extracted,
        personality: { ...state.draft.personality, ...(extracted.personality || {}) },
        speaking_style: { ...state.draft.speaking_style, ...(extracted.speaking_style || {}) },
        background: { ...state.draft.background, ...(extracted.background || {}) }
      }
    }))
  },

  selectCharacter: (character: Character | null) => {
    set({ selectedCharacter: character })
  },

  clearError: () => set({ error: null })
}))
