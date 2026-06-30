"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ParentDashboard } from "../../../components/eduboost/ParentDashboard";
import { RouteGuard } from "../../../components/eduboost/RouteGuard";

export default function ParentDashboardPage() {
  const router = useRouter();

  return (
    <RouteGuard required="parent">
      <ParentDashboard onBack={() => router.push("/")} />
    </RouteGuard>
  );
}
