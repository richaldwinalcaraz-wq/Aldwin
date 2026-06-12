import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          orange: '#F47920',
          'orange-dark': '#D4661A',
          navy: '#1B3A8A',
          'navy-dark': '#152e6e',
          'light-blue': '#7ABDE0',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
