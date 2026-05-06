import { LearnerProvider } from "../context/LearnerContext";
import { ServiceWorkerRegistration } from "../components/ServiceWorkerRegistration";
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
        <LearnerProvider>
          <ServiceWorkerRegistration />
          {children}
        </LearnerProvider>
      </body>
    </html>
  );
}
