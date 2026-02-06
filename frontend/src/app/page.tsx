import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center p-4 sm:p-8 bg-gradient-to-br from-slate-50 to-slate-200 dark:from-slate-950 dark:to-slate-900">

      {/* Header */}
      <header className="w-full max-w-2xl mb-8 flex flex-col items-center">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-teal-500 mb-2">
          JanSathi
        </h1>
        <p className="text-slate-600 dark:text-slate-400 font-medium">
          Making Government Services Simple for Everyone
        </p>
      </header>

      {/* Main Chat Interface */}
      <section className="w-full h-[70vh] flex-1 min-h-[500px] mb-8">
        <ChatInterface />
      </section>

      {/* Footer */}
      <footer className="w-full max-w-2xl text-center text-xs text-slate-400">
        <p>AI For Bharat Hackathon • JanSathi 2026</p>
      </footer>
    </main>
  );
}
