"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { Menu, X, Zap, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
  { label: "Features",     href: "/#features" },
  { label: "How It Works", href: "/#how-it-works" },
  { label: "Pricing",      href: "/pricing" },
  { label: "About",        href: "/about" },
] as const;

export function MarketingHeader() {
  const [open, setOpen]         = useState(false);
  const [scrollY, setScrollY]   = useState(0);

  // Track exact scroll position for ramp effect
  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Close menu on ESC
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const scrolled      = scrollY > 24;
  const blurAmount    = Math.min(scrollY / 80, 1);   // 0 → 1 over first 80px
  const bgOpacity     = Math.min(scrollY / 60, 0.92); // transparent → 92% opaque

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-all duration-300",
        scrolled && "shadow-[0_8px_32px_rgba(0,0,0,0.45)]"
      )}
      style={{
        backgroundColor: `rgba(10,22,40,${bgOpacity})`,
        backdropFilter: `blur(${blurAmount * 16}px) saturate(${1 + blurAmount * 0.4})`,
        WebkitBackdropFilter: `blur(${blurAmount * 16}px)`,
        borderBottom: scrolled ? "1px solid rgba(255,255,255,0.05)" : "none",
      }}
    >
      {/* Top accent line that fades in on scroll */}
      <div
        className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-aqua-500/35 to-transparent transition-opacity duration-500"
        style={{ opacity: scrolled ? 1 : 0 }}
      />

      <div className="container flex h-16 items-center justify-between gap-4">
        {/* ── Logo ─────────────────────────────────────────────────── */}
        <Link href="/" className="group flex shrink-0 items-center gap-2.5">
          <div
            className={cn(
              "relative flex h-8 w-8 items-center justify-center rounded-xl",
              "bg-gradient-to-br from-electric-500 to-aqua-500",
              "shadow-glow-sm transition-all duration-300",
              "group-hover:shadow-glow group-hover:scale-110 group-hover:rotate-[-6deg]"
            )}
          >
            <Zap className="h-4 w-4 text-white" strokeWidth={2.5} />
          </div>
          <span className="font-display text-lg font-bold tracking-tight text-cream">
            Edu<span className="text-gradient">Boost</span>
            <span className="ml-0.5 font-normal text-cream-muted">SA</span>
          </span>
        </Link>

        {/* ── Desktop nav ───────────────────────────────────────────── */}
        <nav className="hidden items-center gap-0.5 md:flex">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="group relative rounded-lg px-4 py-2 text-sm font-medium text-seafoam/80 transition-colors duration-200 hover:text-cream"
            >
              {link.label}
              {/* Animated underline */}
              <span className="absolute bottom-1.5 left-4 right-4 h-px origin-left scale-x-0 rounded-full bg-gradient-to-r from-electric-400 to-aqua-400 transition-transform duration-300 group-hover:scale-x-100" />
            </Link>
          ))}
        </nav>

        {/* ── Desktop CTA ───────────────────────────────────────────── */}
        <div className="hidden shrink-0 items-center gap-2 md:flex">
          <Button
            variant="ghost"
            asChild
            className="h-9 text-sm text-seafoam/75 hover:bg-white/5 hover:text-cream"
          >
            <Link href="/login">Sign In</Link>
          </Button>

          {/* Primary CTA with shimmer sweep */}
          <Button
            asChild
            className={cn(
              "group relative h-9 overflow-hidden px-5 text-sm font-semibold text-white",
              "bg-gradient-to-r from-electric-500 to-aqua-500",
              "shadow-glow-sm hover:shadow-glow",
              "transition-all duration-300 hover:opacity-95"
            )}
          >
            <Link href="/signup">
              {/* Shimmer overlay */}
              <span className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/15 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
              <span className="relative z-10 flex items-center gap-1.5">
                Get Started
                <ArrowRight className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
              </span>
            </Link>
          </Button>
        </div>

        {/* ── Mobile menu toggle ────────────────────────────────────── */}
        <button
          className={cn(
            "relative flex h-9 w-9 items-center justify-center rounded-lg md:hidden",
            "text-seafoam hover:bg-white/6 hover:text-cream transition-all duration-200"
          )}
          onClick={() => setOpen(!open)}
          aria-label="Toggle navigation"
          aria-expanded={open}
          aria-controls="mobile-nav"
        >
          {/* Icon crossfade */}
          <span className={cn("absolute transition-all duration-200", open ? "opacity-100 rotate-0" : "opacity-0 rotate-90")}>
            <X className="h-5 w-5" />
          </span>
          <span className={cn("absolute transition-all duration-200", open ? "opacity-0 -rotate-90" : "opacity-100 rotate-0")}>
            <Menu className="h-5 w-5" />
          </span>
        </button>
      </div>

      {/* ── Mobile navigation panel ───────────────────────────────────── */}
      <div
        id="mobile-nav"
        role="navigation"
        className={cn(
          "overflow-hidden transition-all duration-300 ease-spring md:hidden",
          open ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
        )}
        style={{
          backgroundColor: `rgba(10,22,40,0.96)`,
          backdropFilter: `blur(24px)`,
          WebkitBackdropFilter: `blur(24px)`,
          borderTop: "1px solid rgba(255,255,255,0.04)",
        }}
      >
        <div className="px-4 pb-5 pt-2 space-y-0.5">
          {NAV_LINKS.map((link, i) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className={cn(
                "flex items-center rounded-xl px-4 py-3 text-sm font-medium",
                "text-seafoam/80 hover:bg-white/5 hover:text-cream",
                "transition-all duration-200",
                // Stagger via inline delay
              )}
              style={{ transitionDelay: open ? `${i * 40}ms` : "0ms" }}
            >
              {link.label}
            </Link>
          ))}

          <div className="mt-2 flex flex-col gap-2 border-t border-white/5 pt-3">
            <Button
              variant="ghost"
              asChild
              className="h-10 w-full justify-start text-seafoam/80 hover:bg-white/5 hover:text-cream"
            >
              <Link href="/login" onClick={() => setOpen(false)}>Sign In</Link>
            </Button>
            <Button
              asChild
              className="h-10 w-full bg-gradient-to-r from-electric-500 to-aqua-500 font-semibold text-white shadow-glow-sm hover:opacity-90"
            >
              <Link href="/signup" onClick={() => setOpen(false)}>
                Get Started Free
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
