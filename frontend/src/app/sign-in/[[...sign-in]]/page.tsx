'use client';

import { SignIn } from "@clerk/nextjs";
import CustomAuth from "@/components/auth/CustomAuth";
import { useParams } from "next/navigation";

export default function SignInPage() {
    const params = useParams();
    // If params is undefined or empty array, we are at root /sign-in
    const isRoot = !params?.['sign-in'] || params['sign-in'].length === 0;

    return (
        <div className="min-h-screen bg-black flex items-center justify-center p-4 relative overflow-hidden transition-colors duration-500">
            {/* Dark background with subtle gradient */}
            <div className="absolute inset-0 bg-gradient-to-b from-gray-950 to-black z-0"></div>

            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[120px] translate-x-1/2 translate-y-1/2"></div>

            <div className="relative z-10 w-full flex flex-col items-center">
                {isRoot ? (
                    <div className="w-full max-w-md">
                        <CustomAuth mode="signIn" />
                    </div>
                ) : (
                    <SignIn
                        appearance={{
                            layout: {
                                socialButtonsPlacement: 'top',
                                showOptionalFields: false,
                            },
                            elements: {
                                rootBox: 'w-full flex justify-center',
                                card: 'glass-panel border border-border shadow-2xl rounded-3xl w-full max-w-md p-6 bg-[#0a0a0a] border-[#333]',
                                headerTitle: 'text-white text-2xl font-bold mb-1',
                                headerSubtitle: 'text-gray-400 text-sm mb-6',
                                formButtonPrimary: 'bg-white hover:bg-gray-200 text-black font-bold py-3 rounded-lg w-full',
                                formFieldInput: 'bg-[#1a1a1a] border-[#333] text-white rounded-lg focus:ring-2 focus:ring-blue-500',
                                formFieldLabel: 'text-gray-400',
                                footerActionText: 'text-gray-400',
                                footerActionLink: 'text-blue-500 hover:text-blue-400',
                                identityPreviewText: 'text-white',
                                formResendCodeLink: 'text-blue-500',
                            },
                            variables: {
                                colorPrimary: '#ffffff',
                                colorBackground: '#0a0a0a',
                                colorText: '#ffffff',
                                colorInputText: '#ffffff',
                                colorInputBackground: '#1a1a1a',
                            }
                        }}
                    />
                )}
            </div>
        </div>
    );
}
