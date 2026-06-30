import React from "react";
import clsx from "clsx";

type BadgeVariant = "default" | "success" | "warning" | "error" | "primary" | "secondary" | "gold";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export function Badge({ children, variant = "default", className = "" }: BadgeProps) {
  const variants = {
    default: "bg-gray-100 text-gray-800 border-gray-200",
    success: "bg-green-100 text-green-800 border-green-200",
    warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
    error: "bg-red-100 text-red-800 border-red-200",
    primary: "bg-blue-100 text-blue-800 border-blue-200",
    secondary: "bg-slate-100 text-slate-800 border-slate-200",
    gold: "bg-[var(--gold)] text-white border-yellow-500",
  };

  return (
    <span 
      className={clsx(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
