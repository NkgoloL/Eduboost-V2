"use client";

import React from "react";
import clsx from "clsx";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className = "", onClick, ...props }: CardProps) {
  return (
    <div 
      className={clsx(
        "bg-[var(--surface)] border-2 border-[var(--border)] rounded-[var(--radius)] p-4 sm:p-6",
        onClick && "cursor-pointer hover:border-[var(--gold)] transition-colors",
        className
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
}
