import Link from "next/link";
import { Zap, MessageCircle, Briefcase, Code, Mail, ArrowRight, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const FOOTER_LINKS = {
  Product: [
    { label: "Features",     href: "/#features" },
    { label: "How It Works", href: "/#how-it-works" },
    { label: "Pricing",      href: "/pricing" },
    { label: "Changelog",    href: "/changelog" },
  ],
  Company: [
    { label: "About",    href: "/about" },
    { label: "Blog",     href: "/blog" },
    { label: "Careers",  href: "/careers" },
    { label: "Contact",  href: "/contact" },
  ],
  Support: [
    { label: "Help Centre", href: "/help" },
    { label: "FAQ",         href: "/faq" },
    { label: "Privacy",     href: "/privacy" },
    { label: "Terms",       href: "/terms" },
  ],
} as const;

const SOCIAL_LINKS = [
  { Icon: MessageCircle, href: "#",                           label: "Twitter / X" },
  { Icon: Briefcase,     href: "#",                           label: "LinkedIn" },
  { Icon: Code,          href: "#",                           label: "GitHub" },
  { Icon: Mail,          href: "mailto:hello@eduboost.co.za", label: "Email" },
];

export function MarketingFooter() {
  return (
    <footer className="relative overflow-hidden border-t border-navy-700/50 bg-navy-950">
      {/* Background: faint radial glow */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_50%_0%,rgba(0,207,209,0.07),transparent)]" />
      {/* Subtle grid */}
      <div className="pointer-events-none absolute inset-0 grid-pattern-sm opacity-30" />

      <div className="relative container pt-16 pb-8">

        {/* ── Newsletter band ─────────────────────────────────────────── */}
        <div
          className={cn(
            "mb-16 overflow-hidden rounded-2xl border border-navy-600/60",
            "bg-gradient-to-br from-navy-800/90 via-navy-800/70 to-navy-900/80",
            "p-7 md:p-9",
            "flex flex-col gap-6 md:flex-row md:items-center md:justify-between",
            "shadow-inner-border"
          )}
        >
          {/* Left glow accent */}
          <div className="pointer-events-none absolute -left-16 top-1/2 h-48 w-48 -translate-y-1/2 rounded-full bg-electric-500/10 blur-3xl" />

          <div className="relative z-10">
            <p className="text-2xs font-bold uppercase tracking-[0.14em] text-aqua-400/70 mb-1.5">
              Stay updated
            </p>
            <h3 className="font-display text-xl font-bold text-cream mb-2">
              Stay in the loop
            </h3>
            <p className="text-sm text-cream-muted/60 max-w-sm leading-relaxed">
              Get the latest EduBoost news, CAPS updates, and learning resources delivered to your inbox.
            </p>
          </div>

          <form
            className="relative z-10 flex gap-2 w-full md:w-auto md:min-w-[320px]"
            onSubmit={(e) => e.preventDefault()}
          >
            <Input
              type="email"
              placeholder="your@email.co.za"
              className={cn(
                "h-10 flex-1 text-sm",
                "bg-navy-700/80 border-navy-600 text-cream placeholder:text-cream-muted/35",
                "focus-visible:ring-0 focus-visible:border-aqua-500/50 focus-visible:bg-navy-700",
                "transition-all duration-200"
              )}
            />
            <Button
              type="submit"
              className="h-10 shrink-0 bg-gradient-to-r from-electric-500 to-aqua-500 px-4 font-semibold text-white shadow-glow-sm hover:shadow-glow hover:opacity-90 transition-all duration-200"
            >
              <ArrowRight className="h-4 w-4" />
              <span className="sr-only">Subscribe</span>
            </Button>
          </form>
        </div>

        {/* ── Main grid ───────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 gap-10 md:grid-cols-5 mb-14">

          {/* Brand column */}
          <div className="col-span-2 flex flex-col gap-5">
            <Link href="/" className="group flex w-fit items-center gap-2.5">
              <div
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-xl",
                  "bg-gradient-to-br from-electric-500 to-aqua-500",
                  "shadow-glow-sm transition-all duration-300",
                  "group-hover:shadow-glow group-hover:scale-110 group-hover:rotate-[-5deg]"
                )}
              >
                <Zap className="h-4 w-4 text-white" strokeWidth={2.5} />
              </div>
              <span className="font-display text-lg font-bold tracking-tight text-cream">
                Edu<span className="text-gradient">Boost</span>
                <span className="ml-0.5 font-normal text-cream-muted">SA</span>
              </span>
            </Link>

            <p className="text-sm leading-relaxed text-cream-muted/60 max-w-xs">
              CAPS-aligned learning for South African primary school students. Built with educators. Loved by learners.
            </p>

            {/* Location */}
            <p className="flex items-center gap-1.5 text-xs text-cream-muted/40">
              <MapPin className="h-3 w-3 shrink-0" />
              Proudly South African 🇿🇦
            </p>

            {/* Compliance badges */}
            <div className="flex flex-wrap gap-2">
              <span className="badge-aqua text-2xs py-0.5">POPIA Compliant</span>
              <span className="badge-electric text-2xs py-0.5">CAPS Aligned</span>
              <span className="badge-teal text-2xs py-0.5">Grade 4–7</span>
            </div>

            {/* Social row */}
            <div className="flex items-center gap-1.5">
              {SOCIAL_LINKS.map(({ Icon, href, label }) => (
                <Link
                  key={label}
                  href={href}
                  aria-label={label}
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-lg",
                    "border border-navy-600/70 text-cream-muted/50",
                    "transition-all duration-200",
                    "hover:border-aqua-500/35 hover:bg-aqua-500/8 hover:text-aqua-300",
                    "hover:shadow-[0_0_12px_rgba(0,207,209,0.15)]"
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                </Link>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {(Object.entries(FOOTER_LINKS) as [string, readonly { label: string; href: string }[]][]).map(([section, links]) => (
            <div key={section}>
              <h3 className="mb-4 text-2xs font-bold uppercase tracking-[0.14em] text-aqua-400/70">
                {section}
              </h3>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="group inline-flex items-center gap-1 text-sm text-cream-muted/55 transition-all duration-200 hover:text-cream"
                    >
                      <span className="transition-transform duration-200 group-hover:translate-x-0.5">
                        {link.label}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* ── Divider ─────────────────────────────────────────────────── */}
        <div className="divider-gradient mb-6" />

        {/* ── Bottom bar ──────────────────────────────────────────────── */}
        <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
          <p className="text-xs text-cream-muted/35">
            © {new Date().getFullYear()} EduBoost SA. All rights reserved.
          </p>
          <p className="text-xs text-cream-muted/35">
            Built with ❤️ for learners across South Africa
          </p>
        </div>
      </div>
    </footer>
  );
}
