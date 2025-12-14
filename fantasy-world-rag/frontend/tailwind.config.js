/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Fantasy theme colors
        primary: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#e879f9',
          500: '#d946ef',
          600: '#c026d3',
          700: '#a21caf',
          800: '#86198f',
          900: '#701a75',
          950: '#4a044e',
        },
        fantasy: {
          dark: '#1a1a2e',
          darker: '#0f0f1a',
          accent: '#eab308',
          gold: '#fbbf24',
          silver: '#94a3b8',
          bronze: '#cd7f32',
        },
        // Ueasys Void Theme
        void: {
          black: '#050505',
          deep: '#0a0a0a',
          surface: '#121212',
          highlight: '#1a1a1a',
        },
        neon: {
          blue: '#00f3ff',
          purple: '#bc13fe',
          gold: '#ffd700',
          red: '#ff003c',
        }
      },
      fontFamily: {
        fantasy: ['Cinzel', 'serif'],
        body: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'parchment': "url('/textures/parchment.png')",
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(234, 179, 8, 0.5)' },
          '50%': { boxShadow: '0 0 20px rgba(234, 179, 8, 0.8)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
