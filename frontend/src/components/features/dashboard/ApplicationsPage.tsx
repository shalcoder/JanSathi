import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle, XCircle, FileText, ChevronRight } from 'lucide-react';

interface Application {
    id: number;
    title: string;
    date: string;
    status: string;
    step: number;
    totalSteps: number;
}

export default function ApplicationsPage() {
    const [applications, setApplications] = useState<Application[]>([]);
    const [loading, setLoading] = useState(true);
    const userId = "demo-user"; // Usually from auth

    useEffect(() => {
        const fetchApps = async () => {
            try {
                const response = await fetch(`/api/applications?user_id=${userId}`);
                const data = await response.json();
                setApplications(data);
            } catch (error) {
                console.error("Failed to fetch applications:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchApps();
    }, [userId]);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'Approved': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
            case 'Rejected': return 'text-red-500 bg-red-500/10 border-red-500/20';
            default: return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'Approved': return CheckCircle;
            case 'Rejected': return XCircle;
            default: return Clock;
        }
    };

    return (
        <div className="space-y-8 p-6 lg:p-10 max-w-5xl mx-auto">
            <div>
                <h1 className="text-3xl font-black tracking-tight text-foreground">My Applications</h1>
                <p className="text-secondary-foreground font-medium mt-1">Track the status of your submitted applications.</p>
            </div>

            <div className="space-y-4">
                {loading ? (
                    <div className="flex justify-center p-20">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                ) : applications.length === 0 ? (
                    <div className="text-center p-20 bg-card rounded-2xl border border-dashed border-border">
                        <p className="text-secondary-foreground">No applications found.</p>
                    </div>
                ) : (
                    applications.map((app, i) => {
                        const StatusIcon = getStatusIcon(app.status);
                        const colorClass = getStatusColor(app.status);

                        return (
                            <motion.div
                                key={app.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="bg-card border border-border/50 rounded-2xl p-6 hover:shadow-lg transition-all group"
                            >
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">

                                    {/* Icon & Title */}
                                    <div className="flex items-start gap-4">
                                        <div className="p-3 bg-secondary rounded-xl">
                                            <FileText className="w-6 h-6 text-foreground" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-lg text-foreground">{app.title}</h3>
                                            <p className="text-xs text-secondary-foreground font-medium mt-1">ID: {app.id} • Submitted on {app.date}</p>
                                        </div>
                                    </div>

                                    {/* Status Badge */}
                                    <div className="flex items-center gap-4">
                                        <span className={`px-4 py-2 rounded-full border text-xs font-bold uppercase tracking-wider flex items-center gap-2 ${colorClass}`}>
                                            <StatusIcon className="w-4 h-4" />
                                            {app.status}
                                        </span>
                                        <button className="p-2 hover:bg-secondary rounded-full transition-colors text-secondary-foreground">
                                            <ChevronRight className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>

                                {/* Progress Bar (Only if pending or approved) */}
                                {app.status !== 'Rejected' && (
                                    <div className="mt-6 pt-6 border-t border-border/50">
                                        <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-secondary-foreground mb-2">
                                            <span>Submission</span>
                                            <span>Verification</span>
                                            <span>Approval</span>
                                            <span>Disbursement</span>
                                        </div>
                                        <div className="h-2 bg-secondary rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-primary transition-all duration-1000"
                                                style={{ width: `${(app.step / app.totalSteps) * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
