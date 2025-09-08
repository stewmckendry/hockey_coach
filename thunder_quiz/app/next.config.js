/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow Notion embedding
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors 'self' https://www.notion.so https://notion.so"
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