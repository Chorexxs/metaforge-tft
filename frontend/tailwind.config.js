/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "hud-bg": "#181326",
        "hud-surface": "#1E1E2E",
        "hud-surface-hover": "#252538",
        "hud-border": "#2A2A45",
        "hud-accent": "#FFB60D",
        "hud-accent-dim": "#B8860B",
        "hud-accent-glow": "rgba(255, 182, 13, 0.15)",
        "hud-secondary": "#C0C0C0",
        "hud-warning": "#FFB60D",
        "hud-text": "#FFFFFF",
        "hud-text-dim": "#9090A0",
        "tft-gold": "#FFB60D",
        "tft-silver": "#C0C0C0",
        "tft-prismatic": "#BF5AF2",
        "tft-shadow": "#181326",
        "tft-cost-1": "#95A4A4",
        "tft-cost-2": "#379C37",
        "tft-cost-3": "#379CDE",
        "tft-cost-4": "#A335EE",
        "tft-cost-5": "#FFD700",
        "tft-health": "#50C878",
        "tft-health-low": "#FF4444",
        "tft-gold-coin": "#FFD700",
        "tft-xp": "#4169E1",
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
