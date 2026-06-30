import { LessonEntryClient } from "@/components/learner/LessonEntryClient";
import { getLessonShellData } from "@/lib/learner/server-loaders";

export const dynamic = "force-dynamic";

export default async function LessonPage() {
  const shellData = await getLessonShellData();
  return <LessonEntryClient {...shellData} />;
}
