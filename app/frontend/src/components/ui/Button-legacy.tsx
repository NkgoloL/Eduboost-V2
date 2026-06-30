"use client";

import React from "react";
import clsx from "clsx";

type ButtonVariant = "primary" | "secondary";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  className?: string;
}

export function Button({
  children,
  variant = "primary",
  fullWidth = false,
  className = "",
  disabled = false,
  onClick,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={clsx(
        variant === "primary" ? "btn-primary" : "btn-secondary",
        fullWidth && "w-full",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
      style={fullWidth ? { width: "100%" } : {}}
      {...props}
    >
      {children}
    </button>
  );
}
