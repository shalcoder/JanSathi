'use client';

import React from 'react';
import { ExternalLink, CheckCircle, ShieldCheck, Award, ArrowUpRight, Activity } from 'lucide-react';

interface SchemeCardProps {
    title: string;
    description: string;
    link: string;
    benefit: string;
    logo?: string;
    related?: string[];
}

const SchemeCard: React.FC<SchemeCardProps> = ({ title, description, link, benefit, logo, related }) => {
    return (
        <div
            className="flex flex-col bg-card rounded-2xl border border-border overflow-hidden transition-all duration-300 group shadow-sm hover:shadow-md"
        >
            <div className="flex flex-col sm:flex-row p-6 sm:p-8 gap-6 items-start">

                {/* Logo Section */}
                <div
                    className="flex-shrink-0 w-20 h-20 sm:w-24 sm:h-24 bg-background rounded-2xl flex items-center justify-center p-3 sm:p-4 border border-border shadow-sm group-hover:border-primary/30 transition-colors"
                >
                    <img
                        src={logo || "https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"}
                        alt={`${title} Logo`}
                        className="w-full h-full object-contain"
                        onError={(e) => { e.currentTarget.src = 'https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg'; }}
                    />
                </div>

                {/* Content Section */}
                <div className="flex-1 space-y-4">
                    <div className="space-y-2">
                        <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-primary py-0.5 px-2 bg-primary/5 rounded border border-primary/10">Official Government Scheme</span>
                        </div>
                        <h3 className="font-bold text-2xl text-foreground leading-tight group-hover:text-primary transition-colors">
                            {title}
                        </h3>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        <span className="inline-flex items-center px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            {benefit}
                        </span>
                        <div className="inline-flex items-center px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-secondary border border-border">
                            Direct Transfer (DBT)
                        </div>
                    </div>

                    <p className="text-sm text-secondary-foreground font-medium opacity-70 leading-relaxed">
                        {description}
                    </p>

                    {related && related.length > 0 && (
                        <div className="pt-2">
                            <p className="text-[9px] font-black uppercase tracking-[0.2em] text-secondary-foreground opacity-30 mb-2">Knowledge Graph Suggestions</p>
                            <div className="flex flex-wrap gap-2">
                                {related.map((r, i) => (
                                    <span key={i} className="px-2 py-1 bg-secondary/50 rounded-md text-[9px] font-bold text-secondary-foreground border border-border/50">
                                        {r}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Action Footer */}
            <div className="bg-secondary/20 p-6 sm:px-8 flex flex-col sm:flex-row justify-between items-center gap-4 border-t border-border mt-auto">
                <div className="flex items-center gap-4">
                    <div>
                        <span className="text-[10px] text-secondary-foreground font-bold uppercase tracking-wider opacity-40">Verification</span>
                        <span className="text-[11px] text-foreground font-bold uppercase tracking-widest block">Aadhaar Enabled</span>
                    </div>
                </div>

                <a
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-xs font-bold text-white bg-primary rounded-xl transition-all shadow-md hover:opacity-90 gap-3"
                >
                    <span>Apply Now</span>
                    <ArrowUpRight className="w-5 h-5" />
                </a>
            </div>
        </div>
    );
};

export default SchemeCard;
