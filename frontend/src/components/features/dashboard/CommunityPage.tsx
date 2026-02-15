import React, { useState, useEffect } from 'react';
import { MessageSquare, ThumbsUp, MapPin, Users } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function CommunityPage() {
    const [posts, setPosts] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newPost, setNewPost] = useState({ title: '', content: '' });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const location = "Varanasi"; // Mock location for now, usually from user profile

    const handleCreatePost = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newPost.title || !newPost.content) return;

        setIsSubmitting(true);
        try {
            const response = await fetch('/api/community/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: newPost.title,
                    content: newPost.content,
                    location: location,
                    author: "JanSathi User", // In real app, from user profile
                    role: "Citizen"
                })
            });
            const data = await response.json();
            if (data.status === 'success') {
                setPosts([data.post, ...posts]);
                setIsModalOpen(false);
                setNewPost({ title: '', content: '' });
            }
        } catch (error) {
            console.error("Failed to create post:", error);
        } finally {
            setIsSubmitting(false);
        }
    };

    useEffect(() => {
        const fetchPosts = async () => {
            try {
                const response = await fetch(`/api/community/posts?location=${location}`);
                const data = await response.json();
                setPosts(data);
            } catch (error) {
                console.error("Failed to fetch posts:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchPosts();
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

            {/* Location Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 text-blue-500 rounded-full text-xs font-bold uppercase tracking-widest">
                <MapPin className="w-4 h-4" />
                <span>{location}, Uttar Pradesh</span>
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
                                    <p className="text-[10px] uppercase font-bold text-secondary-foreground opacity-50">{post.time}</p>
                                </div>
                            </div>

                            <h3 className="text-lg font-bold mb-2">{post.title}</h3>
                            <p className="text-secondary-foreground text-sm leading-relaxed mb-4">{post.content}</p>

                            <div className="flex gap-6 pt-4 border-t border-border/30">
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

            {/* New Post Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-card w-full max-w-lg rounded-3xl p-8 border border-border shadow-2xl"
                    >
                        <h2 className="text-2xl font-black mb-6">Create New Post</h2>
                        <form onSubmit={handleCreatePost} className="space-y-4">
                            <div>
                                <label className="block text-[10px] font-black uppercase tracking-widest text-secondary-foreground mb-2">Title</label>
                                <input
                                    type="text"
                                    value={newPost.title}
                                    onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                                    className="w-full bg-secondary/50 border border-border rounded-xl px-4 py-3 font-medium focus:ring-2 focus:ring-primary outline-none transition-all"
                                    placeholder="Brief topic..."
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-[10px] font-black uppercase tracking-widest text-secondary-foreground mb-2">Content</label>
                                <textarea
                                    value={newPost.content}
                                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                                    className="w-full bg-secondary/50 border border-border rounded-xl px-4 py-3 font-medium focus:ring-2 focus:ring-primary outline-none transition-all min-h-[150px]"
                                    placeholder="Write your message to the community..."
                                    required
                                />
                            </div>
                            <div className="flex gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="flex-1 px-6 py-3 rounded-xl font-bold text-sm border border-border hover:bg-secondary transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="flex-2 bg-primary text-primary-foreground px-10 py-3 rounded-xl font-bold text-sm shadow-md hover:opacity-90 transition-opacity disabled:opacity-50"
                                >
                                    {isSubmitting ? 'Posting...' : 'Post Message'}
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </div>
            )}
        </div>
    );
}
