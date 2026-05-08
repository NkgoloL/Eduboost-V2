import { LearnerProvider } from "../context/LearnerContext";
import { ServiceWorkerRegistration } from "../components/ServiceWorkerRegistration";
import { ErrorBoundary } from "../components/eduboost/ErrorBoundary";
import { SkipLink } from "../components/accessibility/A11y";
import "./globals.css";
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "EduBoost SA",
  description: "AI-powered learning for South African learners Grade R to Grade 7",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#3b82f6",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SkipLink />
        <LearnerProvider>
          <ErrorBoundary>
            <ServiceWorkerRegistration />
            {children}
          </ErrorBoundary>
        </LearnerProvider>
      </body>
    </html>
  );
}
