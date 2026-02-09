import React from 'react';
import { ExternalLink, CheckCircle } from 'lucide-react';

interface SchemeCardProps {
    title: string;
    description: string;
    link: string;
    benefit: string;
    logo?: string;
}

const SchemeCard: React.FC<SchemeCardProps> = ({ title, description, link, benefit, logo }) => {
    return (
        <div className="flex flex-col bg-slate-900 rounded-[2rem] shadow-premium hover:shadow-premium-hover border border-white/5 overflow-hidden transition-all duration-500 group">
            <div className="flex flex-row p-6 gap-5 items-start">
                {/* Logo Section */}
                <div className="flex-shrink-0 w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center p-3 border border-white/10 shadow-inner overflow-hidden">
                    <img
                        src={logo || "/globe.svg"}
                        alt={`${title} Logo`}
                        className="w-full h-full object-contain group-hover:scale-110 transition-transform duration-500"
                        onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg'; // Fallback to Indian Emblem
                        }}
                    />
                </div>

                {/* Content Section */}
                <div className="flex-1">
                    <div className="flex justify-between items-start mb-2">
                        <h3 className="font-black text-xl text-white leading-tight tracking-tight transition-colors">
                            {title}
                        </h3>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-3">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            <CheckCircle className="w-3 h-3 mr-1.5" />
                            {benefit}
                        </span>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest bg-blue-500/10 text-blue-400 border border-blue-500/20">
                            Verified
                        </span>
                    </div>

                    <p className="text-sm text-slate-400 font-semibold leading-relaxed line-clamp-2 transition-colors">
                        {description}
                    </p>
                </div>
            </div>

            {/* Action Footer */}
            <div className="bg-white/[0.02] p-4 px-6 flex justify-between items-center border-t border-white/5 transition-colors">
                <span className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em]">Official Government Scheme</span>
                <a
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center px-6 py-2 text-sm font-black text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-all shadow-xl shadow-blue-600/20 gap-2 group/btn active:scale-95"
                >
                    Apply Now
                    <ExternalLink className="w-4 h-4 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                </a>
            </div>
        </div>
    );
};

export default SchemeCard;
