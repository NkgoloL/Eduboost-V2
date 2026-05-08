"use client";

import { useLearner } from "../../context/LearnerContext";
import { AVATARS, GRADES } from "./constants";
import type { ActiveLearner } from "../../lib/api/types";

interface SidebarProps {
  learner: ActiveLearner;
  activeTab: string;
  onTab: (tabId: string) => void;
  onLogout: () => void;
}

interface BadgePopupProps {
  badge: string;
  onDismiss: () => void;
}

interface PlaceholderPanelProps {
  title: string;
  description: string;
  children: React.ReactNode;
}

const navItems = [
  { id: "dashboard", icon: "🏠", label: "Home" },
  { id: "diagnostic", icon: "🧪", label: "Assessment" },
  { id: "lesson", icon: "📖", label: "Learn" },
  { id: "plan", icon: "📅", label: "Study Plan" },
  { id: "badges", icon: "🏆", label: "Badges" },
  { id: "parent", icon: "👨‍👩‍👧", label: "Parent Portal" },
];

function NavButton({ item, activeTab, onTab, compact = false }: { item: typeof navItems[number]; activeTab: string; onTab: (tabId: string) => void; compact?: boolean }) {
  const active = activeTab === item.id;
  return (
    <button
      type="button"
      onClick={() => onTab(item.id)}
      aria-current={active ? "page" : undefined}
      aria-label={item.label}
      className={compact ? "flex flex-col items-center justify-center gap-1 rounded-xl px-2 py-2 text-xs font-bold" : "w-full text-left font-bold"}
      style={compact ? { color: active ? "var(--gold)" : "var(--muted)" } : {
        padding: "12px 20px",
        cursor: "pointer",
        color: active ? "var(--gold)" : "var(--muted)",
        borderLeft: active ? "3px solid var(--gold)" : "3px solid transparent",
        background: "transparent",
        borderTop: 0,
        borderRight: 0,
        borderBottom: 0,
        fontFamily: "Nunito",
      }}
    >
      <span aria-hidden="true">{item.icon}</span>
      <span>{compact ? item.label.split(" ")[0] : item.label}</span>
    </button>
  );
}

export function Sidebar({ learner, activeTab, onTab, onLogout }: SidebarProps) {
  const { gamification } = useLearner();
  const level = gamification?.level || 1;
  const xp = gamification?.total_xp || 0;
  const xpProgress = xp % 100;

  return (
    <>
      <aside className="sidebar" aria-label="Learner navigation">
        <div style={{ padding: "0 20px 24px", borderBottom: "1px solid var(--border)", marginBottom: 8 }}>
          <strong>EduBoost SA</strong>
        </div>
        <section aria-label="Learner profile" style={{ margin: "8px 12px 16px", background: "var(--surface2)", borderRadius: "var(--radius)", padding: 14 }}>
          <div style={{ fontSize: "2rem", textAlign: "center", marginBottom: 6 }} aria-hidden="true">
            {typeof learner.avatar === "number" ? AVATARS[learner.avatar] : "🦁"}
          </div>
          <div style={{ fontWeight: 800, textAlign: "center" }}>{learner.nickname || learner.display_name || "Learner"}</div>
          <div style={{ fontSize: "0.75rem", color: "var(--muted)", textAlign: "center", marginBottom: 12 }}>{GRADES[learner.grade]?.label || `Grade ${learner.grade}`}</div>
          <div aria-label={`Level ${level}, ${xp} XP`}>
            <div style={{ background: "rgba(0,0,0,0.2)", height: 6, borderRadius: 3, overflow: "hidden", marginBottom: 4 }}>
              <div style={{ background: "var(--gold)", height: "100%", width: `${xpProgress}%`, transition: "width 0.5s ease-out" }} />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10px", fontWeight: "bold" }}>
              <span style={{ color: "var(--gold)" }}>LVL {level}</span>
              <span style={{ color: "var(--muted)" }}>{xp} XP</span>
            </div>
          </div>
        </section>
        <nav aria-label="Primary learner sections">
          {navItems.map((item) => <NavButton key={item.id} item={item} activeTab={activeTab} onTab={onTab} />)}
        </nav>
        <div style={{ marginTop: "auto", padding: 16 }}>
          <button className="btn-secondary" onClick={onLogout} style={{ width: "100%" }}>Logout</button>
        </div>
      </aside>
      <nav className="mobile-bottom-nav" aria-label="Mobile learner navigation">
        {navItems.slice(0, 4).map((item) => <NavButton key={item.id} item={item} activeTab={activeTab} onTab={onTab} compact />)}
      </nav>
    </>
  );
}

export function BadgePopup({ badge, onDismiss }: BadgePopupProps) {
  return (
    <button type="button" className="badge-popup" onClick={onDismiss} aria-live="polite" aria-label={`Badge earned: ${badge}. Dismiss notification.`}>
      <span style={{ fontSize: "2rem" }} aria-hidden="true">🏅</span>
      <div>
        <div style={{ fontSize: "0.75rem", opacity: 0.8 }}>Badge Earned!</div>
        <div>{badge}</div>
      </div>
    </button>
  );
}

export function PlaceholderPanel({ title, description, children }: PlaceholderPanelProps) {
  return (
    <section style={{ maxWidth: 860, margin: "0 auto" }} aria-labelledby="placeholder-panel-title">
      <h2 id="placeholder-panel-title" style={{ fontFamily: "'Baloo 2',cursive", fontSize: "1.6rem", marginBottom: 8 }}>{title}</h2>
      <p style={{ color: "var(--muted)", marginBottom: 24 }}>{description}</p>
      <div className="consent-form">{children}</div>
    </section>
  );
}
