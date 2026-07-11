"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";
import { useLearner } from "../../context/LearnerContext";
import { Sidebar, BadgePopup } from "../../components/eduboost/ShellComponents";
import { RouteGuard } from "../../components/eduboost/RouteGuard";
import { AuthService } from "../../lib/api/services";

export default function LearnerLayout({ children }: { children: React.ReactNode }) {
  const { learner, setLearner, badge, setBadge } = useLearner();
  const router = useRouter();
  const pathname = usePathname();

  const isParentRoute = pathname.startsWith("/parent");

  useEffect(() => {
    if (!learner && !isParentRoute) {
      router.push("/");
    }
  }, [isParentRoute, learner, router]);

  if (isParentRoute) {
    return <>{children}</>;
  }

  if (!learner) return <RouteGuard required="learner">{children}</RouteGuard>;

  // Derive active tab from pathname
  const activeTab = pathname.split("/").pop() || "dashboard";

  return (
    <div className="app">
      <div className="flag-bar" />
      {badge && <BadgePopup badge={badge} onDismiss={() => setBadge(null)} />}
      <div className="main-layout">
        <Sidebar
          learner={learner}
          activeTab={activeTab}
          onTab={(tabId: string) => router.push(`/${tabId}`)}
          onLogout={() => {
            void AuthService.logout();
            setLearner(null);
            router.push("/");
          }}
        />
        <main id="main-content" className="main-content" tabIndex={-1}>
          {children}
        </main>
      </div>
    </div>
  );
}
