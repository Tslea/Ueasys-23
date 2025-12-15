import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'

const ImmersiveLayout = () => {
  return (
    <div className="relative min-h-screen w-full bg-void-black text-gray-200 selection:bg-neon-purple selection:text-white">
      {/* Dynamic Background - The Cosmic Void (OPTIMIZED) */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        {/* Base gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-void-black via-void-deep to-void-black" />
        
        {/* Static starfield - CSS only, no JS animations */}
        <div className="absolute inset-0 opacity-30" style={{
          backgroundImage: `radial-gradient(1px 1px at 20px 30px, white, transparent),
                           radial-gradient(1px 1px at 40px 70px, white, transparent),
                           radial-gradient(1px 1px at 50px 160px, white, transparent),
                           radial-gradient(1px 1px at 90px 40px, white, transparent),
                           radial-gradient(1px 1px at 130px 80px, white, transparent),
                           radial-gradient(1px 1px at 160px 120px, white, transparent)`,
          backgroundSize: '200px 200px'
        }} />
        
        {/* Simplified Aurora - Top (CSS animation instead of Framer) */}
        <div 
          className="absolute top-[-20%] left-[-10%] w-[60vw] h-[50vh] rounded-full blur-[100px] opacity-20 animate-pulse-slow"
          style={{
            background: 'radial-gradient(ellipse at center, rgba(178, 77, 255, 0.3) 0%, transparent 70%)',
          }}
        />
        
        {/* Simplified Aurora - Bottom Right */}
        <div 
          className="absolute bottom-[-15%] right-[-10%] w-[50vw] h-[45vh] rounded-full blur-[80px] opacity-15 animate-pulse-slow"
          style={{
            background: 'radial-gradient(ellipse at center, rgba(0, 229, 255, 0.25) 0%, transparent 70%)',
            animationDelay: '2s'
          }}
        />
        
        {/* Subtle noise texture overlay */}
        <div 
          className="absolute inset-0 opacity-[0.015] mix-blend-overlay"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* Main Content Area */}
      <main className="relative z-10 w-full min-h-screen flex flex-col">
        {/* Header / Navigation Bar */}
        <header className="w-full px-6 md:px-10 py-5 flex justify-between items-center flex-shrink-0">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-4"
          >
            {/* Logo/Brand */}
            <div className="relative">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-purple/30 to-neon-blue/30 border border-white/10 flex items-center justify-center">
                <div className="w-2 h-2 bg-neon-purple rounded-full animate-pulse" />
              </div>
              <div className="absolute inset-0 rounded-lg bg-neon-purple/20 blur-lg animate-glow-pulse" />
            </div>
            <div>
              <h1 className="font-display text-xl tracking-[0.15em] text-white/90 uppercase">
                Ueasys
              </h1>
              <span className="text-[10px] font-mono text-white/30 tracking-wider">NEXUS v1.0</span>
            </div>
          </motion.div>
          
          {/* Status Indicators */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="hidden md:flex items-center gap-6 text-[11px] font-mono text-white/40"
          >
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.05]">
              <span className="w-1.5 h-1.5 bg-neon-emerald/70 rounded-full animate-pulse" />
              <span className="tracking-wider">LINK ACTIVE</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.05]">
              <span className="w-1.5 h-1.5 bg-neon-gold/70 rounded-full animate-pulse" />
              <span className="tracking-wider">MEMORY SYNC</span>
            </div>
          </motion.div>
        </header>

        {/* Page Content */}
        <div className="flex-1 relative">
          <div className="px-6 md:px-10 pb-10">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  )
}

export default ImmersiveLayout
