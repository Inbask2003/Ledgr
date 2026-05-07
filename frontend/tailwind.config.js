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

        primary: {
          DEFAULT: "var(--primary)",
          hover: "var(--primary-hover)",
        },

        secondary: "var(--secondary)",

        border: "var(--border)",
        muted: "var(--muted)",
      },
    },
  },

  plugins: [],
}