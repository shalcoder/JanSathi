export default function PrivacyPolicy() {
    return (
        <main className="min-h-screen bg-background text-foreground py-20 px-6 max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
            <p className="text-sm opacity-60 mb-12">Last Updated: February 14, 2026</p>

            <div className="space-y-12 leading-relaxed text-secondary-foreground">
                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">1. Data Collection</h2>
                    <p>We collect only the minimal data required to provide personalized scheme recommendations. This may include your occupation, income bracket, and location. We do not store any sensitive personal identifiers permanently.</p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">2. Voice Data</h2>
                    <p>Voice interactions are processed in real-time. Audio recordings are not stored unless you explicitly opt-in for accuracy improvement.</p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">3. Document Security</h2>
                    <p>Uploaded documents are processed temporarily in memory for OCR and then immediately discarded. No file contents are saved to our servers.</p>
                </section>

                <section>
                    <h2 className="text-xl font-bold mb-4 text-foreground">4. Third-Party Sharing</h2>
                    <p>We do not sell your data. We may share anonymized statistics with government partners to improve scheme reach.</p>
                </section>
            </div>
        </main>
    );
}
