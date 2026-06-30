"use client";

import { useEffect, useId, useMemo, useRef } from "react";
import { AlertTriangle, CheckCircle2, Info, ShieldAlert } from "lucide-react";

import { cn } from "@/lib/utils";
import { ValidationTone } from "@/design/tokens";

type AriaRole = "alert" | "status";

type ValidationMessageProps = {
  tone?: ValidationTone;
  title: string;
  description?: React.ReactNode;
  className?: string;
  id?: string;
  autoFocus?: boolean;
};

type SummaryItem = {
  id?: string;
  href?: string;
  label: string;
  description?: string;
};

type ValidationSummaryProps = {
  tone?: ValidationTone;
  heading?: string;
  description?: string;
  items: SummaryItem[];
  className?: string;
  autoFocus?: boolean;
};

const toneIconMap: Record<ValidationTone, React.ComponentType<{ className?: string }>> = {
  error: ShieldAlert,
  warning: AlertTriangle,
  success: CheckCircle2,
  info: Info,
};

const toneRoleMap: Record<ValidationTone, { role: AriaRole; ariaLive: "assertive" | "polite" }> = {
  error: { role: "alert", ariaLive: "assertive" },
  warning: { role: "alert", ariaLive: "assertive" },
  success: { role: "status", ariaLive: "polite" },
  info: { role: "status", ariaLive: "polite" },
};

export function ValidationMessage({
  tone = "error",
  title,
  description,
  className,
  id,
  autoFocus,
}: ValidationMessageProps) {
  const fallbackId = useId();
  const elementId = id ?? fallbackId;
  const ref = useRef<HTMLDivElement>(null);
  const Icon = toneIconMap[tone];
  const { role, ariaLive } = toneRoleMap[tone];

  useEffect(() => {
    if (autoFocus && ref.current) {
      ref.current.focus();
    }
  }, [autoFocus]);

  return (
    <div
      ref={ref}
      id={elementId}
      role={role}
      aria-live={ariaLive}
      className={cn("validation-message", className)}
      data-tone={tone}
      tabIndex={autoFocus ? -1 : undefined}
    >
      <span className="validation-icon" aria-hidden>
        <Icon className="h-5 w-5" />
      </span>
      <div>
        <p className="validation-title">{title}</p>
        {description && <p className="validation-description">{description}</p>}
      </div>
    </div>
  );
}

export function ValidationSummary({
  tone = "error",
  heading = "Please review the highlighted issues",
  description,
  items,
  className,
  autoFocus = true,
}: ValidationSummaryProps) {
  const summaryId = useId();
  const ref = useRef<HTMLElement>(null);
  const filtered = useMemo(() => items.filter(Boolean), [items]);

  useEffect(() => {
    if (autoFocus && filtered.length && ref.current) {
      ref.current.focus();
    }
  }, [autoFocus, filtered.length]);

  if (!filtered.length) return null;

  return (
    <section
      ref={ref}
      aria-labelledby={`${summaryId}-title`}
      className={cn("validation-summary", className)}
      data-tone={tone}
      tabIndex={autoFocus ? -1 : undefined}
    >
      <div>
        <p id={`${summaryId}-title`} className="validation-title">
          {heading}
        </p>
        {description && <p className="validation-description">{description}</p>}
      </div>
      <ul>
        {filtered.map(({ id, href, label, description: detail }) => {
          const linkTarget = href ?? (id ? `#${id}` : undefined);
          return (
            <li key={`${label}-${id ?? href ?? Math.random()}`}>
              {linkTarget ? (
                <a href={linkTarget}>{label}</a>
              ) : (
                <span>{label}</span>
              )}
              {detail && <span className="validation-item-detail">{detail}</span>}
            </li>
          );
        })}
      </ul>
    </section>
  );
}

export type { ValidationMessageProps, ValidationSummaryProps, SummaryItem };
