import type { NextConfig } from "next";
import withPWAModule from "@ducanh2912/next-pwa";

const withPWA = withPWAModule({
  dest: "public",
  register: true,
  disable: process.env.NODE_ENV === "development",
});

const nextConfig: NextConfig = {
  // Static export for Amplify WEB platform hosting
  output: "export",

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://b0z0h6knui.execute-api.us-east-1.amazonaws.com",
  },

  images: {
    unoptimized: true,
  },
};

export default withPWA(nextConfig);
