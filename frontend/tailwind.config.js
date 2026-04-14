/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "hud-bg": "#0D0D0F",
        "hud-surface": "#151518",
        "hud-surface-hover": "#1C1C21",
        "hud-border": "#2A2A35",
        "hud-accent": "#00FFE5",
        "hud-accent-dim": "#00B8A3",
        "hud-accent-glow": "rgba(0, 255, 229, 0.15)",
        "hud-secondary": "#FF3366",
        "hud-warning": "#FFB800",
        "hud-text": "#E8E8EC",
        "hud-text-dim": "#7A7A85",
      },
      fontFamily: {
        game: ["Chakra Petch", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "scan-line": "scan-line 4s linear infinite",
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.6 },
        },
        "scan-line": {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
      },
    },
  },
  plugins: [],
};
