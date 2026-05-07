import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './hooks/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // === Design tokens (dark amber theme) ===
        primary: {
          DEFAULT: '#FFB000',
          container: 'rgba(255,176,0,0.12)',
          soft: 'rgba(255,176,0,0.08)',
          glow: 'rgba(255,176,0,0.22)',
        },
        surface: {
          DEFAULT: '#09090e',
          low: '#0f0f18',
          variant: 'rgba(255,255,255,0.06)',
          container: 'rgba(255,176,0,0.06)',
          elevated: '#16161f',
        },
        'on-surface': '#ede8f5',
        'on-surface-variant': '#b8b0cc',
        'outline-variant': 'rgba(255,255,255,0.10)',
        amber: {
          DEFAULT: '#FFB000',
          soft: 'rgba(255,176,0,0.08)',
          glow: 'rgba(255,176,0,0.22)',
        },
        bg: {
          DEFAULT: '#09090e',
          surface: '#0f0f18',
          elevated: '#16161f',
        },
        border: {
          DEFAULT: 'rgba(255,255,255,0.08)',
          strong: 'rgba(255,255,255,0.15)',
        },
        text: {
          primary: '#ede8f5',
          muted: '#b8b0cc',
          dim: '#6b6480',
        },
      },
      fontFamily: {
        jakarta: ['var(--font-jakarta)', 'Plus Jakarta Sans', 'sans-serif'],
        grotesk: ['var(--font-space-grotesk)', 'sans-serif'],
        jetbrains: ['var(--font-jetbrains)', 'sans-serif'],
        rubik: ['var(--font-jetbrains)', 'sans-serif'],
        playfair: ['var(--font-jakarta)', 'Plus Jakarta Sans', 'sans-serif'],
        goldman: ['var(--font-goldman)', 'sans-serif'],
      },
      spacing: {
        '4.5': '1.125rem',
      },
      borderRadius: {
        none:    '0px',
        sm:      '6px',
        DEFAULT: '12px',
        md:      '16px',
        lg:      '20px',
        xl:      '28px',
        '2xl':   '32px',
        '3xl':   '48px',
        full:    '9999px',
      },
      boxShadow: {
        'primary-sm':  '0 2px 8px rgba(103,75,181,0.12)',
        'primary-md':  '0 4px 20px rgba(103,75,181,0.16)',
        'primary-lg':  '0 8px 40px rgba(103,75,181,0.20)',
        'glass':       '0 4px 24px rgba(103,75,181,0.08)',
        'glass-hover': '0 8px 32px rgba(103,75,181,0.14)',
      },
    },
  },
  plugins: [],
}

export default config
