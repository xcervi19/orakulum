import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Orakulum - Kariérní plánování',
  description: 'Vytvořte si osobní kariérní plán na míru',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="cs">
      <body className="antialiased">{children}</body>
    </html>
  );
}
