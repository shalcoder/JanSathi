# Authentication Setup Guide

## Current Demo Authentication

The current sign-in and sign-up pages use **localStorage** for demo purposes. This allows you to test the authentication flow without setting up a real authentication provider.

### Demo Features:
- ✅ Email/Password sign-in and sign-up
- ✅ Google sign-in button (demo)
- ✅ Form validation
- ✅ Password strength requirements
- ✅ Beautiful, modern UI
- ✅ Mobile-responsive design

## Integrating Real Authentication

You can integrate any authentication provider. Here are the recommended options:

### Option 1: Clerk (Recommended)
Clerk provides ready-to-use authentication with minimal setup.

**Installation:**
```bash
npm install @clerk/nextjs
```

**Setup .env.local:**
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

**Update layout.tsx:**
```tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

**Replace demo sign-in/sign-up:**
- Use `<SignIn />` component from `@clerk/nextjs`
- Use `<SignUp />` component from `@clerk/nextjs`

### Option 2: NextAuth.js (Auth.js)
Free and open-source authentication solution.

**Installation:**
```bash
npm install next-auth
```

**Setup:**
1. Create `app/api/auth/[...nextauth]/route.ts`
2. Configure providers (Google, Email, etc.)
3. Add required environment variables

**Example Configuration:**
```typescript
import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"

export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
  ],
}

export default NextAuth(authOptions)
```

### Option 3: Firebase Authentication

**Installation:**
```bash
npm install firebase
```

**Setup:**
```typescript
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
```

### Option 4: Supabase Auth

**Installation:**
```bash
npm install @supabase/supabase-js
```

**Setup:**
```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)
```

## Modifying Current Pages

### Sign In Page (`app/sign-in/page.tsx`)

Replace the demo authentication code:

```typescript
// CURRENT (Demo)
const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    setTimeout(() => {
        localStorage.setItem('jansathi_user', JSON.stringify({...}));
        router.push('/dashboard');
    }, 1000);
};

// REPLACE WITH (Real Auth - Example with Clerk)
import { useSignIn } from '@clerk/nextjs';

const { signIn, setActive } = useSignIn();

const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
        const result = await signIn.create({
            identifier: email,
            password: password,
        });
        
        if (result.status === "complete") {
            await setActive({ session: result.createdSessionId });
            router.push('/dashboard');
        }
    } catch (err) {
        setError("Invalid credentials");
    } finally {
        setIsLoading(false);
    }
};
```

### Sign Up Page (`app/sign-up/page.tsx`)

Similar modifications for sign-up flow.

## Google OAuth Setup

### For Clerk:
1. Enable Google in Clerk Dashboard
2. Configure OAuth consent screen
3. No code changes needed - handled by Clerk

### For NextAuth:
1. Get Google OAuth credentials from Google Cloud Console
2. Add to environment variables:
   ```
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```
3. Configure in NextAuth options

### For Firebase:
1. Enable Google Sign-In in Firebase Console
2. Add Web SDK configuration
3. Use `signInWithPopup(auth, new GoogleAuthProvider())`

## Protected Routes

### Current Implementation:
Routes are currently open. Add middleware to protect them:

**Create `middleware.ts`:**
```typescript
import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  publicRoutes: ["/", "/sign-in", "/sign-up"],
});

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

## User Data

### Current (Demo):
```typescript
const user = { id: 'demo_user', firstName: 'JanSathi User' };
```

### With Real Auth (Clerk):
```typescript
import { useUser } from '@clerk/nextjs';

const { user } = useUser();
// Access user.firstName, user.email, etc.
```

## Next Steps

1. Choose an authentication provider
2. Install required packages
3. Set up environment variables
4. Replace demo code in sign-in/sign-up pages
5. Add authentication context/provider
6. Protect dashboard routes
7. Update user-dependent components

## Security Notes

- Never store sensitive user data in localStorage for production
- Always validate on the backend
- Use HTTPS in production
- Implement rate limiting
- Add CSRF protection
- Enable 2FA for enhanced security

## Demo Mode Toggle

To allow demo mode alongside real authentication:

```typescript
const isDemoMode = !process.env.NEXT_PUBLIC_AUTH_PROVIDER;

if (isDemoMode) {
    // Use localStorage demo auth
} else {
    // Use real authentication
}
```

## Questions?

Refer to the official documentation:
- Clerk: https://clerk.com/docs
- NextAuth: https://next-auth.js.org
- Firebase: https://firebase.google.com/docs/auth
- Supabase: https://supabase.com/docs/guides/auth
