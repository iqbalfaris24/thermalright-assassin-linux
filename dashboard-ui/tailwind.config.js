/** @type {import('tailwindcss').Config} */
export default {
 content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        'navy-blue': '#002F5D',
        'dark-blue': '#014475',
        slate: {
          850: '#151f32',
          900: '#0f172a',
          950: '#0b0f19',
        }
      },
    },
  },
  // plugins: [require('daisyui')],
  
}

