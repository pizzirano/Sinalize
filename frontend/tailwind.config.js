/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class', 'html'],
  content: [
    "../templates/**/*.html",
    "../apps/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        base: 'var(--color-base)',
        surface: 'var(--color-surface)',
        card: 'var(--color-card)',
        border: 'var(--color-border)',
        foreground: 'var(--color-foreground)',
        'foreground-secondary': 'var(--color-foreground-secondary)',
        'foreground-muted': 'var(--color-foreground-muted)',
        muted: 'var(--color-muted)',
        'accent-cyan': 'var(--color-accent-cyan)',
        'accent-amber': 'var(--color-accent-amber)',
        'accent-indigo': 'var(--color-accent-indigo)',
        primary: 'var(--color-primary)',
        'primary-foreground': 'var(--color-primary-foreground)',
        secondary: 'var(--color-secondary)',
        'secondary-foreground': 'var(--color-secondary-foreground)',
        accent: 'var(--color-accent)',
        'accent-foreground': 'var(--color-accent-foreground)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        destructive: 'var(--color-destructive)',
        'destructive-foreground': 'var(--color-destructive-foreground)',
        ring: 'var(--color-ring)',
      },
    },
  },
  plugins: [],
}
