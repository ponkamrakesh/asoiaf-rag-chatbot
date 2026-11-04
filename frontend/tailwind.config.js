/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        westeros: {
          950: '#07090e',
          900: '#0d1117',
          850: '#131822',
          800: '#1a202c',
          700: '#2d3748',
          gold: '#c59b27',
          goldLight: '#e6ca65',
          crimson: '#8a181a',
          parchment: '#f4ede2',
          ice: '#60a5fa',
        }
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

