import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import './globals.css';
import ThemeToggle from "@/components/ThemeToggle";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Электронная доска",
  description: "Электронная информационная доска",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Инициализация темы до гидратации, чтобы избежать вспышки */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
  (function () {
    try {
      var stored = localStorage.getItem('theme');
      var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var isDark = stored ? stored === 'dark' : prefersDark;
      var root = document.documentElement;
      if (isDark) root.classList.add('dark'); else root.classList.remove('dark');
    } catch (_) {}
  })();`,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white text-gray-900 dark:bg-neutral-800 dark:text-gray-100 transition-colors duration-300`}
      >
        <div className="fixed right-4 top-4 z-30">
          <ThemeToggle />
        </div>
        {children}
      </body>
    </html>
  );
}
