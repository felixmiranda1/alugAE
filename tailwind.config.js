/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.css',
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")], // Confirma que DaisyUI está carregado
};
