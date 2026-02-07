'use client';

import { useState, useEffect } from 'react';

export type AppSettings = {
    language: string;
    voiceEnabled: boolean;
    notifications: boolean;
    autoTranslate: boolean;
};

const STORAGE_KEY = 'jansathi_settings';

const DEFAULT_SETTINGS: AppSettings = {
    language: 'hi',
    voiceEnabled: true,
    notifications: true,
    autoTranslate: true,
};

export function useSettings() {
    const [settings, setSettings] = useState<AppSettings>(DEFAULT_SETTINGS);

    useEffect(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                setSettings(JSON.parse(stored));
            } catch (e) {
                console.error("Failed to parse settings", e);
            }
        }
    }, []);

    const updateSettings = (updates: Partial<AppSettings>) => {
        const newSettings = { ...settings, ...updates };
        setSettings(newSettings);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newSettings));

        // Dispatch event for other components to sync
        window.dispatchEvent(new Event('jansathi-settings-update'));
    };

    return { settings, updateSettings };
}
