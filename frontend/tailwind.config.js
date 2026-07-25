/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Geist', 'sans-serif'],
        display: ['Special Elite', 'serif'],
      },
      colors: {
        wandor: {
          dark: '#0a0a0a',
          text: '#1a1a1a',
          muted: '#767676',
          prompt: '#905831',
        },
      },
      typography: ({ theme }) => ({
        wandor: {
          css: {
            '--tw-prose-body': theme('colors.wandor.text'),
            '--tw-prose-headings': theme('colors.wandor.text'),
            '--tw-prose-links': theme('colors.wandor.prompt'),
            '--tw-prose-bold': theme('colors.wandor.text'),
            '--tw-prose-bullets': theme('colors.wandor.muted'),
            '--tw-prose-th-borders': 'rgba(0,0,0,0.1)',
            '--tw-prose-td-borders': 'rgba(0,0,0,0.08)',
            fontFamily: theme('fontFamily.sans').join(', '),
            a: { fontWeight: '500', textDecoration: 'underline', textUnderlineOffset: '2px' },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
