'use client';

import { SignIn } from "@clerk/nextjs";
import CustomAuth from "@/components/auth/CustomAuth";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, CheckCircle2 } from "lucide-react";

export default function SignInPage() {
    const params = useParams();
    const isRoot = !params?.['sign-in'] || params['sign-in'].length === 0;

    return (
        <div className="min-h-screen bg-background flex w-full relative overflow-hidden transition-colors duration-500">
            {/* Left Side: Premium Branding & Imagery */}
            <div className="hidden lg:flex w-1/2 relative flex-col justify-between p-12 border-r border-border/50 overflow-hidden bg-zinc-950">
                <div className="absolute inset-0 bg-gradient-to-br from-zinc-950 via-zinc-950 to-zinc-900 z-0"></div>
                <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 pointer-events-none z-0"></div>
                <div className="absolute -left-[20%] -top-[20%] w-[800px] h-[800px] bg-orange-600/10 rounded-full blur-[120px] pointer-events-none z-0"></div>
                
                <div className="relative z-10">
                    <Link href="/" className="inline-flex items-center gap-3 group cursor-pointer">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-orange-600 flex items-center justify-center shadow-lg">
                            <span className="font-bold text-xl text-white">JS</span>
                        </div>
                        <span className="text-2xl font-bold tracking-tight text-white transition-colors">JanSathi</span>
                    </Link>
                </div>

                <div className="relative z-10 max-w-md">
                    <h2 className="text-4xl font-black text-white mb-6 leading-tight">
                        Empowering <br/><span className="text-primary">the Last Mile.</span>
                    </h2>
                    <p className="text-zinc-400 text-lg mb-8 leading-relaxed">
                        Access the Agentic Command Center to monitor the 10-layer pipeline, review HITL cases, and manage local deployments.
                    </p>
                    <ul className="space-y-4">
                        {["Secure DPDP-compliant Hash Chain", "Real-time AWS Connect IVR Streams", "Automated Policy Evaluation Traces"].map((item, i) => (
                            <li key={i} className="flex items-center gap-3 text-zinc-300 font-medium">
                                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="relative z-10 text-sm text-zinc-600 font-medium">
                    © 2026 JanSathi Protocol. Internal Portal.
                </div>
            </div>

            {/* Right Side: Auth Form */}
            <div className="w-full lg:w-1/2 flex flex-col relative justify-center items-center py-12 px-4 sm:px-12 bg-background">
                <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[100px] pointer-events-none -z-10"></div>
                
                <div className="w-full max-w-md lg:hidden flex justify-start mb-12">
                     <Link href="/" className="inline-flex items-center gap-2 text-secondary-foreground hover:text-foreground transition-colors">
                        <ArrowLeft className="w-4 h-4" /> Back to Home
                    </Link>
                </div>

                <div className="relative z-10 w-full flex flex-col items-center">
                    {isRoot ? (
                        <div className="w-full">
                            <CustomAuth mode="signIn" />
                        </div>
                    ) : (
                        <SignIn
                            appearance={{
                                layout: {
                                    socialButtonsPlacement: 'top',
                                },
                                elements: {
                                    rootBox: "w-full max-w-md",
                                    card: "bg-card backdrop-blur-2xl border border-border/50 shadow-2xl rounded-[2rem] p-6 w-full",
                                    headerTitle: "text-foreground text-2xl font-bold mb-1",
                                    headerSubtitle: "text-secondary-foreground text-sm mb-6",
                                    socialButtonsBlockButton: "bg-secondary border border-border/50 hover:bg-secondary/80 text-foreground rounded-xl mb-3",
                                    formButtonPrimary: "bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl py-3 font-bold w-full",
                                    formFieldInput: "bg-secondary border border-border/50 text-foreground rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent",
                                    formFieldLabel: "text-secondary-foreground font-medium",
                                    footerActionText: "text-secondary-foreground",
                                    footerActionLink: "text-primary hover:text-primary/80 font-bold ml-1",
                                    dividerLine: "bg-border/50",
                                    dividerText: "text-secondary-foreground text-xs",
                                    identityPreviewText: "text-foreground",
                                    identityPreviewEditButton: "text-primary hover:text-primary/80",
                                }
                            }}
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
