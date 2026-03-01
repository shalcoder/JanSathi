import type { NextConfig } from "next";
import withPWAModule from "@ducanh2912/next-pwa";

const withPWA = withPWAModule({
  dest: "public",
  register: true,
  // skipWaiting: true, // Deprecated/Invalid in newer version
  disable: process.env.NODE_ENV === "development",
});

const isProduction = process.env.NODE_ENV === "production";
const isStaticExport = process.env.STATIC_EXPORT === "true";

const nextConfig: NextConfig = {
  // Static export for S3 + CloudFront deployment (Only if explicitly requested)
  ...(isStaticExport && { output: "export" }),

  // Environment variables available in browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://jansathi.onrender.com",
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "pk_test_Y2xlcmsuY2xlcmsuY29tJ",
  },

  // Rewrites only work in dev mode (not with static export)
  ...(!isProduction && {
    async rewrites() {
      return [
        {
          source: "/query",
          destination: "https://jansathi.onrender.com/query",
        },
        {
          source: "/health",
          destination: "https://jansathi.onrender.com/health",
        },
        {
          source: "/schemes",
          destination: "https://jansathi.onrender.com/schemes",
        },
        {
          source: "/analyze",
          destination: "https://jansathi.onrender.com/analyze",
        },
      ];
    },
  }),

  // Image optimization disabled for static export
  images: {
    unoptimized: true,
  },
};

// Avoid PWA plugin in development to prevent Turbopack conflicts
if (process.env.NODE_ENV === "development") {
  module.exports = nextConfig;
} else {
  module.exports = withPWA(nextConfig);
}

