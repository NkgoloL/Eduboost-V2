// ── User & Auth ───────────────────────────────────────────────────────────

export type UserRole = "student" | "teacher" | "parent" | "admin" | "super_admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  avatar_url?: string;
  grade?: number;
  school?: string;
  created_at: string;
}

export interface AuthSession {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_at: number;
}

// ── Courses & Lessons ─────────────────────────────────────────────────────

export type SubjectArea =
  | "mathematics"
  | "english"
  | "science"
  | "social_studies"
  | "afrikaans"
  | "arts";

export interface Course {
  id: string;
  title: string;
  description: string;
  subject: SubjectArea;
  grade: number;
  total_lessons: number;
  estimated_hours: number;
  thumbnail_url?: string;
  is_caps_aligned: boolean;
  created_at: string;
}

export interface Lesson {
  id: string;
  course_id: string;
  title: string;
  description: string;
  order: number;
  duration_minutes: number;
  is_locked: boolean;
  lesson_type: "video" | "reading" | "quiz" | "activity";
}

// ── Progress ──────────────────────────────────────────────────────────────

export interface CourseProgress {
  course_id: string;
  course: Course;
  completed_lessons: number;
  total_lessons: number;
  percentage: number;
  last_accessed: string;
  time_spent_minutes: number;
}

export interface StudentDashboardMetrics {
  courses_enrolled: number;
  lessons_completed: number;
  study_streak_days: number;
  average_score: number;
  total_time_hours: number;
  badges_earned: number;
}

// ── Assessments ───────────────────────────────────────────────────────────

export interface Assessment {
  id: string;
  title: string;
  course_id: string;
  total_questions: number;
  time_limit_minutes?: number;
  due_date?: string;
  status: "not_started" | "in_progress" | "completed";
  score?: number;
}

// ── Notifications ─────────────────────────────────────────────────────────

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  is_read: boolean;
  created_at: string;
}

// ── API Response wrappers ─────────────────────────────────────────────────

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, string[]>;
}
