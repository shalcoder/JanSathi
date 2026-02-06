'use client';

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Metadata cannot be exported from a Client Component in Next.js.
// It should be moved to a separate file or removed if not strictly required for the demo.

import { ClerkProvider } from "@clerk/nextjs";

import ErrorBoundary from "@/components/ui/ErrorBoundary";

const PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const content = (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );

  // Only wrap with Clerk if a key is provided and looks valid
  if (!PUBLISHABLE_KEY || PUBLISHABLE_KEY.includes('test_example')) {
    return content;
  }

  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      {content}
    </ClerkProvider>
  );
}
