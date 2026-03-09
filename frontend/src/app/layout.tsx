'use client';

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ErrorBoundary from "@/components/ui/ErrorBoundary";
import OfflineNotice from "@/components/OfflineNotice";
import { I18nProvider } from "@/context/i18n";
import { ThemeProvider } from "@/context/theme";
import { configureAmplify } from "@/lib/cognito";

// Configure Amplify/Cognito once at app boot
configureAmplify();

export const metadata = {
  themeColor: '#2563eb',
  description: 'JanSathi AI - Government scheme assistant for rural India',
  manifest: '/manifest.json',
  icons: {
    apple: [{ url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' }],
  },
};

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
      <head />
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
      </body>
    </html>
  );
}
