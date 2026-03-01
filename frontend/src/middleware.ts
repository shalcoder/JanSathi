import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher(["/dashboard(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  // Protect all routes under /dashboard
  if (isProtectedRoute(req)) {
    await auth.protect();

    // In a real app, you would check a custom claim or a secure cookie here.
    // Given the Next.js edge runtime limitations with external API calls in middleware,
    // we let the client side handle the exact "profile_complete" check.
    // However, if we strongly know they haven't via a cookie we set after login:
    const hasCompletedOnboarding = req.cookies.get('jansathi_profile_complete')?.value === 'true';
    if (!hasCompletedOnboarding && req.nextUrl.pathname !== '/onboarding') {
       // We skip hard-redirecting here in Edge to avoid looping if cookie isn't set yet.
       // The actual client-side fetch in Dashboard will handle kicking them to /onboarding.
    }
  }
});

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
};
