/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0B0E14",
          900: "#12151D",
          800: "#171B26",
          700: "#20242F",
          600: "#262B38",
        },
        mist: {
          400: "#5A6072",
          300: "#8A90A3",
          200: "#B7BBC9",
          100: "#EDEFF4",
        },
        signal: {
          violet: "#8B7FFF",
          coral: "#FF7A59",
          teal: "#45C4B0",
          amber: "#F5C56B",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      backgroundImage: {
        "spectrum-gradient":
          "linear-gradient(135deg, #8B7FFF 0%, #FF7A59 100%)",
      },
      boxShadow: {
        glow: "0 0 60px -12px rgba(139, 127, 255, 0.35)",
      },
    },
  },
  plugins: [],
};
