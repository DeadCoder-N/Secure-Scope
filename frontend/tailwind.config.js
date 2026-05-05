/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'surface':   '#111118',
        'surface-2': '#1a1a24',
        'slate-950': '#020617',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'glow-cyan': 'radial-gradient(ellipse at center, rgba(6,182,212,0.07) 0%, transparent 70%)',
      },
    },
  },
  plugins: [],
};
