import { DashboardClient } from "@/components/learner/DashboardClient";
import { getLearnerDashboardShellData } from "@/lib/learner/server-loaders";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const shellData = await getLearnerDashboardShellData();
  return <DashboardClient {...shellData} />;
}
