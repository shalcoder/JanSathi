import type { NextConfig } from "next";
import withPWAModule from "@ducanh2912/next-pwa";

const withPWA = withPWAModule({
  dest: "public",
  register: true,
  // skipWaiting: true, // Deprecated/Invalid in newer version
  disable: process.env.NODE_ENV === "development",
});

const isProduction = process.env.NODE_ENV === "production";
const isStaticExport = true; // Enforced for AWS S3 deployment

const nextConfig: NextConfig = {
  // Static export for S3 + CloudFront deployment
  output: "export",

  // Environment variables available in browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://jansathi.onrender.com",
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "pk_test_Y2xlcmsuY2xlcmsuY29tJ",
  },

  // Image optimization disabled for static export
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
