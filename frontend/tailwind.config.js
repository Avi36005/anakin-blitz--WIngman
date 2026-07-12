/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Rich light fintech palette (Dashboard.html / Investly style)
        paper: "#FFFFFF",
        bg2: "#FAFAFA",
        surface: "#FFFFFF",
        "surface-2": "#F3F5F9",
        ink: "#14161C",
        "ink-soft": "#3B4458",
        navy: "#101114",
        fog: "#7D8699",
        line: "#EDF0F5",
        "line-strong": "#E3E8F0",
        signal: {
          red: "#F0476A", "red-ink": "#D62F54", "red-bg": "#FDEBEF",
          green: "#16B67E", "green-ink": "#0E9568", "green-bg": "#E6F7F0",
          amber: "#EF9D2B", "amber-ink": "#C47D12", "amber-bg": "#FDF2DD",
          blue: "#2563EB",
        },
      },
      fontFamily: {
        // One font across the entire site.
        display: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
        body: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
        mono: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
      },
      letterSpacing: { caps: "0.1em" },
      borderRadius: {
        none: "0px",
        sm: "8px",
        DEFAULT: "11px",
        md: "11px",
        lg: "14px",
        xl: "18px",
        "2xl": "20px",
        full: "9999px",
      },
      boxShadow: {
        card: "0 1px 2px rgba(28,35,54,.04), 0 10px 26px -16px rgba(28,35,54,.20)",
        "card-hover": "0 3px 8px rgba(28,35,54,.07), 0 22px 44px -22px rgba(28,35,54,.32)",
        navy: "0 14px 32px -12px rgba(20,26,44,.5)",
      },
      keyframes: {
        marquee: { "0%": { transform: "translateX(0)" }, "100%": { transform: "translateX(-50%)" } },
        "fade-up": { "0%": { opacity: "0", transform: "translateY(16px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        blink: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.25" } },
      },
      animation: {
        marquee: "marquee 42s linear infinite",
        "fade-up": "fade-up 0.6s ease forwards",
        blink: "blink 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
