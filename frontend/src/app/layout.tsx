'use client';

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Authenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import { configureAmplify } from "@/lib/cognito";
import ErrorBoundary from "@/components/ui/ErrorBoundary";
import OfflineNotice from "@/components/OfflineNotice";
import { I18nProvider } from "@/context/i18n";
import { ThemeProvider } from "@/context/theme";

// Initialize Cognito
configureAmplify();

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
  const content = (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="description" content="JanSathi AI - Government scheme assistant for rural India" />
      </head>
      <body
        suppressHydrationWarning
        className={`${geistSans.variable} ${geistMono.variable} antialiased scrollbar-none`}
      >
        <OfflineNotice />
        <ErrorBoundary>
          <ThemeProvider>
            <I18nProvider>
              {children}
            </I18nProvider>
          </ThemeProvider>
        </ErrorBoundary>

        {/* Unregister Service Worker to clear poisoned cache and stale Server Action IDs */}

      </body>
    </html>
  );

  return (
    <Authenticator.Provider>
      {content}
    </Authenticator.Provider>
  );
}
