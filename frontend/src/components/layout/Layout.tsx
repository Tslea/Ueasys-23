import { Outlet, Link, useLocation } from 'react-router-dom'
import { Sparkles, Map, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'

export default function Layout() {
  const location = useLocation()
  const { isAdmin } = useAuthStore()

  return (
    <div className="min-h-screen bg-fantasy-darker">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-gray-800 bg-fantasy-darker/90 backdrop-blur-md">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="p-2 rounded-lg bg-gradient-to-br from-fantasy-accent to-fantasy-gold group-hover:animate-glow transition-all">
              <Sparkles className="w-6 h-6 text-fantasy-darker" />
            </div>
            <div>
              <h1 className="font-fantasy text-xl text-fantasy-gold">Ueasys</h1>
              <p className="text-xs text-gray-500">Living Characters</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-6">
            <Link 
              to="/"
              className={cn(
                'text-sm font-medium transition-colors hover:text-fantasy-accent',
                location.pathname === '/' ? 'text-fantasy-accent' : 'text-gray-400'
              )}
            >
              Characters
            </Link>
            
            <Link 
              to="/map"
              className={cn(
                'text-sm font-medium transition-colors hover:text-fantasy-accent flex items-center gap-2',
                location.pathname === '/map' ? 'text-fantasy-accent' : 'text-gray-400'
              )}
            >
              <Map className="w-4 h-4" />
              World Map
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-fantasy-accent/20 text-fantasy-accent">
                Soon
              </span>
            </Link>

            {isAdmin && (
              <Link 
                to="/admin"
                className={cn(
                  'text-sm font-medium transition-colors hover:text-fantasy-accent flex items-center gap-2',
                  location.pathname.startsWith('/admin') ? 'text-fantasy-accent' : 'text-gray-400'
                )}
              >
                <Settings className="w-4 h-4" />
                Admin
              </Link>
            )}

            {!isAdmin && (
              <Link 
                to="/login"
                className="text-sm font-medium text-gray-400 hover:text-fantasy-accent transition-colors"
              >
                Login
              </Link>
            )}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-6 mt-auto">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500">
          <p>Ueasys © 2024 - Living Characters System</p>
        </div>
      </footer>
    </div>
  )
}
