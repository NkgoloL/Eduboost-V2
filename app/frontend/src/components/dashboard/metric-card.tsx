"use client";

import { useEffect, useRef, useState } from "react";
import { type LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

type TrendDirection = "up" | "down" | "neutral";
type MetricVariant = "default" | "electric" | "aqua" | "teal";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    direction: TrendDirection;
    label?: string;
  };
  variant?: MetricVariant;
  className?: string;
  /** Numeric value for the animated counter (uses `value` as fallback display) */
  numericValue?: number;
}

// ── Variant tokens ──────────────────────────────────────────────────────────
const VARIANT: Record<MetricVariant, {
  icon: string;
  border: string;
  glow: string;
  sparkColor: string;
  sparkFill: string;
  accentLine: string;
}> = {
  default: {
    icon:         "bg-gradient-to-br from-navy-700 to-navy-800 text-seafoam border border-navy-600/50",
    border:       "border-navy-700/60 hover:border-navy-500/70",
    glow:         "hover:shadow-card",
    sparkColor:   "rgba(168,218,220,0.55)",
    sparkFill:    "rgba(168,218,220,0.06)",
    accentLine:   "via-seafoam/25",
  },
  electric: {
    icon:         "bg-gradient-to-br from-electric-900/90 to-electric-800/60 text-electric-300 border border-electric-700/40",
    border:       "border-navy-700/60 hover:border-electric-500/45",
    glow:         "hover:shadow-[0_8px_32px_rgba(13,127,192,0.20),0_2px_8px_rgba(0,0,0,0.55)]",
    sparkColor:   "rgba(13,127,192,0.85)",
    sparkFill:    "rgba(13,127,192,0.08)",
    accentLine:   "via-electric-400/30",
  },
  aqua: {
    icon:         "bg-gradient-to-br from-aqua-900/70 to-aqua-800/40 text-aqua-300 border border-aqua-700/40",
    border:       "border-navy-700/60 hover:border-aqua-400/45",
    glow:         "hover:shadow-[0_8px_32px_rgba(0,207,209,0.20),0_2px_8px_rgba(0,0,0,0.55)]",
    sparkColor:   "rgba(0,207,209,0.85)",
    sparkFill:    "rgba(0,207,209,0.08)",
    accentLine:   "via-aqua-400/30",
  },
  teal: {
    icon:         "bg-gradient-to-br from-teal-900/70 to-teal-800/40 text-teal-300 border border-teal-700/40",
    border:       "border-navy-700/60 hover:border-teal-400/40",
    glow:         "hover:shadow-[0_8px_32px_rgba(45,139,139,0.18),0_2px_8px_rgba(0,0,0,0.55)]",
    sparkColor:   "rgba(45,139,139,0.85)",
    sparkFill:    "rgba(45,139,139,0.08)",
    accentLine:   "via-teal-400/25",
  },
} as const;

const TREND_STYLES: Record<TrendDirection, { text: string; bg: string; Icon: typeof TrendingUp }> = {
  up:      { text: "text-success",       bg: "bg-success/8 border border-success/20",  Icon: TrendingUp },
  down:    { text: "text-error",         bg: "bg-error/8 border border-error/20",       Icon: TrendingDown },
  neutral: { text: "text-cream-muted/65", bg: "bg-navy-700/50 border border-navy-600",  Icon: Minus },
};

// ── Deterministic sparkline data per variant ─────────────────────────────────
const SPARK_DATA: Record<MetricVariant, number[]> = {
  default:  [28, 42, 36, 58, 45, 62, 55, 74, 66, 80],
  electric: [35, 28, 50, 42, 65, 55, 78, 68, 85, 90],
  aqua:     [48, 60, 52, 72, 65, 80, 70, 88, 78, 95],
  teal:     [22, 35, 30, 48, 40, 58, 50, 68, 60, 75],
};

/** Convert sparkline numbers to a smooth SVG cubic-bezier path */
function buildSparkPath(data: number[], w: number, h: number): { line: string; area: string; endX: number; endY: number } {
  const safeData = data.length >= 2 ? data : [...data, data[0] ?? 0];
  const max  = Math.max(...safeData);
  const min  = Math.min(...safeData) * 0.6;
  const norm = (v: number) => h - ((v - min) / (max - min)) * (h * 0.82) - h * 0.06;
  const segments = Math.max(safeData.length - 1, 1);
  const xs   = safeData.map((_, i) => (i / segments) * w);
  const ys   = safeData.map(norm);

  const firstX = xs[0] ?? 0;
  const firstY = ys[0] ?? h;

  let line = `M ${firstX.toFixed(1)} ${firstY.toFixed(1)}`;
  for (let i = 1; i < xs.length; i++) {
    const currentX = xs[i] ?? firstX;
    const prevX = xs[i - 1] ?? firstX;
    const prevY = ys[i - 1] ?? firstY;
    const currentY = ys[i] ?? firstY;
    const cpx = (prevX + currentX) / 2;
    line += ` C ${cpx.toFixed(1)} ${prevY.toFixed(1)}, ${cpx.toFixed(1)} ${currentY.toFixed(1)}, ${currentX.toFixed(1)} ${currentY.toFixed(1)}`;
  }
  const lastX = xs[xs.length - 1] ?? firstX;
  const lastY = ys[ys.length - 1] ?? firstY;
  const area = `${line} L ${lastX.toFixed(1)} ${h} L ${firstX.toFixed(1)} ${h} Z`;
  return { line, area, endX: lastX, endY: lastY };
}

