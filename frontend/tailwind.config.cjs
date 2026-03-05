/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#0b1020',
        panel: '#111a33',
      },
      boxShadow: {
        glow: '0 10px 40px rgba(59,130,246,0.25)',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
