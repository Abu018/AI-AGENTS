/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        greatVibes: ['"Great Vibes"', "cursive"],
        gupter: ["Gupter", "serif"],
        lato: ["Lato", "sans-serif"],
        styleScript: ['"Style Script"', "cursive"],
      },
      keyframes: {
        slideFromTop: {
          "0%": { transform: "translateY(-50px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideFromBottom: {
          "0%": { transform: "translateY(50px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      animation: {
        "slide-from-top": "slideFromTop 1s ease-out",
        "slide-from-bottom": "slideFromBottom 1s ease-out",
      },
      screens: {
        xs: "344px", // Custom breakpoint
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px",
      },
    },
  },
  plugins: [],
};
