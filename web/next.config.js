/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_URL: process.env.API_URL || 'http://localhost:8000',
  },
  images: {
    domains: ['images.amazon.com'], // For Amazon product images
  },
  logging: {
    fetches: {
      fullUrl: true,
    },
  },
  webpack: (config, { dev }) => {
    if (dev) {
      config.devtool = 'source-map';
    }
    return config;
  },
}

module.exports = nextConfig
