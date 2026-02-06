'use client';

import { Suspense } from 'react';
import ChatInterface from "@/components/ChatInterface";

export default function ChatPage() {
    return (
        <main className="h-screen w-full flex flex-col bg-slate-50 dark:bg-slate-950">
            <div className="flex-1 w-full relative">
                <Suspense fallback={<div>Loading...</div>}>
                    <ChatInterface />
                </Suspense>
            </div>
        </main>
    );
}
