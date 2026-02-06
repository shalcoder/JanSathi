'use client';

import React, { useEffect, useRef } from 'react';

interface AudioPlayerProps {
    src: string;
    autoPlay?: boolean;
}

export default function AudioPlayer({ src, autoPlay = true }: AudioPlayerProps) {
    const audioRef = useRef<HTMLAudioElement>(null);

    useEffect(() => {
        if (audioRef.current && autoPlay) {
            audioRef.current.play().catch(e => {
                console.warn("Auto-play blocked:", e);
            });
        }
    }, [src, autoPlay]);

    return (
        <div className="mt-2 text-sm text-slate-500">
            <audio ref={audioRef} controls src={src} className="h-8 w-full max-w-[200px]" />
        </div>
    );
}
