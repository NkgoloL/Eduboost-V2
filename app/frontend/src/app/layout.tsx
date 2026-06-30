import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { LearnerProvider } from "@/context/LearnerContext";
import { SkipLink } from "@/components/accessibility/A11y";
import { ErrorBoundary } from "@/components/eduboost/ErrorBoundary";
import { PWAInstallPrompt } from "@/components/eduboost/PWAInstallPrompt";
import { NetworkStatus } from "@/components/eduboost/NetworkStatus";
import { LowDataMode } from "@/components/eduboost/LowDataMode";
import { ServiceWorkerRegistration } from "@/components/eduboost/ServiceWorkerRegistration";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "EduBoost SA — Modern Learning for South African Students",
    template: "%s | EduBoost SA",
  },
  description:
    "EduBoost SA is a professional EdTech platform delivering CAPS-aligned learning for South African primary school students.",
  keywords: ["education", "South Africa", "CAPS", "learning", "EdTech", "Grade 4"],
  authors: [{ name: "EduBoost SA" }],
  creator: "EduBoost SA",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3050"),
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "EduBoost SA",
  },
  openGraph: {
    type: "website",
    locale: "en_ZA",
    siteName: "EduBoost SA",
    title: "EduBoost SA — Modern Learning for South African Students",
    description: "Professional CAPS-aligned learning platform for SA primary education.",
  },
  twitter: {
    card: "summary_large_image",
    title: "EduBoost SA",
    description: "Professional CAPS-aligned learning platform for SA primary education.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
};

export const viewport: Viewport = {
  themeColor: "#0a1628",
  width: "device-width",
  initialScale: 1,
};

const MAIN_CONTENT_ID = "main-content";

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background text-foreground`}
        data-theme="night"
        suppressHydrationWarning
      >
        <LearnerProvider>
          <SkipLink target={MAIN_CONTENT_ID} />
          <NetworkStatus />
          <div className="fixed bottom-20 right-4 z-40">
            <LowDataMode />
          </div>
          <ServiceWorkerRegistration />
          <ErrorBoundary title="This screen could not load.">
            <div className="app-shell" data-app-shell>
              <div className="app-shell__background" aria-hidden="true">
                <div className="app-shell__glow" />
                <div className="app-shell__grid" />
                <div className="app-shell__dots" />
              </div>
              <main
                id={MAIN_CONTENT_ID}
                className="relative z-10 min-h-screen focus:outline-none"
                tabIndex={-1}
                role="main"
              >
                {children}
              </main>
            </div>
          </ErrorBoundary>
          <PWAInstallPrompt />
        </LearnerProvider>
        <Toaster position="bottom-right" theme="dark" richColors closeButton duration={5000} />
      </body>
    </html>
  );
}

