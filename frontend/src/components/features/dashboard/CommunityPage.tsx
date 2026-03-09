'use client';

import React, { useState, useEffect, useCallback } from "react";
import { MessageSquare, ThumbsUp, MapPin, Users, AlertTriangle, ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";
import { getCommunityPosts, createCommunityPost, reportFraud, getCommunityInsights, type CommunityInsightsResponse } from "@/services/api";
import { getToken } from "@/hooks/useAuth";

interface Post {
    id?: number | string;
    title: string;
    content: string;
    author: string;
    time: string;
    likes: number;
    comments: number;
    timestamp?: string;
    location?: string;
    author_role?: string;
}

const LOCAL_FORUM_POSTS_KEY = "jansathi_local_forum_posts";
const FALLBACK_LOCATION = "Varanasi";

const normalizePost = (raw: Partial<Post>): Post => {
    const fallbackTime =
        typeof raw.timestamp === "string"
            ? raw.timestamp.replace("T", " ").slice(0, 16)
            : new Date().toISOString().replace("T", " ").slice(0, 16);

    return {
        id: raw.id,
        title: (raw.title || "").trim(),
        content: (raw.content || "").trim(),
        author: (raw.author || "JanSathi User").trim(),
        time: (raw.time || fallbackTime).trim(),
        likes: Number(raw.likes ?? 0),
        comments: Number(raw.comments ?? 0),
        timestamp: raw.timestamp,
        location: raw.location,
        author_role: raw.author_role,
    };
};

// No mock posts as we are using real backend data

export default function CommunityPage() {
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newPost, setNewPost] = useState({ title: "", content: "" });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [insights, setInsights] = useState<CommunityInsightsResponse | null>(null);
    const [fraudDetails, setFraudDetails] = useState("");
    const [fraudAmount, setFraudAmount] = useState("");
    const location = FALLBACK_LOCATION;

    const loadLocalPosts = (): Post[] => {
        try {
            const raw = localStorage.getItem(LOCAL_FORUM_POSTS_KEY);
            if (!raw) return [];
            const parsed = JSON.parse(raw);
            if (!Array.isArray(parsed)) return [];
            return parsed.map((post) => normalizePost(post));
        } catch {
            return [];
        }
    };

    const storeLocalPost = (post: Post) => {
        const localPosts = loadLocalPosts();
        const next = [post, ...localPosts].slice(0, 50);
        localStorage.setItem(LOCAL_FORUM_POSTS_KEY, JSON.stringify(next));
    };

    const fetchPosts = useCallback(async () => {
        setError(null);
        try {
            const token = await getToken();
            const data = await getCommunityPosts(location, 20, token || undefined);
            const remotePosts = data.map((post: Record<string, unknown>) => normalizePost(post));
            setPosts(remotePosts);
        } catch (err) {
            console.error("Failed to fetch posts:", err);
            const localPosts = loadLocalPosts();
            setPosts(localPosts.length > 0 ? localPosts : []);
            setError("Direct forum connection unavailable. Showing local archives.");
        } finally {
            setLoading(false);
        }
    }, [location]);

    const handleCreatePost = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newPost.title.trim() || !newPost.content.trim()) return;

        setIsSubmitting(true);
        setError(null);
        try {
            const token = await getToken();
            const data = await createCommunityPost({
                title: newPost.title.trim(),
                content: newPost.content.trim(),
                location,
                author: "JanSathi User",
                role: "Citizen",
            }, token || undefined);
            
            if (data?.status === "success" && data?.post) {
                setPosts((prev) => [normalizePost(data.post), ...prev]);
                setIsModalOpen(false);
                setNewPost({ title: "", content: "" });
            } else {
                setError("Post could not be published.");
            }
        } catch (err) {
            console.error("Failed to create post:", err);
            const localPost = normalizePost({
                id: `local-${Date.now()}`,
                title: newPost.title.trim(),
                content: newPost.content.trim(),
                location,
                author: "JanSathi User",
                author_role: "Citizen",
                likes: 0,
                comments: 0,
                timestamp: new Date().toISOString(),
            });
            storeLocalPost(localPost);
            setPosts((prev) => [localPost, ...prev]);
            setError("Post saved locally. It will remain visible in your local forum.");
            setIsModalOpen(false);
            setNewPost({ title: "", content: "" });
        } finally {
            setIsSubmitting(false);
        }
    };

    useEffect(() => {
        fetchPosts();
    }, [fetchPosts]);

    useEffect(() => {
        (async () => {
            try {
                const data = await getCommunityInsights(location);
                setInsights(data);
            } catch (e) {
                console.error("Failed community insights fetch", e);
            }
        })();
    }, [location]);

    return (
        <div className="space-y-8 p-6 lg:p-10 max-w-4xl mx-auto">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-black tracking-tight text-foreground">Community</h1>
                    <p className="text-secondary-foreground font-medium mt-1">Connect with your local civic community.</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-bold text-sm shadow-md hover:opacity-90 transition-opacity"
                >
                    + New Post
                </button>
            </div>

            {error && (
                <motion.div 
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="rounded-xl border border-orange-500/30 bg-orange-500/10 px-4 py-3 text-sm text-orange-600 dark:text-orange-400 flex items-center gap-2"
                >
                    <AlertTriangle className="w-4 h-4" />
                    {error}
                </motion.div>
            )}

            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 text-blue-600 dark:text-blue-300 rounded-full text-xs font-bold uppercase tracking-widest border border-blue-500/20">
                <MapPin className="w-4 h-4" />
                <span>{location}, Uttar Pradesh</span>
            </div>

            {insights && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl border border-border/50 bg-card">
                        <p className="text-[10px] uppercase font-black tracking-wider text-secondary-foreground">Posts Analyzed</p>
                        <p className="text-2xl font-black text-foreground">{insights.posts_analyzed}</p>
                    </div>
                    <div className="p-4 rounded-xl border border-border/50 bg-card">
                        <p className="text-[10px] uppercase font-black tracking-wider text-secondary-foreground">Common Issue</p>
                        <p className="text-sm font-bold text-foreground">{insights.common_document_issue}</p>
                    </div>
                    <div className="p-4 rounded-xl border border-border/50 bg-card">
                        <p className="text-[10px] uppercase font-black tracking-wider text-secondary-foreground">Action</p>
                        <p className="text-sm font-bold text-foreground">{insights.recommended_action}</p>
                    </div>
                </div>
            )}

            <div className="p-5 rounded-2xl border border-red-500/30 bg-red-500/10">
                <h3 className="text-lg font-black text-foreground flex items-center gap-2 mb-3">
                    <ShieldAlert className="w-5 h-5 text-red-500" />
                    Middleman / Fraud Report
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <input
                        value={fraudDetails}
                        onChange={(e) => setFraudDetails(e.target.value)}
                        placeholder="Describe bribe or exploitation"
                        className="md:col-span-3 px-3 py-2 rounded-lg border border-border bg-background text-sm"
                    />
                    <input
                        value={fraudAmount}
                        onChange={(e) => setFraudAmount(e.target.value)}
                        placeholder="Amount ₹"
                        className="px-3 py-2 rounded-lg border border-border bg-background text-sm"
                    />
                </div>
                <button
                    onClick={async () => {
                        if (!fraudDetails.trim()) return;
                        try {
                            const token = await getToken();
                            await reportFraud({
                                location,
                                details: fraudDetails.trim(),
                                amount: Number(fraudAmount || 0),
                            }, token || undefined);
                            setFraudDetails("");
                            setFraudAmount("");
                            setError("Fraud pattern reported successfully.");
                        } catch {
                            setError("Unable to report now. Please retry.");
                        }
                    }}
                    className="mt-3 px-5 py-2 rounded-lg bg-red-600 text-white font-bold text-sm"
                >
                    Submit Report
                </button>
            </div>

            <div className="space-y-6">
                {loading ? (
                    <div className="flex justify-center p-20">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                ) : posts.length === 0 ? (
                    <div className="text-center p-20 bg-card rounded-2xl border border-dashed border-border">
                        <p className="text-secondary-foreground">No local posts found for your area.</p>
                    </div>
                ) : (
                    posts.map((post, i) => (
                        <div key={i} className="bg-card border border-border/50 rounded-2xl p-6">
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                                    <Users className="w-5 h-5 text-secondary-foreground" />
                                </div>
                                <div>
                                    <h4 className="font-bold text-foreground text-sm">{post.author}</h4>
                                    <p className="text-[10px] uppercase font-bold text-secondary-foreground opacity-60">{post.time}</p>
                                </div>
                            </div>

                            <h3 className="text-lg font-bold mb-2 text-foreground">{post.title}</h3>
                            <p className="text-secondary-foreground text-sm leading-relaxed mb-4">{post.content}</p>

                            <div className="flex gap-6 pt-4 border-t border-border/40">
                                <button className="flex items-center gap-2 text-sm font-bold text-secondary-foreground hover:text-primary transition-colors">
                                    <ThumbsUp className="w-4 h-4" />
                                    <span>{post.likes}</span>
                                </button>
                                <button className="flex items-center gap-2 text-sm font-bold text-secondary-foreground hover:text-primary transition-colors">
                                    <MessageSquare className="w-4 h-4" />
                                    <span>{post.comments} Comments</span>
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-card text-card-foreground w-full max-w-lg rounded-3xl p-8 border border-border shadow-2xl"
                    >
                        <h2 className="text-2xl font-black mb-6 text-card-foreground">Create New Post</h2>
                        <form onSubmit={handleCreatePost} className="space-y-4">
                            <div>
                                <label className="block text-[10px] font-black uppercase tracking-widest text-secondary-foreground mb-2">Title</label>
                                <input
                                    type="text"
                                    value={newPost.title}
                                    onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                                    className="w-full bg-secondary/50 text-foreground border border-border rounded-xl px-4 py-3 font-medium focus:ring-2 focus:ring-primary outline-none transition-all placeholder:text-secondary-foreground/50"
                                    placeholder="Brief topic..."
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-[10px] font-black uppercase tracking-widest text-secondary-foreground mb-2">Content</label>
                                <textarea
                                    value={newPost.content}
                                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                                    className="w-full bg-secondary/50 text-foreground border border-border rounded-xl px-4 py-3 font-medium focus:ring-2 focus:ring-primary outline-none transition-all min-h-[150px] placeholder:text-secondary-foreground/50"
                                    placeholder="Write your message to the community..."
                                    required
                                />
                            </div>
                            <div className="flex gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="flex-1 px-6 py-3 rounded-xl font-bold text-sm border border-border bg-secondary/30 text-foreground hover:bg-secondary transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="flex-1 bg-primary text-primary-foreground px-10 py-3 rounded-xl font-bold text-sm shadow-md hover:opacity-90 transition-opacity disabled:opacity-50"
                                >
                                    {isSubmitting ? "Posting..." : "Post Message"}
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </div>
            )}
        </div>
    );
}
