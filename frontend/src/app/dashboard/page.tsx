'use client';

import React, { useState } from 'react';
import Sidebar from "@/components/layout/Sidebar";
import TelemetryPanel from "@/components/layout/TelemetryPanel";
import ChatInterface from "@/components/features/chat/ChatInterface";
import DocumentsPage from "@/components/features/dashboard/DocumentsPage";
import ProfilePage from "@/components/features/dashboard/ProfilePage";
import SettingsPage from "@/components/features/dashboard/SettingsPage";

import BackendStatus from "@/components/BackendStatus";
import { Menu, X } from 'lucide-react';

export default function Home() {
  const [activePage, setActivePage] = useState('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const renderContent = () => {
    switch (activePage) {
      case 'dashboard':
        return <ChatInterface />;
      case 'documents':
        return <DocumentsPage />;

      case 'profile':
        return <ProfilePage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <main className="h-screen w-full flex bg-background aurora-bg text-foreground overflow-hidden relative selection:bg-blue-500/30 font-sans transition-colors duration-500">

      {/* Decorative Gradient Orbs */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[100px] -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-purple-500/20 rounded-full blur-[100px] translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

      {/* 1. Sidebar Navigation - Responsive Wrapper */}
      <div className={`
        fixed inset-0 z-50 lg:relative lg:inset-auto lg:flex
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        transition-transform duration-300 ease-in-out
      `}>
        <div className="absolute inset-0 bg-black/50 lg:hidden" onClick={() => setIsSidebarOpen(false)}></div>
        <div className="relative h-full w-64 lg:w-72 xl:w-80">
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
      <div className="flex-1 flex flex-col h-full relative z-10 transition-all duration-500 min-w-0 overflow-hidden">
        {/* Responsive Header */}
        <header className="px-6 py-5 flex items-center justify-between border-b border-white/5 bg-slate-900/80 backdrop-blur-xl lg:px-10 shrink-0 transition-all duration-500 z-20">
          <div className="flex items-center gap-5">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2.5 -ml-2 hover:bg-white/5 rounded-xl lg:hidden transition-all active:scale-95 shadow-sm"
            >
              <Menu className="w-6 h-6 text-white" />
            </button>
            <span className="font-black text-2xl tracking-tighter text-blue-500 lg:hidden transition-colors">JanSathi</span>
            <div className="hidden lg:flex items-center gap-3 px-4 py-2 rounded-2xl bg-white/5 border border-white/10 shadow-inner">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
              <span className="text-[10px] uppercase font-black tracking-[0.2em] text-slate-400 transition-colors">Core Intelligence Active</span>
            </div>
          </div>

          <div className="flex items-center gap-4 lg:gap-8">
            <div className="flex flex-col items-end hidden sm:flex">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-0.5">Application Context</span>
              <span className="text-xs font-black text-white uppercase tracking-widest transition-colors">{activePage}</span>
            </div>
            <div className="h-10 w-10 lg:h-12 lg:w-12 rounded-2xl bg-slate-800 border-2 border-blue-500/30 shadow-premium p-0.5 group cursor-pointer hover:scale-105 transition-all">
              <div className="w-full h-full rounded-[0.9rem] bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-black text-sm lg:text-base shadow-inner group-hover:rotate-3 transition-transform">
                JD
              </div>
            </div>
          </div>
        </header>

        <div className={`flex-1 overflow-x-hidden ${activePage === 'dashboard' ? 'overflow-hidden p-0' : 'overflow-y-auto p-4 sm:p-6 lg:p-10'} scrollbar-none scroll-smooth`}>
          <div className={`${activePage === 'dashboard' ? 'h-full w-full' : 'max-w-6xl mx-auto min-h-full pb-32 lg:pb-20'}`}>
            {renderContent()}
          </div>
        </div>
      </div>

      {/* 3. Tech Telemetry Panel - Desktop Only */}
      <TelemetryPanel />

      <BackendStatus />

    </main>
  );
}
