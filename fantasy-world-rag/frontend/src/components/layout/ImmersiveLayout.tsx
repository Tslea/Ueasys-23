import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'

const ImmersiveLayout = () => {
  return (
    <div className="relative min-h-screen w-full bg-void-black overflow-hidden text-gray-200 selection:bg-neon-blue selection:text-void-black">
      {/* Dynamic Background - The Void */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-void-deep via-void-black to-void-black opacity-80" />
        <div className="absolute top-0 left-0 w-full h-full bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay" />
        
        {/* Ambient Glows */}
        <motion.div 
          animate={{ opacity: [0.3, 0.5, 0.3], scale: [1, 1.1, 1] }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-neon-purple/5 rounded-full blur-[100px]"
        />
        <motion.div 
          animate={{ opacity: [0.2, 0.4, 0.2], scale: [1, 1.2, 1] }}
          transition={{ duration: 10, repeat: Infinity, delay: 2 }}
          className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] bg-neon-blue/5 rounded-full blur-[120px]"
        />
      </div>

      {/* Main Content Area */}
      <main className="relative z-10 w-full h-screen flex flex-col">
        {/* Header / Navigation Bar (Minimalist) */}
        <header className="w-full px-8 py-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse" />
            <h1 className="text-xl font-light tracking-[0.2em] text-white/80 uppercase">
              Ueasys <span className="text-xs text-white/30 ml-2">System v1.0</span>
            </h1>
          </div>
          
          {/* Status Indicators */}
          <div className="flex items-center gap-6 text-xs font-mono text-white/40">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-green-500/50 rounded-full" />
              <span>NETWORK: STABLE</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-neon-gold/50 rounded-full" />
              <span>MEMORY: ACTIVE</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-hidden relative">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default ImmersiveLayout
