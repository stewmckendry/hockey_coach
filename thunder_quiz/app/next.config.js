/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow Notion embedding
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          // DO NOT set X-Frame-Options to allow Notion embedding
          // Instead, use CSP frame-ancestors
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors https://www.notion.so https://*.notion.site;"
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
        ],
      },
    ]
  },
  
  // Image optimization for Thunder logo
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'tedreevehockey.com',
        pathname: '/wp-content/uploads/**',
      },
    ],
  },
}

module.exports = nextConfig