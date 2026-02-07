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
        <div className="flex flex-col bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden hover:shadow-xl transition-shadow duration-300">
            <div className="flex flex-row p-4 gap-4 items-start">
                {/* Logo Section */}
                <div className="flex-shrink-0 w-16 h-16 bg-slate-50 dark:bg-slate-900 rounded-lg flex items-center justify-center p-2 border border-slate-100 dark:border-slate-700">
                    <img
                        src={logo || "/globe.svg"}
                        alt={`${title} Logo`}
                        className="w-full h-full object-contain"
                        onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg'; // Fallback to Indian Emblem
                        }}
                    />
                </div>

                {/* Content Section */}
                <div className="flex-1">
                    <div className="flex justify-between items-start">
                        <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 leading-tight mb-1">
                            {title}
                        </h3>
                    </div>

                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 mb-2">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        {benefit}
                    </span>

                    <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 mb-3">
                        {description}
                    </p>
                </div>
            </div>

            {/* Action Footer */}
            <div className="bg-slate-50 dark:bg-slate-900 p-3 px-4 flex justify-between items-center border-t border-slate-200 dark:border-slate-700">
                <span className="text-xs text-slate-500 font-medium">Official Gov Scheme</span>
                <a
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-colors shadow-sm gap-2 group"
                >
                    Apply Now
                    <ExternalLink className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </a>
            </div>
        </div>
    );
};

export default SchemeCard;
