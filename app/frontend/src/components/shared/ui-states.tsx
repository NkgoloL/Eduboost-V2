import { type LucideIcon, Search, AlertCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

// ── PageHeader ────────────────────────────────────────────────────────────

interface PageHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, description, action, className }: PageHeaderProps) {
  return (
    <div className={cn("flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8", className)}>
      <div className="accent-line pl-4">
        <h1 className="text-2xl font-bold text-cream tracking-tight">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-cream-muted/70">{description}</p>
        )}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}

// ── EmptyState ────────────────────────────────────────────────────────────

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
  className?: string;
}

export function EmptyState({
  icon: Icon = Search,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed border-navy-600 bg-navy-900/40 py-16 px-6 text-center",
        className
      )}
    >
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-navy-700/50 border border-navy-600">
        <Icon className="h-6 w-6 text-cream-muted/60" />
      </div>
      <h3 className="mb-2 text-base font-semibold text-cream">{title}</h3>
      {description && (
        <p className="mb-6 max-w-sm text-sm text-cream-muted/60 leading-relaxed">
          {description}
        </p>
      )}
      {action && (
        <Button
          onClick={action.onClick}
          className="bg-gradient-to-r from-electric-500 to-aqua-500 text-white hover:opacity-90"
        >
          {action.label}
        </Button>
      )}
    </div>
  );
}

// ── ErrorState ────────────────────────────────────────────────────────────

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Something went wrong",
  description = "An error occurred while loading this content. Please try again.",
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-error/20 bg-error/5 py-16 px-6 text-center",
        className
      )}
    >
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-error/10 border border-error/20">
        <AlertCircle className="h-6 w-6 text-error" />
      </div>
      <h3 className="mb-2 text-base font-semibold text-cream">{title}</h3>
      <p className="mb-6 max-w-sm text-sm text-cream-muted/60 leading-relaxed">
        {description}
      </p>
      {onRetry && (
        <Button
          variant="outline"
          onClick={onRetry}
          className="border-error/30 text-error hover:bg-error/10"
        >
          Try Again
        </Button>
      )}
    </div>
  );
}

// ── LoadingState ──────────────────────────────────────────────────────────

interface LoadingStateProps {
  text?: string;
  className?: string;
}

export function LoadingState({ text = "Loading...", className }: LoadingStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 gap-4", className)}>
      <Loader2 className="h-8 w-8 animate-spin text-aqua-400" />
      <p className="text-sm text-cream-muted/60">{text}</p>
    </div>
  );
}

// ── Skeleton Card ─────────────────────────────────────────────────────────

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("card-glow p-5 space-y-4 animate-pulse", className)}>
      <div className="flex items-center gap-2">
        <div className="h-5 w-16 rounded-full bg-navy-700" />
        <div className="h-5 w-12 rounded-full bg-navy-700 ml-auto" />
      </div>
      <div className="space-y-2">
        <div className="h-4 w-3/4 rounded bg-navy-700" />
        <div className="h-4 w-1/2 rounded bg-navy-700" />
      </div>
      <div className="h-2 w-full rounded-full bg-navy-700" />
    </div>
  );
}
