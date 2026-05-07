// app/layout.tsx

import type { Metadata } from 'next'
import { Plus_Jakarta_Sans, Goldman, Rubik, Space_Grotesk } from 'next/font/google'
import './globals.css'
import { ToastProvider } from '@/components/Toast'

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-jakarta',
})

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-space-grotesk',
})

const rubik = Rubik({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-jetbrains',
})

const goldman = Goldman({
  subsets: ['latin'],
  weight: ['700'],
  variable: '--font-goldman',
})

export const metadata: Metadata = {
  title: 'Episteme',
  description: 'The Socratic Study Engine — AI that refuses to answer your questions.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${plusJakarta.variable} ${spaceGrotesk.variable} ${rubik.variable} ${goldman.variable}`}>
        {/* Top gradient accent line */}
        <div className="top-accent-line" />
        <ToastProvider>
          <div style={{ minHeight: '100vh' }}>{children}</div>
        </ToastProvider>
      </body>
    </html>
  )
}
