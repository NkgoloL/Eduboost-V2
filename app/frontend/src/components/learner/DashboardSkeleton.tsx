"use client";

import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

interface DashboardSkeletonProps {
  note?: string;
}

export function DashboardSkeleton({ note }: DashboardSkeletonProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 text-center">
      <LoadingSpinner text={note ?? "Loading your dashboard..."} />
    </div>
  );
}
