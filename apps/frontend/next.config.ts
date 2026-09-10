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
  }
};

export default nextConfig;
