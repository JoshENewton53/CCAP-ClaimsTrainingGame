/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'principal-blue': '#00d4ff',
        'principal-dark': '#1a1a2e',
        'principal-darker': '#0f3460',
      },
    },
  },
  plugins: [],
}
