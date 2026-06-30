import Link from "next/link";
import { Clock, BookOpen, ChevronRight } from "lucide-react";
import { cn, formatPercent } from "@/lib/utils";
import type { Course } from "@/types";

type SubjectColors = { badge: string; glow: string };

const SUBJECT_COLORS: Record<string, SubjectColors> = {
  mathematics:    { badge: "badge-electric", glow: "from-electric-500/20" },
  english:        { badge: "badge-aqua",     glow: "from-aqua-500/20" },
  science:        { badge: "badge-teal",     glow: "from-teal-500/20" },
  social_studies: { badge: "badge-aqua",     glow: "from-teal-600/20" },
  afrikaans:      { badge: "badge-teal",     glow: "from-seafoam/20" },
  arts:           { badge: "badge-electric", glow: "from-electric-400/20" },
};

interface CourseCardProps {
  course: Course;
  progress?: number; // 0–100
  lastAccessed?: string;
  className?: string;
}

export function CourseCard({
  course,
  progress = 0,
  lastAccessed,
  className,
}: CourseCardProps) {
  const subjectKey = course.subject ?? "mathematics";
  const colors = (SUBJECT_COLORS[subjectKey] ?? SUBJECT_COLORS.mathematics) as SubjectColors;
  const isStarted  = progress > 0;
  const isComplete = progress >= 100;

  return (
    <Link
      href={`/dashboard/courses/${course.id}`}
      className={cn(
        "card-glow group block overflow-hidden transition-all duration-200",
        className
      )}
    >
      {/* Top colour band */}
      <div
        className={cn(
          "h-1.5 w-full bg-gradient-to-r",
          colors.glow,
          "from-30% to-transparent"
        )}
        style={{
          background: `linear-gradient(to right, var(--tw-gradient-from), transparent)`,
        }}
      />

      <div className="p-5">
        {/* Subject badge + CAPS */}
        <div className="flex items-center gap-2 mb-3">
          <span className={colors.badge}>
            {course.subject.replace("_", " ")}
          </span>
          {course.is_caps_aligned && (
            <span className="badge-teal">CAPS</span>
          )}
          <span className="ml-auto text-xs text-cream-muted/60">
            Gr {course.grade}
          </span>
        </div>

        {/* Title & description */}
        <h3 className="mb-1.5 text-base font-semibold text-cream leading-snug group-hover:text-aqua-300 transition-colors">
          {course.title}
        </h3>
        <p className="text-xs text-cream-muted/70 line-clamp-2 leading-relaxed">
          {course.description}
        </p>

        {/* Meta row */}
        <div className="mt-4 flex items-center gap-4 text-xs text-cream-muted/60">
          <span className="flex items-center gap-1">
            <BookOpen className="h-3.5 w-3.5" />
            {course.total_lessons} lessons
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            {course.estimated_hours}h
          </span>
          {lastAccessed && (
            <span className="ml-auto">{lastAccessed}</span>
          )}
        </div>

        {/* Progress */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-1.5 text-xs">
            <span className="text-cream-muted/70">
              {isComplete
                ? "Completed ✓"
                : isStarted
                ? "In progress"
                : "Not started"}
            </span>
            <span
              className={cn(
                "font-medium",
                isComplete ? "text-success" : isStarted ? "text-aqua-400" : "text-cream-muted/40"
              )}
            >
              {formatPercent(progress)}
            </span>
          </div>
          <div className="progress-bar">
            <div
              className={cn(
                "progress-fill",
                isComplete && "bg-success"
              )}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Continue button */}
      <div className="flex items-center justify-end gap-1 px-5 py-3 border-t border-navy-700 text-xs font-medium text-electric-400 group-hover:text-aqua-300 transition-colors">
        {isComplete ? "Review" : isStarted ? "Continue" : "Start learning"}
        <ChevronRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
      </div>
    </Link>
  );
}
