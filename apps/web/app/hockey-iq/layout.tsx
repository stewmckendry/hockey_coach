import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Hockey IQ Coach - Learn Hockey the Fun Way',
  description: 'Interactive Hockey IQ chatbot for U10 players. Ask questions, take quizzes, and learn hockey through Socratic questioning.',
  openGraph: {
    title: 'Hockey IQ Coach',
    description: 'Interactive hockey learning for young players',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Hockey IQ Coach',
    description: 'Interactive hockey learning for young players',
  },
  other: {
    'X-Frame-Options': 'ALLOWALL', // Allow embedding in iframes
  }
}

export default function HockeyIQLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      {children}
    </>
  )
}