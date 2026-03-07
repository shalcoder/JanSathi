'use client';

import React from 'react';
import { useI18n } from '@/context/i18n';
import { Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function LanguageSwitcher() {
  const { language, setLanguage } = useI18n();
  const [isOpen, setIsOpen] = React.useState(false);

  const languages = [
    { code: 'en', name: 'English', label: 'EN' },
    { code: 'hi', name: 'हिन्दी', label: 'HI' },
    { code: 'ta', name: 'தமிழ்', label: 'TA' },
    { code: 'te', name: 'తెలుగు', label: 'TE' },
    { code: 'kn', name: 'ಕನ್ನಡ', label: 'KN' },
    { code: 'ml', name: 'മലയാളം', label: 'ML' },
    { code: 'mr', name: 'मराठी', label: 'MR' },
    { code: 'gu', name: 'ગુજરાતી', label: 'GU' },
    { code: 'bn', name: 'বাংলা', label: 'BN' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ', label: 'PA' },
    { code: 'or', name: 'ଓଡ଼ିଆ', label: 'OR' },
    { code: 'as', name: 'অসমীয়া', label: 'AS' },
  ] as const;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-secondary/50 hover:bg-secondary rounded-xl transition-all border border-border/50 active:scale-95"
      >
        <Globe className="w-4 h-4 text-primary" />
        <span className="text-xs font-bold uppercase tracking-widest">
          {languages.find(l => l.code === language)?.label || 'EN'}
        </span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute top-full right-0 mt-2 w-64 bg-card border border-border/50 rounded-2xl shadow-xl z-50 overflow-hidden backdrop-blur-xl p-2 grid grid-cols-2 gap-1"
          >
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={`w-full px-3 py-2 text-left text-[11px] font-bold uppercase tracking-wider transition-colors hover:bg-primary/10 rounded-xl flex items-center justify-between ${
                  language === lang.code ? 'bg-primary/5 text-primary' : 'text-foreground/60'
                }`}
              >
                {lang.name}
                {language === lang.code && <div className="w-1.5 h-1.5 bg-primary rounded-full shrink-0 ml-2" />}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
