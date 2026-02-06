'use client';

import React, { useState } from 'react';
import Sidebar from "@/components/layout/Sidebar";
import TelemetryPanel from "@/components/layout/TelemetryPanel";
import ChatInterface from "@/components/features/chat/ChatInterface";
import DocumentsPage from "@/components/features/dashboard/DocumentsPage";
import ProfilePage from "@/components/features/dashboard/ProfilePage";
import SettingsPage from "@/components/features/dashboard/SettingsPage";
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
    <main className="h-screen w-full flex bg-slate-950 aurora-bg text-white overflow-hidden relative selection:bg-blue-500/30">

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
              sessionStorage.removeItem('jansathi_chat');
              if (activePage === 'dashboard') {
                window.location.reload();
              }
            }}
          />
        </div>
      </div>

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col h-full relative z-10 transition-all duration-500 min-w-0">
        {/* Responsive Header */}
        <header className="px-4 py-4 flex items-center justify-between border-b border-white/5 bg-slate-900/50 backdrop-blur-md lg:px-8">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 -ml-2 hover:bg-white/5 rounded-lg lg:hidden"
            >
              <Menu className="w-6 h-6" />
            </button>
            <span className="font-black text-xl tracking-tighter text-blue-500 lg:hidden">JanSathi</span>
            <div className="hidden lg:flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></div>
              <span className="text-[10px] uppercase font-black tracking-widest text-slate-400">System Ready</span>
            </div>
          </div>

          <div className="flex items-center gap-2 lg:gap-4">
            <span className="text-[10px] lg:text-xs font-bold text-slate-500 uppercase tracking-widest capitalize">{activePage}</span>
            <div className="lg:hidden h-8 w-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 border border-white/10"></div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-10 scrollbar-none">
          <div className="max-w-6xl mx-auto h-full pb-20 lg:pb-0">
            {renderContent()}
          </div>
        </div>
      </div>

      {/* 3. Tech Telemetry Panel */}
      <TelemetryPanel />

    </main>
  );
}
