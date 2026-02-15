import { AuthenticateWithRedirectCallback } from "@clerk/nextjs";

export default function SSOCallback() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-background">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                <p className="text-secondary-foreground font-bold animate-pulse">Completing secure sign in...</p>
                <AuthenticateWithRedirectCallback />
            </div>
        </div>
    );
}
