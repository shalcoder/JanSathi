'use client';

import { Authenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import CustomAuth from "@/components/auth/CustomAuth";
import { useParams, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";

export default function SignUpPage() {
    const params = useParams();
    const router = useRouter();
    const { isAuthenticated, loading } = useAuth();
    
    useEffect(() => {
        if (!loading && isAuthenticated) {
            router.push('/dashboard');
        }
    }, [isAuthenticated, loading, router]);

    const isRoot = !params?.['sign-up'] || params['sign-up'].length === 0;

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
                        <CustomAuth mode="signUp" />
                    </div>
                ) : (
                        <div className="w-full max-w-md bg-card backdrop-blur-2xl border border-border/50 shadow-2xl rounded-[2rem] p-6 text-foreground">
                            <Authenticator initialState="signUp">
                                {({ signOut, user }) => (
                                    <div className="text-center">
                                        <h2 className="text-xl font-bold mb-4 text-foreground">Welcome {user?.username}</h2>
                                        <button 
                                            onClick={() => router.push('/dashboard')}
                                            className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl py-3 font-bold w-full mb-3"
                                        >
                                            Go to Dashboard
                                        </button>
                                        <button 
                                            onClick={signOut}
                                            className="bg-secondary border border-border/50 hover:bg-secondary/80 text-foreground rounded-xl py-3 font-bold w-full"
                                        >
                                            Sign out
                                        </button>
                                    </div>
                                )}
                            </Authenticator>
                        </div>
                )}
            </div>
        </div>
    );
}
