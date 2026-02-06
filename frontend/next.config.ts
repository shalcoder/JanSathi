import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/query',
        destination: 'http://127.0.0.1:5000/query',
      },
      {
        source: '/health',
        destination: 'http://127.0.0.1:5000/health',
      },
    ];
  },
};

export default nextConfig;
