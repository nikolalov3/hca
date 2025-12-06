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
        babyBlue: '#89CFF0',
        babyGreen: '#98FB98',
        bgLight: '#FFFFFF',
        babyOrange: '#FFB347',
        textDark: '#FFFFFF',
        bgDark: '#1A1A1A',
        cardDark: '#2C2C2C'
      },
    },
  },
  plugins: [],
}
