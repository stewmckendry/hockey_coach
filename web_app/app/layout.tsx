import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Hockey Coach AI Assistant',
  description: 'AI-powered coaching assistant for hockey season planning, practice design, and player development',
  keywords: ['hockey', 'coaching', 'AI', 'season planning', 'practice planning'],
  authors: [{ name: 'Hockey Coach AI Team' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full flex flex-col`}>
        <Header />
        <main className="flex-1 flex flex-col">
          {children}
        </main>
        <Footer />
        {/* TODO: Add authentication provider wrapper */}
        {/* TODO: Add global error boundary */}
        {/* TODO: Add analytics and monitoring */}
      </body>
    </html>
  )
}
