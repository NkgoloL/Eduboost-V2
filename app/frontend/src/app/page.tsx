"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { StarsBackground } from "../components/ui/StarsBackground";
import { Button } from "../components/ui/Button";

export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[var(--bg)] flex items-center justify-center relative overflow-hidden">
      <div className="absolute top-0 w-full h-2 bg-gradient-to-r from-green-500 via-yellow-400 to-red-500 z-50" />
      <StarsBackground />
      
      <div className="relative z-10 w-full max-w-md p-6 text-center">
        <div className="text-6xl mb-6">🦁</div>
        <h1 className="text-4xl font-['Baloo_2'] font-bold text-[var(--text)] mb-2">EduBoost SA</h1>
        <p className="text-[var(--muted)] font-medium mb-12">
          AI-powered learning for South African learners Grade R to Grade 7
        </p>
        
        <div className="flex flex-col gap-4 items-center">
          <Button 
            onClick={() => router.push("/login")} 
            fullWidth 
            className="py-4 text-lg"
          >
            🚀 Start Learning!
          </Button>
          
          <Button 
            onClick={() => router.push("/login")} 
            variant="secondary" 
            fullWidth 
            className="py-4 text-lg"
          >
            👨‍👩‍👧 Parent / Guardian Portal
          </Button>
        </div>
      </div>
    </div>
  );
}
