/* components/ThemeToggle.tsx */
'use client';
import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';

type Theme = 'light' | 'dark';

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light';
  try {
    const stored = window.localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') return stored;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  } catch {
    return 'light';
  }
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTheme(getInitialTheme());
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    try {
      window.localStorage.setItem('theme', theme);
    } catch {}
  }, [theme, mounted]);

  const toggle = useCallback(() => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      className="group inline-flex items-center gap-2 rounded-full border border-neutral-200 bg-white px-2 py-1 text-sm text-neutral-800 shadow-sm transition-colors hover:bg-neutral-50 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100 dark:hover:bg-neutral-700"
    >
      <div className="relative h-6 w-10 rounded-full bg-neutral-200 transition-colors dark:bg-neutral-700">
        <motion.div
          layout
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          className="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-sm dark:bg-neutral-200"
          style={{ left: isDark ? 'calc(100% - 1.25rem - 2px)' : '2px' }}
        />
      </div>
      <motion.span
        key={isDark ? 'dark' : 'light'}
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
        className="min-w-[3ch] text-xs font-medium text-neutral-700 dark:text-neutral-200"
      >
        {isDark ? 'Dark' : 'Light'}
      </motion.span>
    </button>
  );
}


