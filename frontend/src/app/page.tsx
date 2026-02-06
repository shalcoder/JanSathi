import { ArrowRight, Mic, ShieldCheck, Languages, MessageCircle, FileText, CheckCircle } from "lucide-react";
import Link from 'next/link';
import BackendStatus from "@/components/BackendStatus";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50 scroll-smooth">

      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center text-center px-4 pt-20 pb-16 sm:pt-32 sm:pb-20 max-w-5xl mx-auto space-y-8 z-0">
        {/* Background Gradients */}
        <div className="absolute top-0 -z-10 h-full w-full bg-white dark:bg-slate-950 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] dark:bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.15),rgba(255,255,255,0))]"></div>

        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <h1 className="text-6xl sm:text-8xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-teal-500 pb-2">
            JanSathi
          </h1>
          <div className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-800 dark:border-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
            <span>🚀 Hackathon Ready</span>
          </div>

          <h2 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
            Bridging the Gap to Public Services
          </h2>

          {/* Strengthened Context */}
          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed font-medium">
            Built for India’s government schemes, certificates, and public services.
          </p>
          <p className="text-base text-slate-500 dark:text-slate-500 max-w-xl mx-auto">
            Your voice-first AI companion. Simple, accessible, and human.
          </p>
        </div>

        {/* Improved CTA */}
        <div className="pt-4 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
          <Link
            href="/chat"
            className="group flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-bold text-lg transition-all transform hover:scale-105 shadow-lg shadow-blue-600/20"
          >
            Start Chat <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Accessibility Signals */}
        <div className="flex gap-4 text-xs sm:text-sm text-slate-400 font-medium pt-4">
          <span className="flex items-center gap-1">🎙️ Voice-first</span>
          <span>•</span>
          <span className="flex items-center gap-1">🗣️ Simple language</span>
          <span>•</span>
          <span className="flex items-center gap-1">⚡ Low-bandwidth friendly</span>
        </div>
      </section>

      {/* "How it works" Micro-section */}
      <section className="py-12 bg-slate-50 dark:bg-slate-900/30 border-y border-slate-200 dark:border-slate-800">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-center items-center gap-8 md:gap-16 text-center">
            <div className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xl">1</div>
              <span className="font-semibold text-slate-700 dark:text-slate-300">Ask in your language</span>
            </div>
            <div className="hidden md:block w-16 h-0.5 bg-slate-200 dark:bg-slate-700"></div>
            <div className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xl">2</div>
              <span className="font-semibold text-slate-700 dark:text-slate-300">AI Understands & Search</span>
            </div>
            <div className="hidden md:block w-16 h-0.5 bg-slate-200 dark:bg-slate-700"></div>
            <div className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-xl">3</div>
              <span className="font-semibold text-slate-700 dark:text-slate-300">Get Clear Guidance</span>
            </div>
          </div>
        </div>
      </section>

      {/* "What can I ask?" Section */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto space-y-8">
          <h3 className="text-2xl sm:text-3xl font-bold text-center">What can I ask?</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <ExampleCard text="How to apply for income certificate?" />
            <ExampleCard text="Am I eligible for government scholarships?" />
            <ExampleCard text="Free health schemes for senior citizens" />
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="py-20 px-4 bg-white dark:bg-slate-900/50 border-t border-slate-100 dark:border-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Mic className="w-8 h-8 text-blue-500" />}
              title="Voice First"
              description="Speak naturally in your language. No need to type or navigate complex menus."
            />
            <FeatureCard
              icon={<Languages className="w-8 h-8 text-teal-500" />}
              title="Multilingual Support"
              description="Breaking language barriers to make governance accessible to every citizen."
            />
            <FeatureCard
              icon={<ShieldCheck className="w-8 h-8 text-purple-500" />}
              title="Trusted Info"
              description="Accurate information sourced directly from official government guidelines."
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-slate-500 text-sm border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-950">
        <p>© 2026 JanSathi • AI For Bharat Hackathon</p>
      </footer>

      <BackendStatus />
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-8 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 hover:border-blue-200 dark:hover:border-blue-800 transition-all hover:shadow-lg">
      <div className="mb-4 inline-block p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700">
        {icon}
      </div>
      <h4 className="text-xl font-bold mb-3">{title}</h4>
      <p className="text-slate-600 dark:text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}

function ExampleCard({ text }: { text: string }) {
  return (
    <div className="p-6 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col items-center justify-center gap-3">
      <div className="bg-blue-50 dark:bg-blue-900/20 p-2 rounded-full text-blue-600 dark:text-blue-400">
        <MessageCircle className="w-5 h-5" />
      </div>
      <p className="font-medium text-slate-800 dark:text-slate-200">"{text}"</p>
    </div>
  )
}

