'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft, Lock } from 'lucide-react';
import { Authenticator, useAuthenticator, View, Text, Heading, Button, useTheme } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

export default function SignIn() {
    const router = useRouter();
    const { authStatus } = useAuthenticator(context => [context.authStatus]);

    useEffect(() => {
        if (authStatus === 'authenticated') {
            router.push('/dashboard');
        }
    }, [authStatus, router]);

    const components = {
        Header() {
            const { tokens } = useTheme();
            return (
                <View textAlign="center" padding={tokens.space.large}>
                    <div className="mx-auto w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-orange-500/20 mb-4">JS</div>
                </View>
            );
        },
        Footer() {
            const { tokens } = useTheme();
            return (
                <View textAlign="center" padding={tokens.space.large}>
                    <Text color={tokens.colors.neutral[80]} fontSize="0.75rem">
                        &copy; 2026 JanSathi Protocol. All Rights Reserved.
                    </Text>
                </View>
            );
        },
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Ambience */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md bg-card/80 backdrop-blur-2xl border border-border/50 rounded-3xl shadow-2xl overflow-hidden relative z-10"
            >
                <div className="p-8">
                    <Link href="/" className="inline-flex items-center gap-2 text-sm text-secondary-foreground hover:text-foreground mb-8 transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>

                    <div className="mb-4 text-center">
                        <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">Welcome Back</h1>
                        <p className="text-sm text-secondary-foreground font-medium opacity-70">Sign in with your Bharat Cloud ID</p>
                    </div>

                    <div className="amplify-auth-container">
                        <Authenticator 
                            socialProviders={['google', 'apple', 'facebook', 'amazon']} 
                            components={components}
                        >
                            {({ signOut, user }) => (
                                <div className="text-center py-8">
                                    <Heading level={4} color="white">Hello {user?.username}</Heading>
                                    <Button onClick={signOut} variation="primary" marginTop="1rem">
                                        Sign Out
                                    </Button>
                                </div>
                            )}
                        </Authenticator>
                    </div>
                </div>

                <div className="bg-secondary/10 p-4 text-center border-t border-border/50">
                    <p className="text-[10px] text-secondary-foreground opacity-60 font-bold uppercase tracking-widest">
                        Secure Access powered by AWS Cognito
                    </p>
                </div>
            </motion.div>

            <style jsx global>{`
                .amplify-auth-container {
                    /* Next-gen overrides for standard Amplify UI */
                    --amplify-colors-background-primary: transparent;
                    --amplify-colors-background-secondary: rgba(255, 255, 255, 0.03);
                    --amplify-colors-font-primary: #ffffff;
                    --amplify-colors-font-secondary: #a1a1aa;
                    --amplify-colors-font-tertiary: #71717a;
                    --amplify-colors-font-interactive: white;
                    
                    --amplify-colors-brand-primary-10: var(--primary);
                    --amplify-colors-brand-primary-80: var(--primary);
                    --amplify-colors-brand-primary-90: var(--primary);
                    --amplify-colors-brand-primary-100: var(--primary);
                    
                    --amplify-components-button-primary-background-color: var(--primary);
                    --amplify-components-button-primary-hover-background-color: var(--primary);
                    --amplify-components-fieldcontrol-focus-box-shadow: 0 0 0 2px var(--primary);
                    --amplify-components-button-link-color: var(--primary);
                    
                    --amplify-components-tabs-item-active-color: var(--primary);
                    --amplify-components-tabs-item-active-border-color: var(--primary);
                    --amplify-components-tabs-item-color: #a1a1aa;
                    --amplify-components-tabs-list-border-color: rgba(255, 255, 255, 0.1);
                }
                
                .amplify-auth-container [data-amplify-authenticator] {
                    background: transparent;
                    border: none;
                    box-shadow: none;
                    padding: 0;
                }
                
                [data-amplify-router] {
                    background: transparent;
                    border: none;
                    box-shadow: none;
                }
                
                .amplify-field-group__control {
                    background: rgba(255,255,255,0.05) !important;
                    border: 1px solid rgba(255,255,255,0.1) !important;
                    color: white !important;
                    border-radius: 0.75rem !important;
                }
                
                .amplify-label {
                    color: rgba(255,255,255,0.7) !important;
                    font-size: 0.8rem;
                    font-weight: 600;
                    margin-bottom: 0.25rem;
                }
                
                .amplify-input {
                    color: white !important;
                    background: transparent !important;
                }
                
                .amplify-button[data-variation="primary"] {
                    border-radius: 0.75rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.025em;
                }
                
                .amplify-button--link {
                    color: var(--primary) !important;
                    font-weight: 600;
                }

                .amplify-divider {
                    border-bottom-color: rgba(255, 255, 255, 0.1);
                }
                .amplify-divider__label {
                    background: #121212;
                    color: rgba(255, 255, 255, 0.5);
                    font-size: 0.7rem;
                    font-weight: 700;
                    text-transform: uppercase;
                }
                
                .amplify-tabs {
                    border: none !important;
                }
            `}</style>
        </div>
    );
}
