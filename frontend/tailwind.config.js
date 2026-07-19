/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        glow: '0 20px 60px rgba(14, 165, 233, 0.22)',
      },
      backgroundImage: {
        'hero-grid':
          'radial-gradient(circle at 20% 20%, rgba(14,165,233,0.16), transparent 28%), radial-gradient(circle at 80% 0%, rgba(16,185,129,0.14), transparent 24%), linear-gradient(135deg, rgba(3,7,18,1) 0%, rgba(15,23,42,1) 55%, rgba(30,41,59,1) 100%)',
      },
    },
  },
  plugins: [],
}
