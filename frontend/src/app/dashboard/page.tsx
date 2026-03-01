'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from "@/components/layout/Sidebar";
import TelemetryPanel from "@/components/layout/TelemetryPanel";
import ChatInterface from "@/components/features/chat/ChatInterface";
import DocumentsPage from "@/components/features/dashboard/DocumentsPage";
import ProfilePage from "@/components/features/dashboard/ProfilePage";
import SettingsPage from "@/components/features/dashboard/SettingsPage";
import OverviewPage from "@/components/features/dashboard/OverviewPage";
import SchemesPage from "@/components/features/dashboard/SchemesPage";
import ApplicationsPage from "@/components/features/dashboard/ApplicationsPage";
import CommunityPage from "@/components/features/dashboard/CommunityPage";
import HelpPage from "@/components/features/dashboard/HelpPage";
import IVRMonitor from "@/components/features/dashboard/IVRMonitor";
import { Menu, Sun, Moon, Search, Bell, PhoneCall, LayoutDashboard, FileText, Settings, User, Users, HelpCircle } from 'lucide-react';
import { useUser, useAuth, UserButton } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { buildClient } from '@/services/api';

export default function Home() {
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const [activePage, setActivePage] = useState('overview');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);

  // Semantic notification types
  const [notifications, setNotifications] = useState([
    { title: "PM-Kisan Installment", time: "2m ago", desc: "Your 16th installment has been processed.", type: "success" },
    { title: "Weather Alert", time: "1h ago", desc: "Heavy rain forecast for your district.", type: "warning" },
    { title: "System Update", time: "5h ago", desc: "JanSathi v2.5 features live now.", type: "info" }
  ]);
  const [unreadCount, setUnreadCount] = useState(3);

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success': return 'bg-emerald-500';
      case 'warning': return 'bg-amber-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-blue-500'; // info
    }
  };

  const handleMarkAllRead = () => {
    setUnreadCount(0);
  };

  const handleViewAllActivity = () => {
    // For now, redirect to notifications or show a toast
    alert("Redirecting to full activity log...");
  };

  // Simulate real-time notification
  useEffect(() => {
    const timer = setTimeout(() => {
      const newNotification = {
        title: "New Scheme Matched",
        time: "Just now",
        desc: "You are eligible for PM-Vishwakarma based on your profile.",
        type: "success"
      };
      setNotifications(prev => [newNotification, ...prev]);
      setUnreadCount(prev => prev + 1);
    }, 5000); // 5 seconds delay

    return () => clearTimeout(timer);
  }, []);

  // Initialize and check user
  useEffect(() => {
    async function checkProfile() {
      if (!isLoaded || !user) return;
      
      try {
        const token = await getToken();
        if (!token) return;
        
        const api = buildClient(token);
        const res = await api.get('/v1/profile');
        if (res.data?.profile?.profile_complete === false) {
           router.push('/onboarding');
        } else {
           setIsLoadingProfile(false);
        }
      } catch (err) {
        console.error("Failed to check profile status:", err);
        setIsLoadingProfile(false);
      }
    }
    checkProfile();
  }, [isLoaded, user, router, getToken]);

  useEffect(() => {
    const initializeTheme = () => {
      const root = window.document.documentElement;
      const initialColorValue = localStorage.getItem('jansathi-theme') || 'dark';

      if (initialColorValue === 'dark') {
        root.classList.add('dark');
        setIsDarkMode(true);
      } else {
        root.classList.remove('dark');
        setIsDarkMode(false);
      }
    };
    initializeTheme();
  }, []);

  const toggleTheme = () => {
    const root = window.document.documentElement;
    if (isDarkMode) {
      root.classList.remove('dark');
      localStorage.setItem('jansathi-theme', 'light');
      setIsDarkMode(false);
    } else {
      root.classList.add('dark');
      localStorage.setItem('jansathi-theme', 'dark');
      setIsDarkMode(true);
    }
  };

  const renderContent = () => {
    switch (activePage) {
      case 'overview':
        return <OverviewPage onNavigate={setActivePage} />;
      case 'assistant':
      case 'dashboard': // Legacy fallback
        return <ChatInterface />;
      case 'schemes':
        return <SchemesPage />;
      case 'applications':
        return <ApplicationsPage />;
      case 'community':
        return <CommunityPage />;
      case 'documents':
        return <DocumentsPage />;
      case 'profile':
        return <ProfilePage />;
      case 'settings':
        return <SettingsPage />;
      case 'help':
        return <HelpPage />;
      case 'ivr':
        return <IVRMonitor />;
      default:
        return <OverviewPage onNavigate={setActivePage} />;
    }
  };

  if (isLoadingProfile) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-background text-foreground">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <main className="h-screen w-full flex bg-background text-foreground overflow-hidden relative selection:bg-primary/20 transition-colors">

      {/* Simplified Background */}
      <div className="fixed inset-0 z-[-1] bg-background"></div>
      <div className="mesh-bg opacity-30"></div>

      {/* 1. Sidebar Navigation */}
      <div className={`
        fixed inset-0 z-50 lg:relative lg:inset-auto lg:flex
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        transition-transform duration-300 ease-in-out
      `}>
        <div className="absolute inset-0 bg-black/20 lg:hidden" onClick={() => setIsSidebarOpen(false)}></div>
        <div className="relative h-full w-72 flex-shrink-0">
          <Sidebar
            activePage={activePage}
            onPageChange={(p) => {
              setActivePage(p);
              setIsSidebarOpen(false);
            }}
            onNewChat={() => {
              sessionStorage.removeItem('current_jansathi_session');
              if (activePage === 'dashboard') {
                window.location.reload();
              } else {
                setActivePage('dashboard');
              }
            }}
          />
        </div>
      </div>

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col h-full relative z-10 transition-all min-w-0 overflow-hidden">

        {/* Clean Header */}
        <header className="px-6 py-4 flex items-center justify-between bg-card border-b border-border lg:px-10 shrink-0 z-20">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 hover:bg-secondary rounded-lg lg:hidden transition-colors"
            >
              <Menu className="w-6 h-6 text-foreground" />
            </button>

            {/* Status Pill - More responsive */}
            <div className="flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 rounded-full bg-secondary/50 border border-border group cursor-default">
              <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-emerald-500 rounded-full"></div>
              <span className="text-[9px] sm:text-[10px] uppercase font-bold tracking-widest text-foreground opacity-60">Online</span>
            </div>

            {/* Search Bar - Responsive width */}
            <div className="hidden sm:flex items-center gap-3 px-4 py-2 bg-secondary/30 border border-border/50 rounded-xl transition-all">
              <Search className="w-4 h-4 text-secondary-foreground opacity-40" />
              <input
                type="text"
                placeholder="Search..."
                className="bg-transparent border-none text-[13px] font-medium text-foreground placeholder:opacity-40 focus:outline-none w-24 md:w-44"
              />
            </div>
          </div>

          <div className="flex items-center gap-4 lg:gap-6">
            {/* Theme Toggle */}
            <button onClick={toggleTheme} className="p-2.5 bg-secondary/50 hover:bg-secondary rounded-xl transition-colors border border-border/50">
              {isDarkMode ?
                <Sun className="w-5 h-5 text-amber-500" /> :
                <Moon className="w-5 h-5 text-indigo-500" />
              }
            </button>

            {/* Notification Bell & Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2.5 bg-secondary/50 hover:bg-secondary rounded-xl transition-colors border border-border/50 relative active:scale-95"
              >
                <Bell className="w-5 h-5 text-secondary-foreground" />
                {unreadCount > 0 && (
                  <div className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-background animate-pulse"></div>
                )}
              </button>

              <AnimatePresence>
                {showNotifications && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    className="absolute top-full right-0 mt-3 w-80 bg-card border border-border/50 rounded-2xl shadow-xl z-50 overflow-hidden backdrop-blur-xl"
                  >
                    <div className="p-4 border-b border-border/50 flex justify-between items-center bg-card">
                      <span className="text-xs font-bold uppercase tracking-widest text-foreground">Notifications</span>
                      {unreadCount > 0 && (
                        <button
                          onClick={handleMarkAllRead}
                          className="text-[10px] font-bold text-primary hover:text-primary/80 transition-colors"
                        >
                          Mark all read
                        </button>
                      )}
                    </div>
                    <div className="max-h-[300px] overflow-y-auto scrollbar-thin bg-card">
                      {notifications.map((item, i) => (
                        <div key={i} className="p-4 hover:bg-secondary/20 transition-colors cursor-pointer border-b border-border/30 last:border-none flex gap-3">
                          <div className={`w-2 h-2 mt-1.5 shrink-0 rounded-full ${getNotificationColor(item.type)} ${unreadCount === 0 ? 'opacity-50' : ''}`}></div>
                          <div className={unreadCount === 0 ? 'opacity-60' : ''}>
                            <p className="text-sm font-bold text-foreground leading-none mb-1">{item.title}</p>
                            <p className="text-xs text-secondary-foreground opacity-80 leading-snug mb-1.5">{item.desc}</p>
                            <p className="text-[9px] font-bold text-secondary-foreground opacity-40 uppercase tracking-widest">{item.time}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="p-3 bg-card text-center border-t border-border/50">
                      <button
                        onClick={handleViewAllActivity}
                        className="text-[10px] font-bold text-foreground opacity-60 hover:opacity-100 uppercase tracking-widest transition-opacity"
                      >
                        View All Activity
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* User Identity - Clerk Avatar */}
            <div className="hidden sm:block">
               <UserButton afterSignOutUrl="/" appearance={{ elements: { userButtonAvatarBox: "w-10 h-10 shadow-sm" } }} />
            </div>
          </div>
        </header>

        {/* Dynamic Page Rendering */}
        <div className={`flex-1 overflow-x-hidden ${activePage === 'dashboard' ? 'p-0' : 'overflow-y-auto p-4 sm:p-8 lg:p-12'} scrollbar-none`}>
          <div className={`${activePage === 'dashboard' ? 'h-full w-full' : 'max-w-6xl mx-auto min-h-full pb-20'}`}>
            <AnimatePresence mode="wait">
              <motion.div
                key={activePage}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="h-full"
              >
                {renderContent()}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      <TelemetryPanel />

    </main>
  );
}
