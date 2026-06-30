export type ThemeMode = "light" | "dark";

export type ColorScale = Record<string, string>;

export const brandPalette = {
  navy: {
    950: "#050d1a",
    900: "#0a1628",
    800: "#1a2332",
    700: "#1e2d40",
    600: "#243550",
    500: "#2a3e60",
    400: "#3a5070",
  },
  teal: {
    DEFAULT: "#2d8b8b",
    50: "#e6f7f7",
    100: "#b3e5e5",
    200: "#80d4d4",
    300: "#4dc2c2",
    400: "#26b0b0",
    500: "#2d8b8b",
    600: "#226a6a",
    700: "#1a5050",
    800: "#113535",
    900: "#091b1b",
  },
  electric: {
    DEFAULT: "#0d7fc0",
    50: "#e0f2fb",
    100: "#b3dff5",
    200: "#80c9ee",
    300: "#4db3e7",
    400: "#26a2e0",
    500: "#0d7fc0",
    600: "#0a6396",
    700: "#07486d",
    800: "#042d43",
    900: "#021220",
  },
  aqua: {
    DEFAULT: "#00cfd1",
    50: "#e0fafa",
    100: "#b3f2f2",
    200: "#80e9ea",
    300: "#4de0e1",
    400: "#26d8d9",
    500: "#00cfd1",
    600: "#00a1a3",
    700: "#007476",
    800: "#004748",
    900: "#001a1b",
  },
  seafoam: {
    DEFAULT: "#a8dadc",
    light: "#d4eef0",
    dark: "#6db8bb",
  },
  cream: {
    DEFAULT: "#f1faee",
    muted: "#c8ddd5",
    dark: "#9ab8b0",
  },
} as const;

export const statusPalette = {
  success: {
    DEFAULT: "#22c55e",
    foreground: "#052e16",
    muted: "#dcfce7",
    dark: "#16a34a",
  },
  warning: {
    DEFAULT: "#f59e0b",
    foreground: "#451a03",
    muted: "#fef3c7",
  },
  error: {
    DEFAULT: "#ef4444",
    foreground: "#450a0a",
    muted: "#fee2e2",
    dark: "#dc2626",
  },
  info: {
    DEFAULT: "#0d7fc0",
    foreground: "#f1faee",
    muted: "#e0f2fb",
  },
} as const;

export const semanticColorVariables = {
  border: "hsl(var(--border))",
  input: "hsl(var(--input))",
  ring: "hsl(var(--ring))",
  background: "hsl(var(--background))",
  foreground: "hsl(var(--foreground))",
  primary: {
    DEFAULT: "hsl(var(--primary))",
    foreground: "hsl(var(--primary-foreground))",
  },
  secondary: {
    DEFAULT: "hsl(var(--secondary))",
    foreground: "hsl(var(--secondary-foreground))",
  },
  destructive: {
    DEFAULT: "hsl(var(--destructive))",
    foreground: "hsl(var(--destructive-foreground))",
  },
  muted: {
    DEFAULT: "hsl(var(--muted))",
    foreground: "hsl(var(--muted-foreground))",
  },
  accent: {
    DEFAULT: "hsl(var(--accent))",
    foreground: "hsl(var(--accent-foreground))",
  },
  popover: {
    DEFAULT: "hsl(var(--popover))",
    foreground: "hsl(var(--popover-foreground))",
  },
  card: {
    DEFAULT: "hsl(var(--card))",
    foreground: "hsl(var(--card-foreground))",
  },
} as const;

export const fontStacks: Record<string, string[]> = {
  sans: ["DM Sans", "var(--font-geist-sans)", "system-ui", "sans-serif"],
  mono: ["JetBrains Mono", "var(--font-geist-mono)", "monospace"],
  display: ["Bricolage Grotesque", "var(--font-geist-sans)", "system-ui", "sans-serif"],
};

export const spacingScale = {
  "4.5": "1.125rem",
  13: "3.25rem",
  18: "4.5rem",
  22: "5.5rem",
  26: "6.5rem",
  sidebar: "16rem",
  topbar: "3.5rem",
} as const;

export const radiusScale = {
  "4xl": "2rem",
  "3xl": "1.5rem",
  "2xl": "1rem",
  xl: "calc(var(--radius) + 4px)",
  lg: "var(--radius)",
  md: "calc(var(--radius) - 2px)",
  sm: "calc(var(--radius) - 4px)",
} as const;

