import type { NextConfig } from "next";
import withPWAModule from "@ducanh2912/next-pwa";

const withPWA = withPWAModule({
  dest: "public",
  register: true,
  disable: process.env.NODE_ENV === "development",
});

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://b0z0h6knui.execute-api.us-east-1.amazonaws.com";

const nextConfig: NextConfig = {
  // SSR mode — Amplify handles build & hosting (no static export needed)

  env: {
    NEXT_PUBLIC_API_URL: API_URL,
  },

  // Proxy all /v1/* and /health* requests to Lambda — avoids CORS in production
  async rewrites() {
    return [
      {
        source: "/v1/:path*",
        destination: `${API_URL}/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${API_URL}/health`,
      },
    ];
  },

  images: {
    unoptimized: true,
  },
};

export default withPWA(nextConfig);
