import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef8ff",
          100: "#d6eeff",
          200: "#b3dfff",
          300: "#7fc6ff",
          400: "#40a4ff",
          500: "#1976ff",
          600: "#0f5fed",
          700: "#144dbf",
          800: "#163f99",
          900: "#173878",
        },
        ink: "#0f172a",
        mist: "#f8fbff",
      },
      boxShadow: {
        soft: "0 24px 60px rgba(15, 23, 42, 0.08)",
      },
      backgroundImage: {
        "page-grid":
          "radial-gradient(circle at 1px 1px, rgba(148,163,184,0.22) 1px, transparent 0)",
      },
    },
  },
  plugins: [],
};

export default config;