export const elevationTokens = {
  card: "0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.4)",
  "card-hover": "0 8px 32px rgba(0,207,209,0.18), 0 4px 12px rgba(0,0,0,0.5)",
  "card-lift": "0 16px 48px rgba(0,207,209,0.22), 0 6px 20px rgba(0,0,0,0.6)",
  glow: "0 0 24px rgba(0,207,209,0.4), 0 0 8px rgba(13,127,192,0.2)",
  "glow-sm": "0 0 12px rgba(13,127,192,0.5)",
  "glow-lg": "0 0 48px rgba(0,207,209,0.3), 0 0 20px rgba(13,127,192,0.25)",
  electric: "0 0 20px rgba(13,127,192,0.45)",
  "inner-glow": "inset 0 1px 0 rgba(0,207,209,0.12), inset 0 -1px 0 rgba(0,0,0,0.1)",
  "inner-border": "inset 0 0 0 1px rgba(0,207,209,0.15)",
} as const;

export const motionTokens = {
  durations: {
    instant: "75ms",
    fast: "150ms",
    base: "200ms",
    slow: "350ms",
  },
  easings: {
    spring: "cubic-bezier(0.22, 1, 0.36, 1)",
    bounceIn: "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
    smoothOut: "cubic-bezier(0.4, 0, 0.2, 1)",
  },
} as const;

export type ValidationTone = "info" | "success" | "warning" | "error";

export const validationToneTokens: Record<ValidationTone, { text: string; background: string; border: string; icon: string }> = {
  info: {
    text: statusPalette.info.foreground,
    background: statusPalette.info.muted,
    border: "rgba(13,127,192,0.35)",
    icon: statusPalette.info.DEFAULT,
  },
  success: {
    text: statusPalette.success.foreground,
    background: statusPalette.success.muted,
    border: "rgba(34,197,94,0.45)",
    icon: statusPalette.success.DEFAULT,
  },
  warning: {
    text: statusPalette.warning.foreground,
    background: statusPalette.warning.muted,
    border: "rgba(245,158,11,0.45)",
    icon: statusPalette.warning.DEFAULT,
  },
  error: {
    text: statusPalette.error.foreground,
    background: statusPalette.error.muted,
    border: "rgba(239,68,68,0.45)",
    icon: statusPalette.error.DEFAULT,
  },
};

export type ThemeVariables = Record<string, string>;

export const themeModes: Record<ThemeMode, ThemeVariables> = {
  light: {
    background: "210 33% 98%",
    foreground: "220 15% 12%",
    card: "0 0% 100%",
    "card-foreground": "220 15% 14%",
    popover: "0 0% 100%",
    "popover-foreground": "220 20% 14%",
    primary: "185 72% 38%",
    "primary-foreground": "0 0% 100%",
    secondary: "210 40% 96%",
    "secondary-foreground": "220 25% 20%",
    muted: "210 40% 96%",
    "muted-foreground": "220 15% 35%",
    accent: "185 80% 45%",
    "accent-foreground": "0 0% 100%",
    destructive: "0 85% 55%",
    "destructive-foreground": "0 0% 100%",
    border: "210 30% 90%",
    input: "210 30% 90%",
    ring: "185 80% 45%",
    radius: "0.625rem",
  },
  dark: {
    background: "222 47% 6%",
    foreground: "180 5% 95%",
    card: "220 32% 10%",
    "card-foreground": "180 5% 95%",
    popover: "220 32% 10%",
    "popover-foreground": "180 5% 95%",
    primary: "185 100% 40%",
    "primary-foreground": "222 47% 6%",
    secondary: "215 30% 18%",
    "secondary-foreground": "180 5% 85%",
    muted: "215 30% 14%",
    "muted-foreground": "200 15% 55%",
    accent: "185 100% 40%",
    "accent-foreground": "222 47% 6%",
    destructive: "0 84% 60%",
    "destructive-foreground": "0 0% 98%",
    border: "216 24% 18%",
    input: "216 24% 18%",
    ring: "185 100% 40%",
    radius: "0.625rem",
  },
};

export const designTokens = {
  colors: {
    brand: brandPalette,
    status: statusPalette,
    semantic: semanticColorVariables,
  },
  typography: {
    fonts: fontStacks,
  },
  layout: {
    spacing: spacingScale,
    radii: radiusScale,
    elevation: elevationTokens,
  },
  motion: motionTokens,
};
