import ETLAdminDashboard from "@/components/admin/ETLAdminDashboard";
import ContentFactoryLiveDashboard from "@/components/admin/contentFactory/ContentFactoryLiveDashboard";
import { shouldUseMockContentFactoryDashboard } from "@/lib/admin/contentFactoryMode";

export default function ContentFactoryAdminPage() {
  if (shouldUseMockContentFactoryDashboard()) {
    return <ETLAdminDashboard />;
  }
  return <ContentFactoryLiveDashboard />;
}
