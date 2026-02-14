import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden transition-colors duration-500">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[120px] translate-x-1/2 translate-y-1/2"></div>

            <div className="relative z-10 w-full flex flex-col items-center">
                <SignUp
                    appearance={{
                        layout: {
                            socialButtonsPlacement: 'top',
                            showOptionalFields: false,
                        },
                        elements: {
                            rootBox: 'w-full flex justify-center',
                            card: 'glass-panel border border-border shadow-2xl rounded-3xl w-full max-w-md p-2',
                            headerTitle: 'text-foreground text-2xl font-black tracking-tight mb-1',
                            headerSubtitle: 'text-secondary-foreground text-sm mb-6',
                            socialButtonsBlockButton: 'bg-card hover:bg-secondary text-foreground border border-border rounded-xl font-bold py-3 transition-all duration-200 active:scale-95 mb-2 h-12 shadow-sm',
                            socialButtonsBlockButtonText: 'font-bold text-sm',
                            dividerRow: 'my-6',
                            dividerLine: 'bg-border h-[1px]',
                            dividerText: 'text-secondary-foreground text-[10px] uppercase tracking-widest font-black bg-background px-3',
                            formFieldLabel: 'text-foreground font-bold text-xs uppercase tracking-wider mb-2 ml-1 opacity-80',
                            formFieldInput: 'bg-input/50 border-border text-foreground rounded-xl py-[10px] px-4 focus:ring-2 focus:ring-primary/20 focus:border-primary/50 transition-all placeholder:text-muted h-10',
                            formButtonPrimary: 'bg-primary hover:bg-primary/90 text-primary-foreground font-black py-4 rounded-xl shadow-lg shadow-primary/20 active:scale-95 transition-all duration-200 mt-4 h-12 text-sm uppercase tracking-widest',
                            footerActionText: 'text-secondary-foreground font-medium',
                            footerActionLink: 'text-primary hover:text-primary/80 font-black transition-colors ml-1 underline underline-offset-4',
                            footer: 'hidden',
                            identityPreviewText: 'text-foreground font-bold',
                            identityPreviewEditButtonIcon: 'text-primary',
                            formResendCodeLink: 'text-primary font-bold',
                            otpCodeFieldInput: 'bg-input border-border text-foreground rounded-xl focus:ring-2 focus:ring-primary/20',
                        },
                        variables: {
                            colorPrimary: '#2563eb', // Fallback
                            colorBackground: 'transparent',
                            colorText: 'var(--foreground)',
                            colorTextSecondary: 'var(--secondary-foreground)',
                            colorInputText: 'var(--foreground)',
                            colorInputBackground: 'var(--input)',
                        }
                    }}
                    routing="path"
                    path="/sign-up"
                    signInUrl="/sign-in"
                    forceRedirectUrl="/dashboard"
                />
            </div>
        </div>
    );
}

