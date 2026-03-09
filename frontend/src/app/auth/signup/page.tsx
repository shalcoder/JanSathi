'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { Authenticator, View, useTheme, useAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

// Inner component — must live inside Authenticator.Provider to use useAuthenticator
function SignUpContent() {
    const router = useRouter();
    const { authStatus } = useAuthenticator(context => [context.authStatus]);

    useEffect(() => {
        if (authStatus === 'authenticated') {
            router.push('/onboarding');
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
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6 relative overflow-hidden">
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-background to-background"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md bg-card/80 backdrop-blur-2xl border border-border/50 rounded-3xl shadow-2xl overflow-hidden relative z-10"
            >
                <div className="p-8">
                    <Link href="/" className="inline-flex items-center gap-2 text-sm text-secondary-foreground hover:text-foreground mb-8 transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>

                    <div className="mb-4 text-center">
                        <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">Create Account</h1>
                        <p className="text-sm text-secondary-foreground font-medium opacity-70">Join the JanSathi Protocol</p>
                    </div>

                    <div className="amplify-auth-container">
                        <Authenticator 
                            initialState="signUp" 
                            components={components}
                        >
                            {() => (
                                <div className="text-center py-8 text-foreground font-medium">
                                    Account successfully created. Redirecting to profile setup...
                                </div>
                            )}
                        </Authenticator>
                    </div>
                </div>
            </motion.div>

            <style jsx global>{`
                /* ── Amplify token overrides ─────────────────────────────── */
                .amplify-auth-container {
                    --amplify-colors-background-primary: transparent;
                    --amplify-colors-background-secondary: var(--input);
                    --amplify-colors-font-primary: var(--foreground);
                    --amplify-colors-font-secondary: var(--secondary-foreground);
                    --amplify-colors-font-tertiary: var(--secondary-foreground);
                    --amplify-colors-font-interactive: var(--primary);

                    --amplify-colors-brand-primary-10: var(--primary);
                    --amplify-colors-brand-primary-80: var(--primary);
                    --amplify-colors-brand-primary-90: var(--primary);
                    --amplify-colors-brand-primary-100: var(--primary);

                    --amplify-components-button-primary-background-color: var(--primary);
                    --amplify-components-button-primary-hover-background-color: var(--primary);
                    --amplify-components-button-primary-color: #ffffff;
                    --amplify-components-fieldcontrol-focus-box-shadow: 0 0 0 2px var(--primary);
                    --amplify-components-button-link-color: var(--primary);

                    --amplify-components-tabs-item-active-color: var(--primary);
                    --amplify-components-tabs-item-active-border-color: var(--primary);
                    --amplify-components-tabs-item-color: var(--secondary-foreground);
                    --amplify-components-tabs-list-border-color: var(--border);
                    --amplify-components-tabs-item-background-color: transparent;
                    --amplify-components-tabs-panel-background-color: transparent;
                }

                /* ── Strip all Amplify-imposed backgrounds / borders ─────── */
                .amplify-auth-container [data-amplify-authenticator],
                [data-amplify-router],
                [data-amplify-router-content],
                [data-amplify-form],
                .amplify-tabs,
                .amplify-tabs__panel {
                    background: transparent !important;
                    border: none !important;
                    box-shadow: none !important;
                    padding-left: 0 !important;
                    padding-right: 0 !important;
                }

                /* ── Tabs ─────────────────────────────────────────────────── */
                .amplify-tabs__list {
                    border-bottom: 1px solid var(--border) !important;
                    background: transparent !important;
                    margin-bottom: 1.25rem;
                }
                .amplify-tabs__panel {
                    background: transparent !important;
                    padding-top: 0.5rem !important;
                }

                /* ── Labels ───────────────────────────────────────────────── */
                .amplify-label {
                    color: var(--secondary-foreground) !important;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 0.35rem;
                }

                /* ── Inputs / field controls ──────────────────────────────── */
                .amplify-field-group__control,
                .amplify-input,
                .amplify-select,
                .amplify-textarea {
                    background: var(--input) !important;
                    border: 1px solid var(--border) !important;
                    color: var(--foreground) !important;
                    border-radius: 0.75rem !important;
                }
                .amplify-field-group__control:focus,
                .amplify-input:focus {
                    outline: none !important;
                    border-color: var(--primary) !important;
                    box-shadow: 0 0 0 2px color-mix(in srgb, var(--primary) 25%, transparent) !important;
                }
                /* placeholder */
                .amplify-input::placeholder {
                    color: var(--secondary-foreground) !important;
                    opacity: 0.6;
                }

                /* ── Password show/hide button ────────────────────────────── */
                .amplify-field-group__icon-button {
                    color: var(--secondary-foreground) !important;
                    background: transparent !important;
                    border: none !important;
                }

                /* ── Primary button ───────────────────────────────────────── */
                .amplify-button[data-variation="primary"] {
                    background: var(--primary) !important;
                    color: #ffffff !important;
                    border-radius: 0.75rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.025em;
                    border: none !important;
                }
                .amplify-button[data-variation="primary"]:hover {
                    opacity: 0.9;
                }

                /* ── Link buttons ────────────────────────────────────────── */
                .amplify-button--link,
                .amplify-button[data-variation="link"] {
                    color: var(--primary) !important;
                    font-weight: 600;
                    background: transparent !important;
                    border: none !important;
                }

                /* ── Default / secondary buttons ─────────────────────────── */
                .amplify-button:not([data-variation="primary"]):not([data-variation="link"]) {
                    background: var(--secondary) !important;
                    color: var(--foreground) !important;
                    border: 1px solid var(--border) !important;
                    border-radius: 0.75rem;
                }

                /* ── Divider ─────────────────────────────────────────────── */
                .amplify-divider {
                    border-bottom-color: var(--border) !important;
                }
                .amplify-divider__label {
                    background: var(--card) !important;
                    color: var(--secondary-foreground) !important;
                    font-size: 0.7rem;
                    font-weight: 700;
                    text-transform: uppercase;
                }

                /* ── Error / alert text ──────────────────────────────────── */
                .amplify-alert,
                [data-amplify-qr] p,
                .amplify-text {
                    color: var(--foreground) !important;
                }

                /* ── Checkbox ────────────────────────────────────────────── */
                .amplify-checkbox__button {
                    border-color: var(--border) !important;
                    background: var(--input) !important;
                }
                .amplify-checkbox__label {
                    color: var(--secondary-foreground) !important;
                }
            `}</style>
        </div>
    );
}

// Wrap with Authenticator.Provider so useAuthenticator works inside SignUpContent
export default function SignUp() {
    return (
        <Authenticator.Provider>
            <SignUpContent />
        </Authenticator.Provider>
    );
}
