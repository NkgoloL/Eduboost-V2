import { SeededLessonPage } from "@/components/e2e/SeededE2ERoutePages";

export default async function Page({ params }: { params: Promise<{ learnerId: string }> }) {
  const { learnerId } = await params;
  return <SeededLessonPage learnerId={learnerId} />;
}
