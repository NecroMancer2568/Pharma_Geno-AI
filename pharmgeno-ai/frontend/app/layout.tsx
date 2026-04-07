import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'PharmGeno AI - Personalized Drug Compatibility',
  description: 'AI-powered pharmacogenomics platform. Upload your DNA, enter your medications, get personalized drug compatibility reports in seconds.',
  keywords: 'pharmacogenomics, DNA testing, drug compatibility, personalized medicine, genetic testing',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-white">
        {children}
      </body>
    </html>
  );
}
