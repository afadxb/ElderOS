import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        elder: {
          critical: '#DC2626',
          warning: '#D97706',
          ok: '#16A34A',
          action: '#2563EB',
          'critical-bg': '#FEF2F2',
          'warning-bg': '#FFFBEB',
          'ok-bg': '#F0FDF4',
          'action-bg': '#EFF6FF',
          surface: '#FFFFFF',
          'surface-alt': '#F9FAFB',
          border: '#E5E7EB',
          'text-primary': '#111827',
          'text-secondary': '#6B7280',
          'text-muted': '#9CA3AF',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        'room-number': ['3rem', { lineHeight: '1', fontWeight: '700' }],
        'alert-title': ['1.5rem', { lineHeight: '1.2', fontWeight: '600' }],
      },
      spacing: {
        'sidebar-w': '16rem',
        'sidebar-collapsed': '4rem',
        'bottom-nav': '4rem',
        'topbar-h': '3.5rem',
      },
      animation: {
        'pulse-critical': 'pulse 1.5s ease-in-out infinite',
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
