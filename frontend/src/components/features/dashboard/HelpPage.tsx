import React from 'react';
import { HelpCircle, Phone, Mail, FileQuestion, BookOpen } from 'lucide-react';

export default function HelpPage() {
    return (
        <div className="space-y-8 p-6 lg:p-10 max-w-4xl mx-auto">
            <div>
                <h1 className="text-3xl font-black tracking-tight text-foreground">Help & Support</h1>
                <p className="text-secondary-foreground font-medium mt-1">Get assistance with JanSathi services.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-6 bg-card border border-border/50 rounded-2xl">
                    <FileQuestion className="w-8 h-8 text-primary mb-4" />
                    <h3 className="text-lg font-bold mb-2">FAQs</h3>
                    <p className="text-sm text-secondary-foreground mb-4">Find answers to common questions about schemes and applications.</p>
                    <button className="text-primary font-bold text-sm hover:underline">Browse FAQs</button>
                </div>

                <div className="p-6 bg-card border border-border/50 rounded-2xl">
                    <BookOpen className="w-8 h-8 text-purple-500 mb-4" />
                    <h3 className="text-lg font-bold mb-2">User Guide</h3>
                    <p className="text-sm text-secondary-foreground mb-4">Learn how to navigate the app and use the voice assistant effectively.</p>
                    <button className="text-purple-500 font-bold text-sm hover:underline">Read Guide</button>
                </div>
            </div>

            <h2 className="text-xl font-bold mt-8">Contact Us</h2>
            <div className="space-y-4">
                <div className="flex items-center gap-4 p-4 bg-secondary/10 rounded-xl border border-border/50">
                    <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                        <Phone className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className="font-bold">Helpline (Toll Free)</h4>
                        <p className="text-sm text-secondary-foreground">1800-XXX-XXXX (9 AM - 6 PM)</p>
                    </div>
                </div>

                <div className="flex items-center gap-4 p-4 bg-secondary/10 rounded-xl border border-border/50">
                    <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500">
                        <Mail className="w-5 h-5" />
                    </div>
                    <div>
                        <h4 className="font-bold">Email Support</h4>
                        <p className="text-sm text-secondary-foreground">support@jansathi.gov.in</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
