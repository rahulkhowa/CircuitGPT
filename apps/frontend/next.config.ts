import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output configuration for production Docker deployments
  output: "standalone",
  
  // React Strict Mode for robust component state testing
  reactStrictMode: true,
  
  // Disable linting/TS checking during build since CI runs it separately
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    const backendUrl = process.env.BACKEND_INTERNAL_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};


export default nextConfig;
