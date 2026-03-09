'use client';

import ErrorBoundary from "@/components/ui/ErrorBoundary";
import OfflineNotice from "@/components/OfflineNotice";
import { I18nProvider } from "@/context/i18n";
import { ThemeProvider } from "@/context/theme";
import { configureAmplify } from "@/lib/cognito";

// Configure Amplify/Cognito once at app boot (client-side only)
configureAmplify();

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      <OfflineNotice />
      <ErrorBoundary>
        <ThemeProvider>
          <I18nProvider>
            {children}
          </I18nProvider>
        </ThemeProvider>
      </ErrorBoundary>
    </>
  );
}
