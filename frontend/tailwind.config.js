/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],

  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        card: "var(--card)",

        primary: {
          DEFAULT: "var(--primary)",
          hover: "var(--primary-hover)",
        },

        secondary: "var(--secondary)",

        border: "var(--border)",
        muted: "var(--muted)",
      },
      boxShadow: {
        card: "0 1px 2px 0 rgba(15, 23, 42, 0.04), 0 1px 3px 0 rgba(15, 23, 42, 0.06)",
        elevated: "0 10px 30px -12px rgba(15, 23, 42, 0.25)",
      },
    },
  },

  plugins: [],
}