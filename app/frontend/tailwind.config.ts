import type { Config } from "tailwindcss";
import {
  brandPalette,
  elevationTokens,
  fontStacks,
  radiusScale,
  semanticColorVariables,
  spacingScale,
  statusPalette,
} from "./src/design/tokens";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      // ── Deep Tech Ocean: Tech Innovation × Ocean Depths ──────────────
      colors: {
        ...brandPalette,
        ...semanticColorVariables,
        success: statusPalette.success,
        warning: statusPalette.warning,
        error: statusPalette.error,
        info: statusPalette.info,
      },

      // ── Typography ────────────────────────────────────────────────────
      fontFamily: fontStacks,
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
        "3xs": ["0.5rem",   { lineHeight: "0.75rem"  }],
      },

      // ── Spacing ───────────────────────────────────────────────────────
      spacing: spacingScale,

      // ── Border radius ─────────────────────────────────────────────────
      borderRadius: radiusScale,

      // ── Box shadows ───────────────────────────────────────────────────
      boxShadow: elevationTokens,

      // ── Backdrop blur ─────────────────────────────────────────────────
      backdropBlur: {
        xs: "2px",
      },

      // ── Keyframes ─────────────────────────────────────────────────────
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to:   { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to:   { height: "0" },
        },
        "fade-in":     { from: { opacity: "0", transform: "translateY(16px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        "fade-in-up":  { from: { opacity: "0", transform: "translateY(20px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        "fade-in-down":{ from: { opacity: "0", transform: "translateY(-12px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        "slide-in-left":{ from: { opacity: "0", transform: "translateX(-20px)" }, to: { opacity: "1", transform: "translateX(0)" } },
        "blur-in":     { from: { opacity: "0", filter: "blur(8px)", transform: "scale(0.97)" }, to: { opacity: "1", filter: "blur(0)", transform: "scale(1)" } },
        "scale-in":    { from: { opacity: "0", transform: "scale(0.90)" }, to: { opacity: "1", transform: "scale(1)" } },
        "float":       {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%":      { transform: "translateY(-12px)" },
        },
        "shimmer": {
          from: { transform: "translateX(-100%)" },
          to:   { transform: "translateX(100%)" },
        },
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 10px rgba(0,207,209,0.3)" },
          "50%":       { boxShadow: "0 0 28px rgba(0,207,209,0.7)" },
        },
        "pulse-ring": {
          "0%":   { transform: "scale(0.95)", boxShadow: "0 0 0 0 rgba(0,207,209,0.45)" },
          "70%":  { transform: "scale(1)",    boxShadow: "0 0 0 10px rgba(0,207,209,0)" },
          "100%": { transform: "scale(0.95)", boxShadow: "0 0 0 0 rgba(0,207,209,0)" },
        },
        "spin-slow": {
          to: { transform: "rotate(360deg)" },
        },
        "morph": {
          "0%, 100%": { borderRadius: "60% 40% 30% 70% / 60% 30% 70% 40%" },
          "25%":  { borderRadius: "30% 60% 70% 40% / 50% 60% 30% 60%" },
          "50%":  { borderRadius: "50% 60% 30% 60% / 40% 30% 70% 60%" },
          "75%":  { borderRadius: "40% 70% 60% 30% / 60% 40% 50% 70%" },
        },
        "notification-ping": {
          "0%":   { transform: "scale(1)", opacity: "1" },
          "75%, 100%": { transform: "scale(2.2)", opacity: "0" },
        },
        "gradient-x": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%":      { backgroundPosition: "100% 50%" },
        },
      },

      // ── Animation shorthands ──────────────────────────────────────────
      animation: {
        "accordion-down":    "accordion-down 0.2s ease-out",
        "accordion-up":      "accordion-up 0.2s ease-out",
        "fade-in":           "fade-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both",
        "fade-in-up":        "fade-in-up 0.5s cubic-bezier(0.22, 1, 0.36, 1) both",
        "fade-in-slow":      "fade-in 0.7s cubic-bezier(0.22, 1, 0.36, 1) both",
        "slide-in-left":     "slide-in-left 0.4s cubic-bezier(0.22, 1, 0.36, 1) both",
        "blur-in":           "blur-in 0.5s ease-out both",
        "scale-in":          "scale-in 0.35s cubic-bezier(0.22, 1, 0.36, 1) both",
        "float":             "float 6s ease-in-out infinite",
        "float-slow":        "float 9s ease-in-out infinite",
        "shimmer":           "shimmer 1.8s ease-in-out infinite",
        "pulse-glow":        "pulse-glow 2.5s ease-in-out infinite",
        "pulse-ring":        "pulse-ring 2s ease-in-out infinite",
        "spin-slow":         "spin-slow 10s linear infinite",
        "morph":             "morph 12s ease-in-out infinite",
        "notification-ping": "notification-ping 1.5s ease-out infinite",
        "gradient-x":        "gradient-x 4s ease infinite",
      },

      // ── Transition timing functions ───────────────────────────────────
      transitionTimingFunction: {
        "spring":     "cubic-bezier(0.22, 1, 0.36, 1)",
        "bounce-in":  "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
        "smooth-out": "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
