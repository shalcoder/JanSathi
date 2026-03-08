'use client';

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ErrorBoundary from "@/components/ui/ErrorBoundary";
import OfflineNotice from "@/components/OfflineNotice";
import { I18nProvider } from "@/context/i18n";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
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
          <I18nProvider>
            {children}
          </I18nProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
