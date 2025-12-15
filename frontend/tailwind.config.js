/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Void Theme - Deep immersive darkness
        void: {
          black: '#030304',
          deep: '#080809',
          surface: '#0f1011',
          highlight: '#1a1b1d',
          muted: '#2a2b2e',
        },
        // Mystical Neon Accents
        neon: {
          blue: '#00e5ff',
          purple: '#b24dff',
          gold: '#ffb830',
          emerald: '#00ff9d',
          rose: '#ff4d6d',
          cyan: '#00d4ff',
        },
        // Fantasy Palette
        fantasy: {
          dark: '#12121a',
          shadow: '#1a1825',
          mist: '#c8d4ff',
          ember: '#ff7832',
          ice: '#a8e0ff',
          arcane: '#9945ff',
          dragon: '#ff3d3d',
          forest: '#2dd4a0',
        },
        // Glass effects
        glass: {
          light: 'rgba(255, 255, 255, 0.05)',
          medium: 'rgba(255, 255, 255, 0.08)',
          border: 'rgba(255, 255, 255, 0.06)',
        },
      },
      fontFamily: {
        display: ['Cormorant', 'Georgia', 'serif'],
        body: ['Crimson Pro', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      fontSize: {
        'display-xl': ['4.5rem', { lineHeight: '1.1', letterSpacing: '0.02em' }],
        'display-lg': ['3.5rem', { lineHeight: '1.15', letterSpacing: '0.02em' }],
        'display-md': ['2.5rem', { lineHeight: '1.2', letterSpacing: '0.02em' }],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(var(--tw-gradient-stops))',
        'mystical': 'linear-gradient(135deg, rgba(178, 77, 255, 0.1) 0%, rgba(0, 229, 255, 0.05) 50%, rgba(255, 184, 48, 0.1) 100%)',
        'void-gradient': 'linear-gradient(180deg, #030304 0%, #0f1011 50%, #030304 100%)',
      },
      boxShadow: {
        'glow-blue': '0 0 20px rgba(0, 229, 255, 0.3), 0 0 40px rgba(0, 229, 255, 0.1)',
        'glow-purple': '0 0 20px rgba(178, 77, 255, 0.3), 0 0 40px rgba(178, 77, 255, 0.1)',
        'glow-gold': '0 0 20px rgba(255, 184, 48, 0.3), 0 0 40px rgba(255, 184, 48, 0.1)',
        'inner-glow': 'inset 0 0 30px rgba(255, 255, 255, 0.05)',
        'mystical': '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 60px rgba(178, 77, 255, 0.1)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        'glow': 'glow 3s ease-in-out infinite',
        'glow-pulse': 'glow-pulse 4s ease-in-out infinite',
        'shimmer': 'shimmer 3s linear infinite',
        'breathe': 'breathe 4s ease-in-out infinite',
        'spin-slow': 'spin 8s linear infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(178, 77, 255, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(178, 77, 255, 0.6), 0 0 60px rgba(0, 229, 255, 0.3)' },
        },
        'glow-pulse': {
          '0%, 100%': { opacity: '0.5', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        breathe: {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.8' },
          '50%': { transform: 'scale(1.02)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      backdropBlur: {
        'xs': '2px',
      },
      transitionDuration: {
        '400': '400ms',
      },
    },
  },
  plugins: [],
}
