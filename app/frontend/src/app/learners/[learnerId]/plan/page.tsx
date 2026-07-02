import { SeededStudyPlanPage } from "@/components/e2e/SeededE2ERoutePages";

export const dynamic = "force-dynamic";

export default async function StudyPlanPage({ params }: { params: Promise<{ learnerId: string }> }) {
  const { learnerId } = await params;
  return <SeededStudyPlanPage learnerId={learnerId} />;
}
