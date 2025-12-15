import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { ImmersiveLayout, AdminLayout } from './components/layout'
import { Home, Login, Chat } from './pages'
import { Dashboard, CharacterCreator, CharactersList, CharacterKnowledge } from './pages/admin'
import ProtectedRoute from './components/auth/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#050505',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
      />
      <Routes>
        {/* Public Routes - Now using ImmersiveLayout */}
        <Route path="/" element={<ImmersiveLayout />}>
          <Route index element={<Home />} />
        </Route>
        
        {/* Chat Route - Full screen, no layout wrapper (or maybe we want ImmersiveLayout here too?) 
            For now, keeping it separate as requested, but we might want to wrap it later.
            Actually, the design concept says "The Presence" is a view. 
            If Chat is a separate route, it might need its own layout or just be a page.
            Let's keep it as is for now, but we will redesign Chat.tsx later.
        */}
        <Route path="/chat/:characterId" element={<Chat />} />
        
        {/* Auth */}
        <Route path="/login" element={<Login />} />
        
        {/* Admin Routes */}
        <Route 
          path="/admin" 
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="characters" element={<CharactersList />} />
          <Route path="characters/new" element={<CharacterCreator />} />
          <Route path="characters/:id/edit" element={<CharacterCreator />} />
          <Route path="characters/:characterId/knowledge" element={<CharacterKnowledge />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
