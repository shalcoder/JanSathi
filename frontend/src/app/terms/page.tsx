export default function TermsOfService() {
    return (
        <main className="min-h-screen bg-background text-foreground py-20 px-6 max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
            <p className="text-sm opacity-60 mb-12">Effective Date: February 14, 2026</p>

            <div className="space-y-12 leading-relaxed text-secondary-foreground">
                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">1. Acceptance of Terms</h2>
                    <p>By accessing JanSathi, you agree to be bound by these Terms. If you disagree, please do not use the service.</p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">2. Usage Rights</h2>
                    <p>JanSathi is free for personal, non-commercial use. Automated crawling or scraping of our data without permission is prohibited.</p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">3. Accuracy of Information</h2>
                    <p>While we strive for accuracy, government scheme details can change rapidly. We are not liable for any discrepancies. Always verify with official sources.</p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">4. Governing Law</h2>
                    <p>These terms are governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of the courts in New Delhi.</p>
                </section>
            </div>
        </main>
    );
}