// ── Animated numeric counter ──────────────────────────────────────────────────
function useCountUp(target: number, duration = 1200) {
  const [display, setDisplay] = useState(0);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    const start = performance.now();
    const step = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3); // ease-out-cubic
      setDisplay(Math.round(ease * target));
      if (t < 1) raf.current = requestAnimationFrame(step);
    };
    raf.current = requestAnimationFrame(step);
    return () => { if (raf.current) cancelAnimationFrame(raf.current); };
  }, [target, duration]);

  return display;
}

// ── Component ─────────────────────────────────────────────────────────────────
export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = "default",
  className,
  numericValue,
}: MetricCardProps) {
  const v         = VARIANT[variant];
  const trendSty  = trend ? TREND_STYLES[trend.direction] : null;
  const sparkData = SPARK_DATA[variant];
  const { line, area, endX, endY } = buildSparkPath(sparkData, 120, 32);

  // Optional animated counter
  const animated = useCountUp(numericValue ?? 0, 1100);
  const displayValue = numericValue !== undefined ? animated : value;

  return (
    <div
      className={cn(
        // Base card styles
        "group relative flex flex-col gap-4 overflow-hidden rounded-2xl border bg-navy-800/70 p-5",
        "backdrop-blur-sm transition-all duration-300 cursor-default select-none",
        v.border, v.glow,
        className
      )}
    >
      {/* Top accent line */}
      <div
        className={cn(
          "absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent to-transparent",
          v.accentLine,
          "opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        )}
      />

      {/* Inner noise texture via radial gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_80%_0%,rgba(255,255,255,0.025),transparent_60%)] pointer-events-none" />

      {/* ── Header row ─────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-3">
        <p className="text-2xs font-bold uppercase tracking-[0.12em] text-cream-muted/55 leading-none pt-0.5">
          {title}
        </p>
        <div
          className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
            "transition-all duration-300 group-hover:scale-110 group-hover:rotate-[-4deg]",
            v.icon
          )}
        >
          <Icon className="h-4.5 w-4.5" strokeWidth={1.75} />
        </div>
      </div>

      {/* ── Value ──────────────────────────────────────────────────────── */}
      <div className="space-y-1">
        <p className="font-display text-[2rem] font-bold tracking-tight text-cream leading-none tabular-nums">
          {displayValue}
        </p>
        {subtitle && (
          <p className="text-xs text-cream-muted/50 leading-relaxed">{subtitle}</p>
        )}
      </div>

      {/* ── SVG Sparkline ──────────────────────────────────────────────── */}
      <svg
        viewBox="0 0 120 32"
        className="w-full h-8 overflow-visible"
        aria-hidden="true"
        preserveAspectRatio="none"
      >
        {/* Filled area under the line */}
        <path d={area} fill={v.sparkFill} />
        {/* Smooth curve */}
        <path
          d={line}
          fill="none"
          stroke={v.sparkColor}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="transition-opacity duration-300 opacity-50 group-hover:opacity-100"
        />
        {/* End-point dot */}
        <circle
          cx={endX}
          cy={endY}
          r="2.5"
          fill={v.sparkColor}
          className="transition-opacity duration-300 opacity-0 group-hover:opacity-100"
        />
      </svg>

      {/* ── Trend pill ─────────────────────────────────────────────────── */}
      {trend && trendSty && (
        <div
          className={cn(
            "flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 w-fit text-xs font-medium",
            trendSty.bg
          )}
        >
          <trendSty.Icon className={cn("h-3 w-3", trendSty.text)} strokeWidth={2.5} />
          <span className={cn("font-bold", trendSty.text)}>{trend.value}</span>
          {trend.label && (
            <span className="text-cream-muted/45">{trend.label}</span>
          )}
        </div>
      )}

      {/* ── Shine sweep on hover ────────────────────────────────────────── */}
      <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/[0.04] to-transparent pointer-events-none" />
    </div>
  );
}
