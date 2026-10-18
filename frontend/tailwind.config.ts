import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#070913",
        surface: "#0F1222",
        "surface-card": "#151930",
        "surface-border": "#252B4D",
        gold: {
          300: "#FDE047",
          400: "#FACC15",
          500: "#EAB308",
          600: "#CA8A04",
          primary: "#D97706",
        },
        cosmic: {
          light: "#A5B4FC",
          primary: "#6366F1",
          dark: "#4338CA",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        serif: ["var(--font-cinzel)", "serif"],
      },
    },
  },
  plugins: [],
};

export default config;
