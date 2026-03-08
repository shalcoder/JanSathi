'use client';

import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '@/context/theme';
import { motion } from 'framer-motion';

export default function ThemeToggle() {
  const { theme, setTheme, actualTheme } = useTheme();

  const themes = [
    { value: 'light', icon: Sun, label: 'Light' },
    { value: 'dark', icon: Moon, label: 'Dark' },
    { value: 'system', icon: Monitor, label: 'System' },
  ];

  return (
    <div className="flex items-center bg-secondary/80 backdrop-blur-sm rounded-lg p-1 border border-border/50">
      {themes.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          onClick={() => setTheme(value as any)}
          className={`relative px-3 py-2 rounded-md text-xs font-medium transition-all duration-200 flex items-center gap-1.5 ${
            theme === value
              ? 'text-primary-foreground bg-primary shadow-sm'
              : 'text-secondary-foreground hover:text-foreground hover:bg-secondary/60'
          }`}
          title={`Switch to ${label} theme`}
        >
          <Icon className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">{label}</span>
          
          {theme === value && (
            <motion.div
              layoutId="theme-indicator"
              className="absolute inset-0 bg-primary rounded-md"
              style={{ zIndex: -1 }}
              initial={false}
              transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
            />
          )}
        </button>
      ))}
    </div>
  );
}

// Simple theme toggle for mobile or compact spaces
export function SimpleThemeToggle() {
  const { actualTheme, setTheme } = useTheme();

  return (
    <button
      onClick={() => setTheme(actualTheme === 'dark' ? 'light' : 'dark')}
      className="p-2 rounded-lg bg-secondary/80 backdrop-blur-sm border border-border/50 text-secondary-foreground hover:text-foreground hover:bg-secondary transition-all duration-200"
      title={`Switch to ${actualTheme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {actualTheme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </button>
  );
}