import type { NextConfig } from "next";
const withPWA = require("@ducanh2912/next-pwa").default({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === "development",
});

const isProduction = process.env.NODE_ENV === "production";
const isStaticExport = process.env.STATIC_EXPORT === "true";

const nextConfig: NextConfig = {
  // Static export for S3 + CloudFront deployment (Only if explicitly requested)
  ...(isStaticExport && { output: "export" }),

  // Environment variables available in browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000",
  },

  // Rewrites only work in dev mode (not with static export)
  ...(!isProduction && {
    async rewrites() {
      return [
        {
          source: "/query",
          destination: "http://127.0.0.1:5000/query",
        },
        {
          source: "/health",
          destination: "http://127.0.0.1:5000/health",
        },
        {
          source: "/schemes",
          destination: "http://127.0.0.1:5000/schemes",
        },
        {
          source: "/analyze",
          destination: "http://127.0.0.1:5000/analyze",
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

