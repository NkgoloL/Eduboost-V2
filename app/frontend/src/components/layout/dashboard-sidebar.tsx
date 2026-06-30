"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, BookOpen, BarChart2, ClipboardList,
  Bell, Settings, LogOut, Zap, ChevronLeft, Users, ShieldCheck,
  GraduationCap,
} from "lucide-react";
import { cn, getInitials } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { UserRole, User } from "@/types";

// ── Nav definitions ──────────────────────────────────────────────────────────
const STUDENT_NAV = [
  { label: "Dashboard",     href: "/dashboard",               icon: LayoutDashboard },
  { label: "My Courses",    href: "/dashboard/courses",       icon: BookOpen },
  { label: "Progress",      href: "/dashboard/progress",      icon: BarChart2 },
  { label: "Assessments",   href: "/dashboard/assessments",   icon: ClipboardList },
  { label: "Notifications", href: "/dashboard/notifications", icon: Bell, badge: 3 },
];
const TEACHER_NAV = [
  { label: "Dashboard",     href: "/dashboard",               icon: LayoutDashboard },
  { label: "My Classes",    href: "/dashboard/classes",       icon: Users },
  { label: "Courses",       href: "/dashboard/courses",       icon: BookOpen },
  { label: "Assessments",   href: "/dashboard/assessments",   icon: ClipboardList },
  { label: "Reports",       href: "/dashboard/reports",       icon: BarChart2 },
  { label: "Notifications", href: "/dashboard/notifications", icon: Bell },
];
const ADMIN_NAV = [
  { label: "Dashboard",     href: "/dashboard",               icon: LayoutDashboard },
  { label: "Users",         href: "/dashboard/users",         icon: Users },
  { label: "Courses",       href: "/dashboard/courses",       icon: BookOpen },
  { label: "Analytics",     href: "/dashboard/analytics",     icon: BarChart2 },
  { label: "Moderation",    href: "/dashboard/moderation",    icon: ShieldCheck },
  { label: "Notifications", href: "/dashboard/notifications", icon: Bell },
];

function getNavItems(role: UserRole) {
  if (role === "admin" || role === "super_admin") return ADMIN_NAV;
  if (role === "teacher") return TEACHER_NAV;
  return STUDENT_NAV;
}

const ROLE_LABELS: Record<UserRole, string> = {
  student: "Student", teacher: "Teacher", parent: "Parent",
  admin: "Admin",     super_admin: "Super Admin",
};

const ROLE_BADGE: Record<UserRole, string> = {
  student:     "bg-electric-900/50 text-electric-300 border-electric-800/60",
  teacher:     "bg-teal-900/50 text-teal-300 border-teal-800/60",
  parent:      "bg-aqua-900/40 text-aqua-300 border-aqua-800/60",
  admin:       "bg-navy-700 text-seafoam border-navy-600",
  super_admin: "bg-red-900/30 text-red-300 border-red-800/60",
};

/** Ambient dot color in the status indicator */
const ROLE_DOT: Record<UserRole, string> = {
  student:     "bg-electric-400 shadow-[0_0_6px_rgba(13,127,192,0.7)]",
  teacher:     "bg-teal-400 shadow-[0_0_6px_rgba(45,139,139,0.7)]",
  parent:      "bg-aqua-400 shadow-[0_0_6px_rgba(0,207,209,0.7)]",
  admin:       "bg-seafoam shadow-[0_0_6px_rgba(168,218,220,0.7)]",
  super_admin: "bg-red-400 shadow-[0_0_6px_rgba(248,113,113,0.7)]",
};

interface DashboardSidebarProps {
  user?: Pick<User, "full_name" | "email" | "avatar_url" | "role">;
  role?: UserRole;
  collapsed?: boolean;
  onToggle?: () => void;
}

