/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Hockey theme colors
        hockey: {
          blue: '#003f7f',
          'blue-light': '#1e5a96',
          'blue-dark': '#002855',
          ice: '#e6f3ff',
          'ice-light': '#f0f8ff',
          red: '#c41e3a',
          'red-light': '#d63456',
          'red-dark': '#a01729',
        },
        // Enhanced neutrals
        neutral: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-subtle': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounce 1s infinite',
        'typing': 'typing 1.5s ease-in-out infinite',
      },
      keyframes: {
        typing: {
          '0%, 60%': { opacity: '1' },
          '30%': { opacity: '0' },
        }
      },
      maxWidth: {
        'chat': '768px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      }
    },
  },
  plugins: [],
}
