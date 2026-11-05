/** @type {import('next').NextConfig} */
const backend = process.env.BACKEND_URL || "http://localhost:5001";

const nextConfig = {
  // The browser calls the same origin. Next.js forwards /api/v1 to Flask, so no CORS setup is needed.
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `${backend}/api/v1/:path*` }];
  },
};

export default nextConfig;