export function DashboardSidebar({
  user,
  role = "student",
  collapsed = false,
  onToggle,
}: DashboardSidebarProps) {
  const pathname  = usePathname();
  const navItems  = getNavItems(role);
  const roleLabel = ROLE_LABELS[role] ?? "User";
  const badgeCls  = ROLE_BADGE[role] ?? ROLE_BADGE.student;
  const dotCls    = ROLE_DOT[role] ?? ROLE_DOT.student;

  return (
    <aside
      className={cn(
        "relative flex h-full flex-col",
        "border-r border-navy-700/60 bg-navy-900",
        "transition-all duration-300 ease-spring",
        collapsed ? "w-16" : "w-sidebar"
      )}
    >
      {/* Subtle vertical gradient accent on right edge */}
      <div className="pointer-events-none absolute inset-y-0 right-0 w-px bg-gradient-to-b from-transparent via-aqua-500/12 to-transparent" />

      {/* Background noise layer */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_0%_0%,rgba(13,127,192,0.05),transparent_60%)]" />

      {/* ── Logo ─────────────────────────────────────────────────────── */}
      <div className="relative flex h-topbar shrink-0 items-center border-b border-navy-700/60 px-4">
        <Link href="/dashboard" className="group flex items-center gap-2.5 min-w-0">
          <div
            className={cn(
              "flex h-8 w-8 shrink-0 items-center justify-center rounded-xl",
              "bg-gradient-to-br from-electric-500 to-aqua-500",
              "shadow-glow-sm group-hover:shadow-glow",
              "transition-all duration-300 group-hover:scale-110 group-hover:rotate-[-6deg]"
            )}
          >
            <Zap className="h-4 w-4 text-white" strokeWidth={2.5} />
          </div>
          {!collapsed && (
            <span className="truncate font-display text-base font-bold tracking-tight text-cream">
              Edu<span className="text-gradient">Boost</span>
            </span>
          )}
        </Link>
      </div>

      {/* ── Collapse toggle ───────────────────────────────────────────── */}
      <button
        onClick={onToggle}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        className={cn(
          "absolute -right-3 top-[4.5rem] z-20",
          "flex h-6 w-6 items-center justify-center rounded-full",
          "border border-navy-600/80 bg-navy-800",
          "text-seafoam/60 shadow-card",
          "transition-all duration-200",
          "hover:border-aqua-500/40 hover:bg-navy-700 hover:text-aqua-300 hover:shadow-glow-sm"
        )}
      >
        <ChevronLeft
          className={cn("h-3.5 w-3.5 transition-transform duration-300", collapsed && "rotate-180")}
        />
      </button>

      {/* ── Primary navigation ───────────────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden px-2.5 py-4 space-y-0.5">
        {!collapsed && (
          <p className="mb-2.5 px-3 text-2xs font-bold uppercase tracking-[0.14em] text-cream-muted/30">
            Navigation
          </p>
        )}

        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const hasBadge = "badge" in item && (item as { badge?: number }).badge;

          return (
            <Link
              key={item.href}
              href={item.href}
              title={collapsed ? item.label : undefined}
              className={cn(
                // Base
                "group/item relative flex items-center gap-3 rounded-xl px-3 py-2.5",
                "text-sm font-medium transition-all duration-200",
                // Default state
                "text-cream-muted/60 hover:bg-navy-700/70 hover:text-cream",
                // Active overrides
                isActive && [
                  "bg-gradient-to-r from-navy-700/80 to-navy-700/30",
                  "text-cream shadow-inner-border",
                ],
                // Collapsed adjustments
                collapsed && "justify-center px-0 py-3"
              )}
            >
              {/* Active left accent bar */}
              {isActive && (
                <span
                  className={cn(
                    "absolute left-0 top-1/2 -translate-y-1/2",
                    "h-5 w-0.5 rounded-full bg-gradient-to-b from-electric-400 to-aqua-400",
                    "shadow-[0_0_8px_rgba(0,207,209,0.5)]"
                  )}
                />
              )}

              {/* Icon wrapper */}
              <div className="relative shrink-0">
                <item.icon
                  className={cn(
                    "h-[18px] w-[18px] transition-all duration-200",
                    isActive ? "text-aqua-300" : "text-cream-muted/50 group-hover/item:text-cream-muted/80",
                    !collapsed && "group-hover/item:scale-110"
                  )}
                  strokeWidth={isActive ? 2 : 1.75}
                />
                {/* Badge dot on icon in collapsed state */}
                {hasBadge && collapsed && (
                  <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-aqua-500 text-[0.45rem] font-bold text-navy-900">
                    {(item as { badge: number }).badge}
                  </span>
                )}
              </div>

              {/* Label + badge (expanded) */}
              {!collapsed && (
                <>
                  <span className="flex-1 truncate">{item.label}</span>
                  {hasBadge && (
                    <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full border border-aqua-500/30 bg-aqua-500/12 px-1.5 text-2xs font-bold text-aqua-400">
                      {(item as { badge: number }).badge}
                    </span>
                  )}
                </>
              )}
            </Link>
          );
        })}
      </nav>

      {/* ── User profile card ─────────────────────────────────────────── */}
      {!collapsed && user && (
        <div className="mx-2.5 mb-2.5">
          <div
            className={cn(
              "rounded-xl border border-navy-700/60 bg-navy-800/50 p-3",
              "backdrop-blur-sm transition-colors duration-200",
              "hover:border-navy-600/80 hover:bg-navy-800/70"
            )}
          >
            <div className="flex min-w-0 items-center gap-3">
              {/* Avatar with status ring */}
              <div className="relative shrink-0">
                <Avatar className="h-8 w-8 ring-1 ring-electric-500/25">
                  <AvatarImage src={user.avatar_url} alt={user.full_name} />
                  <AvatarFallback className="bg-gradient-to-br from-electric-900 to-navy-700 text-aqua-300 text-xs font-bold">
                    {getInitials(user.full_name)}
                  </AvatarFallback>
                </Avatar>
                {/* Online status indicator */}
                <span
                  className={cn(
                    "absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-navy-800",
                    dotCls
                  )}
                />
              </div>

              {/* Info */}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold leading-tight text-cream">
                  {user.full_name}
                </p>
                <span
                  className={cn(
                    "mt-0.5 inline-flex items-center gap-0.5 rounded-full border px-1.5 py-0.5 text-[0.6rem] font-semibold",
                    badgeCls
                  )}
                >
                  <GraduationCap className="h-2.5 w-2.5" />
                  {roleLabel}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Bottom actions ────────────────────────────────────────────── */}
      <div className="shrink-0 border-t border-navy-700/60 px-2.5 py-3 space-y-0.5">
        <Link
          href="/dashboard/settings"
          title={collapsed ? "Settings" : undefined}
          className={cn(
            "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium",
            "text-cream-muted/55 transition-all duration-200",
            "hover:bg-navy-700/60 hover:text-cream",
            collapsed && "justify-center px-0"
          )}
        >
          <Settings className="h-[18px] w-[18px] shrink-0" strokeWidth={1.75} />
          {!collapsed && <span>Settings</span>}
        </Link>

        <button
          className={cn(
            "flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium",
            "text-cream-muted/55 transition-all duration-200",
            "hover:bg-error/8 hover:text-error",
            collapsed && "justify-center px-0"
          )}
          title={collapsed ? "Sign Out" : undefined}
        >
          <LogOut className="h-[18px] w-[18px] shrink-0" strokeWidth={1.75} />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  );
}
