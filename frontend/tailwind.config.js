/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef9fa',
          100: '#d5f0f2',
          200: '#aee0e5',
          300: '#7ad0d9',
          400: '#23ced9', 
          500: '#14abb5', 
          600: '#097c87',
          700: '#0b636d',
          800: '#0f5058',
          900: '#114249',
          950: '#072b31',
        },
        accent: {
          peach: '#fca47c',
          yellow: '#f9d779',
          green: '#a1cca5',
        },
        navy: {
          800: '#0f172a',
          850: '#0c1322',
          900: '#080d1a',
          950: '#040711',
        },
        success: { 50: '#f0f7f1', 500: '#a1cca5', 600: '#8abf8f', 700: '#73b279' },
        warning: { 50: '#fffbf0', 500: '#f9d779', 600: '#f7cb52', 700: '#f5bf2b' },
        danger: { 50: '#fff4ef', 500: '#fca47c', 600: '#fb8b55', 700: '#fa722e' }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 20px -5px rgba(35, 206, 217, 0.4)',
        'glow-success': '0 0 20px -5px rgba(16, 185, 129, 0.4)',
        'glow-danger': '0 0 20px -5px rgba(239, 68, 68, 0.4)',
        'card': '0 4px 20px 0 rgba(0, 0, 0, 0.05)',
        'card-hover': '0 10px 30px -5px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(12px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [],
}

