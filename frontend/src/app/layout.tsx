'use client';

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import ErrorBoundary from "@/components/ui/ErrorBoundary";
import OfflineNotice from "@/components/OfflineNotice";
import Script from 'next/script';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

import { dark } from "@clerk/themes";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const content = (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="description" content="JanSathi AI - Government scheme assistant for rural India" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased scrollbar-none`}
      >
        <OfflineNotice />
        <ErrorBoundary>
          {children}
        </ErrorBoundary>

        {/* Unregister Service Worker to clear poisoned cache and stale Server Action IDs */}

      </body>
    </html>
  );

  // Ensure ClerkProvider is always present to prevent "SignedIn outside Provider" errors.
  // Use a fallback key for build time if the environment variable is missing.
  // This is critical for static generation where secrets might not be present.
  const finalKey = PUBLISHABLE_KEY || "pk_test_placeholder_for_build_verification";

  if (!PUBLISHABLE_KEY) {
    console.warn("Missing NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY. Using placeholder for build.");
  }

  return (
    <ClerkProvider
      publishableKey={PUBLISHABLE_KEY}
      appearance={{
        baseTheme: dark,
      }}
    >
      {content}
    </ClerkProvider>
  );
}
