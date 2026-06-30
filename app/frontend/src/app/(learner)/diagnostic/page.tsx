import { DiagnosticEntryClient } from "@/components/learner/DiagnosticEntryClient";
import { getDiagnosticEntryShellData } from "@/lib/learner/server-loaders";

export const dynamic = "force-dynamic";

export default async function DiagnosticPage() {
  const shellData = await getDiagnosticEntryShellData();
  return <DiagnosticEntryClient {...shellData} />;
}
