"use client";

import { Bell, Search, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { getInitials } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { User } from "@/types";
import Link from "next/link";

interface DashboardTopbarProps {
  user?: Pick<User, "full_name" | "email" | "avatar_url" | "role" | "grade">;
  unreadNotifications?: number;
  /** Current page title shown in the topbar */
  pageTitle?: string;
  /** Breadcrumb trail, e.g. ["Dashboard", "My Courses", "Mathematics"] */
  breadcrumbs?: string[];
}

/** Compact notification preview item */
interface NotifPreview {
  id: string;
  message: string;
  time: string;
  unread: boolean;
}

const MOCK_NOTIFICATIONS: NotifPreview[] = [
  { id: "1", message: "New quiz available in Mathematics",   time: "5 min ago",  unread: true  },
  { id: "2", message: "Your essay has been graded",          time: "2 hrs ago",  unread: true  },
  { id: "3", message: "Class schedule updated for Thursday", time: "Yesterday",  unread: false },
];

export function DashboardTopbar({
  user,
  unreadNotifications = 0,
  pageTitle,
  breadcrumbs,
}: DashboardTopbarProps) {
  const hasNotifs = unreadNotifications > 0;

  return (
    <header
      className={cn(
        "fixed left-sidebar right-0 top-0 z-40",
        "flex h-topbar items-center gap-4 px-6",
        "border-b border-navy-700/60 bg-navy-900/85 backdrop-blur-md",
        "transition-all duration-200"
      )}
    >
      {/* Bottom gradient accent */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-aqua-500/12 to-transparent" />

      {/* ── Breadcrumbs / Page title ────────────────────────────────── */}
      {(breadcrumbs?.length || pageTitle) && (
        <div className="hidden shrink-0 items-center gap-1.5 sm:flex">
          {breadcrumbs?.length ? (
            breadcrumbs.map((crumb, i) => {
              const isLast = i === breadcrumbs.length - 1;
              return (
                <span key={crumb} className="flex items-center gap-1.5">
                  {i > 0 && (
                    <ChevronRight className="h-3 w-3 text-cream-muted/25" />
                  )}
                  <span
                    className={cn(
                      "font-display text-sm tracking-tight",
                      isLast
                        ? "font-bold text-cream"
                        : "font-medium text-cream-muted/45 hover:text-cream-muted/70 cursor-pointer transition-colors"
                    )}
                  >
                    {crumb}
                  </span>
                </span>
              );
            })
          ) : (
            <h1 className="font-display text-sm font-bold tracking-tight text-cream">
              {pageTitle}
            </h1>
          )}
        </div>
      )}

      {/* ── Search ─────────────────────────────────────────────────── */}
      <div className="flex-1 max-w-sm">
        <div className="group relative">
          <Search
            className={cn(
              "absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5",
              "text-cream-muted/30 transition-colors duration-200",
              "group-focus-within:text-aqua-400"
            )}
          />
          <Input
            placeholder="Search courses, lessons…"
            className={cn(
              "h-9 pl-9 pr-16 text-sm",
              "bg-navy-800/60 border-navy-600/50 text-cream placeholder:text-cream-muted/30",
              "transition-all duration-200",
              "focus-visible:ring-0 focus-visible:border-aqua-500/40 focus-visible:bg-navy-800",
              "focus-visible:shadow-[0_0_0_3px_rgba(0,207,209,0.06)]"
            )}
          />
          {/* Keyboard shortcut hint */}
          <div className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-0.5 opacity-50 transition-opacity duration-200 group-focus-within:opacity-0">
            <kbd className="flex h-5 items-center rounded border border-navy-600 bg-navy-700/70 px-1.5 font-mono text-2xs text-cream-muted/50">
              ⌘K
            </kbd>
          </div>
        </div>
      </div>

      {/* ── Grade badge ─────────────────────────────────────────────── */}
      {user?.grade && (
        <span className="hidden md:inline-flex badge-electric shrink-0 text-2xs">
          Grade {user.grade}
        </span>
      )}

      {/* ── Right cluster ────────────────────────────────────────────── */}
      <div className="ml-auto flex items-center gap-1">

        {/* Notification bell with dropdown preview */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "relative h-9 w-9 rounded-xl",
                "text-seafoam/65 hover:bg-navy-700/60 hover:text-cream",
                "transition-all duration-200"
              )}
              aria-label={`Notifications${hasNotifs ? ` (${unreadNotifications} unread)` : ""}`}
            >
              <Bell className="h-[18px] w-[18px]" strokeWidth={1.75} />
              {hasNotifs && (
                <>
                  <span className="absolute right-1.5 top-1.5 z-10 flex h-4 min-w-4 items-center justify-center rounded-full border-2 border-navy-900 bg-aqua-500 px-1 font-bold text-3xs text-navy-900">
                    {unreadNotifications > 9 ? "9+" : unreadNotifications}
                  </span>
                  <span className="absolute right-1.5 top-1.5 h-4 w-4 animate-notification-ping rounded-full bg-aqua-400" />
                </>
              )}
            </Button>
          </DropdownMenuTrigger>

          <DropdownMenuContent
            align="end"
            className="w-80 bg-navy-800 border-navy-600/70 text-cream shadow-card-hover p-0 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-navy-700">
              <span className="text-sm font-semibold text-cream">Notifications</span>
              {hasNotifs && (
                <span className="text-2xs font-bold text-aqua-400 badge-aqua px-1.5 py-0.5">
                  {unreadNotifications} new
                </span>
              )}
            </div>

            {/* Preview items */}
            <div className="divide-y divide-navy-700/60">
              {MOCK_NOTIFICATIONS.map((notif) => (
                <DropdownMenuItem
                  key={notif.id}
                  asChild
                  className="cursor-pointer px-4 py-3 hover:bg-navy-700/50 focus:bg-navy-700/50 rounded-none"
                >
                  <Link href="/dashboard/notifications" className="flex items-start gap-3">
                    {/* Unread dot */}
                    <span className={cn("mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full", notif.unread ? "bg-aqua-400" : "bg-transparent")} />
                    <div className="min-w-0 flex-1">
                      <p className={cn("text-xs leading-relaxed", notif.unread ? "text-cream" : "text-cream-muted/60")}>
                        {notif.message}
                      </p>
                      <p className="mt-0.5 text-2xs text-cream-muted/40">{notif.time}</p>
                    </div>
                  </Link>
                </DropdownMenuItem>
              ))}
            </div>

            {/* Footer */}
            <div className="border-t border-navy-700 px-4 py-2.5">
              <Link
                href="/dashboard/notifications"
                className="text-xs font-semibold text-aqua-400 hover:text-aqua-300 transition-colors"
              >
                View all notifications →
              </Link>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Divider */}
        <div className="mx-1 h-5 w-px bg-navy-700/80" />

        {/* User dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className={cn(
                "flex h-9 items-center gap-2 rounded-xl px-2.5",
                "text-seafoam/75 hover:bg-navy-700/60 hover:text-cream",
                "transition-all duration-200 group"
              )}
            >
              <Avatar className="h-7 w-7 ring-1 ring-electric-500/25 transition-all duration-200 group-hover:ring-electric-500/50">
                <AvatarImage src={user?.avatar_url} alt={user?.full_name} />
                <AvatarFallback className="bg-gradient-to-br from-electric-900 to-navy-700 text-aqua-300 text-xs font-bold">
                  {user ? getInitials(user.full_name) : "?"}
                </AvatarFallback>
              </Avatar>
              <span className="hidden max-w-[110px] truncate text-sm font-medium sm:block">
                {user?.full_name ?? "User"}
              </span>
              {/* Online indicator */}
              <span className="hidden h-1.5 w-1.5 shrink-0 rounded-full bg-success shadow-[0_0_6px_rgba(34,197,94,0.6)] sm:block" />
            </Button>
          </DropdownMenuTrigger>

          <DropdownMenuContent
            align="end"
            className="w-60 bg-navy-800 border-navy-600/70 text-cream shadow-card-hover"
          >
            {/* User info header */}
            <div className="flex items-center gap-3 border-b border-navy-700 px-3 py-3">
              <Avatar className="h-9 w-9 shrink-0 ring-1 ring-electric-500/25">
                <AvatarImage src={user?.avatar_url} alt={user?.full_name} />
                <AvatarFallback className="bg-gradient-to-br from-electric-900 to-navy-700 text-aqua-300 text-sm font-bold">
                  {user ? getInitials(user.full_name) : "?"}
                </AvatarFallback>
              </Avatar>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-cream">{user?.full_name ?? "User"}</p>
                <p className="truncate text-xs text-cream-muted/50 mt-0.5">{user?.email}</p>
              </div>
            </div>

            <div className="py-1">
              <DropdownMenuItem asChild className="h-9 cursor-pointer text-sm hover:bg-navy-700/60 focus:bg-navy-700/60">
                <Link href="/dashboard/profile">Profile</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild className="h-9 cursor-pointer text-sm hover:bg-navy-700/60 focus:bg-navy-700/60">
                <Link href="/dashboard/settings">Settings</Link>
              </DropdownMenuItem>
            </div>
            <DropdownMenuSeparator className="bg-navy-700/80" />
            <div className="py-1">
              <DropdownMenuItem className="h-9 cursor-pointer text-sm text-error hover:bg-error/10 hover:text-error focus:bg-error/10 focus:text-error">
                Sign Out
              </DropdownMenuItem>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
