import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user'
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isAdmin: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

// Simulated admin credentials (in production, this would be API-based)
const ADMIN_CREDENTIALS = {
  email: 'admin@fantasy.world',
  password: 'fantasy123',
  user: {
    id: '1',
    name: 'Admin',
    email: 'admin@fantasy.world',
    role: 'admin' as const
  }
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isAdmin: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          // Simulate API call delay
          await new Promise(resolve => setTimeout(resolve, 800))
          
          // Simple auth check (replace with actual API in production)
          if (email === ADMIN_CREDENTIALS.email && password === ADMIN_CREDENTIALS.password) {
            const token = btoa(`${email}:${Date.now()}`) // Simple token generation
            
            set({
              user: ADMIN_CREDENTIALS.user,
              token,
              isAuthenticated: true,
              isAdmin: true,
              isLoading: false
            })
          } else {
            throw new Error('Invalid credentials')
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false
          })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isAdmin: false
        })
      },

      checkAuth: async () => {
        const { token, user } = get()
        
        if (!token || !user) {
          set({ isAuthenticated: false, isAdmin: false })
          return
        }
        
        // In production, validate token with API
        set({ isAuthenticated: true, isAdmin: user.role === 'admin' })
      },

      clearError: () => set({ error: null })
    }),
    {
      name: 'fantasy-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        isAdmin: state.isAdmin
      })
    }
  )
)
