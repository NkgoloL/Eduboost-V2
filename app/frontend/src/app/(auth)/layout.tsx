import React from "react";
import { StarsBackground } from "../../components/ui/StarsBackground";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--bg)] flex items-center justify-center relative overflow-hidden">
      <StarsBackground />
      <div className="relative z-10 w-full max-w-md p-6">
        {children}
      </div>
    </div>
  );
}
