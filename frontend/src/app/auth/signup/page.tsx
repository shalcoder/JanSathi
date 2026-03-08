import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, UserPlus } from 'lucide-react';
import { Authenticator, View, Text, useTheme } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

export default function SignUp() {
    const components = {
        Header() {
            const { tokens } = useTheme();
            return (
                <View textAlign="center" padding={tokens.space.large}>
                    <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-4">
                        <UserPlus className="w-6 h-6 text-primary" />
                    </div>
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
                className="w-full max-w-md bg-card border border-border/50 rounded-3xl shadow-2xl overflow-hidden relative z-10"
            >
                <div className="p-8">
                    <Link href="/" className="inline-flex items-center gap-2 text-sm text-secondary-foreground hover:text-foreground mb-8 transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>

                    <div className="mb-4 text-center">
                        <h1 className="text-2xl font-bold text-foreground">Create Account</h1>
                        <p className="text-secondary-foreground">Join the JanSathi Protocol</p>
                    </div>

                    <div className="amplify-auth-container">
                        <Authenticator initialState="signUp" components={components}>
                            {() => (
                                <div className="text-center py-8">
                                    <Text>Redirecting to dashboard...</Text>
                                    <meta httpEquiv="refresh" content="0; url=/dashboard" />
                                </div>
                            )}
                        </Authenticator>
                    </div>
                </div>
            </motion.div>

            <style jsx global>{`
                .amplify-auth-container [data-amplify-authenticator] {
                    --amplify-colors-brand-primary-10: var(--primary);
                    --amplify-colors-brand-primary-80: var(--primary);
                    --amplify-colors-brand-primary-90: var(--primary);
                    --amplify-colors-brand-primary-100: var(--primary);
                    --amplify-components-button-primary-background-color: var(--primary);
                    --amplify-components-button-primary-hover-background-color: var(--primary);
                    --amplify-components-fieldcontrol-focus-box-shadow: 0 0 0 2px var(--primary);
                    background: transparent;
                    border: none;
                    box-shadow: none;
                }
                .amplify-tabs {
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                }
                .amplify-tabs-item--active {
                    border-color: var(--primary) !important;
                    color: var(--primary) !important;
                }
                .amplify-heading {
                    color: white !important;
                }
                .amplify-label {
                    color: rgba(255,255,255,0.6) !important;
                }
                .amplify-input {
                    background: rgba(255,255,255,0.05) !important;
                    border: 1px solid rgba(255,255,255,0.1) !important;
                    color: white !important;
                }
            `}</style>
        </div>
    );
}
