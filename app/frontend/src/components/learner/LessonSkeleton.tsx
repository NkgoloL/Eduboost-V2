"use client";

import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

export function LessonSkeleton() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 text-center">
      <LoadingSpinner text="Loading lesson shell..." />
    </div>
  );
}
