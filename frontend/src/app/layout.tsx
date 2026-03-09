import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  description: 'JanSathi AI - Government scheme assistant for rural India',
  manifest: '/manifest.json',
  themeColor: '#2563eb',
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
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
