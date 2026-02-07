'use client';

// import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { Ghost } from "lucide-react";

export default function Navbar() {
    return (
        <nav className="w-full max-w-4xl mx-auto flex justify-between items-center py-4 px-6 mb-4">
            <div className="flex items-center gap-2">
                <div className="p-2 bg-blue-600 rounded-lg shadow-lg">
                    {/* Placeholder for actual logo */}
                    <span className="text-white font-bold text-xl">JS</span>
                </div>
                <span className="hidden sm:block font-bold text-slate-800 dark:text-white">JanSathi</span>
            </div>

            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 rounded-full border border-blue-100 dark:border-blue-800">
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">
                        D
                    </div>
                    <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Demo User</span>
                </div>
            </div>
        </nav>
    );
}
