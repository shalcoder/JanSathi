import type { NextConfig } from "next";

const isProduction = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  // Static export for S3 + CloudFront deployment
  ...(isProduction && { output: "export" }),

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

export default nextConfig;

