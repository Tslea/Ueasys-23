import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { 
  Sparkles, 
  LayoutDashboard, 
  Users, 
  Plus, 
  Database,
  Settings,
  LogOut,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'

const sidebarLinks = [
  { 
    name: 'Dashboard', 
    path: '/admin', 
    icon: LayoutDashboard,
    exact: true 
  },
  { 
    name: 'Characters', 
    path: '/admin/characters', 
    icon: Users,
    children: [
      { name: 'All Characters', path: '/admin/characters' },
      { name: 'Create New', path: '/admin/characters/new' },
    ]
  },
  { 
    name: 'Knowledge Base', 
    path: '/admin/knowledge', 
    icon: Database 
  },
  { 
    name: 'Settings', 
    path: '/admin/settings', 
    icon: Settings 
  },
]

export default function AdminLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-void-black flex text-gray-300">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/10 bg-void-deep flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-white/10">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="p-2 rounded-lg bg-gradient-to-br from-neon-blue to-neon-purple">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-mono text-lg text-neon-blue tracking-wider">UEASYS</h1>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest">Admin Console</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {sidebarLinks.map((link) => {
            const Icon = link.icon
            const isActive = link.exact 
              ? location.pathname === link.path
              : location.pathname.startsWith(link.path)

            return (
              <div key={link.path}>
                <Link
                  to={link.path}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all',
                    isActive 
                      ? 'bg-neon-blue/10 text-neon-blue border border-neon-blue/20' 
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium text-sm">{link.name}</span>
                  {link.children && (
                    <ChevronRight className={cn(
                      'w-4 h-4 ml-auto transition-transform',
                      isActive && 'rotate-90'
                    )} />
                  )}
                </Link>
                
                {/* Sub-links */}
                {link.children && isActive && (
                  <div className="ml-8 mt-1 space-y-1">
                    {link.children.map((child) => (
                      <Link
                        key={child.path}
                        to={child.path}
                        className={cn(
                          'block px-3 py-2 text-xs rounded-lg transition-all',
                          location.pathname === child.path
                            ? 'text-neon-blue bg-neon-blue/5'
                            : 'text-gray-500 hover:text-gray-300'
                        )}
                      >
                        {child.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </nav>

        {/* Quick Actions */}
        <div className="p-4 border-t border-white/10">
          <Link
            to="/admin/characters/new"
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg bg-white/5 border border-white/10 text-white font-semibold hover:bg-neon-blue/10 hover:border-neon-blue/50 hover:text-neon-blue transition-all"
          >
            <Plus className="w-5 h-5" />
            <span className="text-sm">New Entity</span>
          </Link>
        </div>

        {/* User */}
        <div className="p-4 border-t border-white/10">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-white">{user?.name || 'Admin'}</p>
              <p className="text-xs text-gray-500">{user?.email || 'System Access'}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg hover:bg-red-900/30 text-gray-400 hover:text-red-400 transition-all"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-void-black">
        {/* Top Bar */}
        <header className="h-16 border-b border-white/10 bg-void-deep/50 flex items-center px-6">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Link to="/admin" className="hover:text-white transition-colors">
              Console
            </Link>
            {location.pathname !== '/admin' && (
              <>
                <ChevronRight className="w-4 h-4" />
                <span className="text-neon-blue uppercase tracking-wider text-xs">
                  {location.pathname.split('/').pop()?.replace(/-/g, ' ')}
                </span>
              </>
            )}
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
