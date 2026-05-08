import { LoadingSpinner } from "../components/ui/LoadingSpinner";

export default function Loading() {
  return (
    <main id="main-content" className="min-h-screen flex flex-col items-center justify-center" role="status" aria-live="polite">
      <LoadingSpinner />
      <p className="mt-4 text-[var(--muted)] font-medium">Loading EduBoost...</p>
    </main>
  );
}
