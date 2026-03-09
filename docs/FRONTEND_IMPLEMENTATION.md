# 🎨 JanSathi Frontend Implementation Details

## 📋 Overview

The JanSathi frontend is a modern **Next.js 16 + React 19** application built with TypeScript and TailwindCSS. It provides a **Progressive Web App (PWA)** experience with offline capabilities, voice interaction, and multi-language support for India's rural population.

---

## 🏗️ **Technology Stack**

### **Core Framework**
- **Next.js 16.1.6**: App Router, Server Components, Static Generation
- **React 19.2.3**: Latest React with Concurrent Features
- **TypeScript 5.x**: Strict type safety throughout the application
- **TailwindCSS 4.x**: Utility-first CSS framework with custom Indian design system

### **Key Dependencies (`package.json`)**
```json
{
  "dependencies": {
    "next": "16.1.6",
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "typescript": "~5.x",
    "@tailwindcss/typography": "^4.x",
    "framer-motion": "12.34.0",
    "lucide-react": "0.475.0",
    "aws-amplify": "6.16.2",
    "@aws-amplify/ui-react": "6.15.1",
    "axios": "^1.x",
    "next-pwa": "10.2.6",
    "workbox-webpack-plugin": "7.4.0"
  }
}
```

### **Development Tools**
- **ESLint 9.x**: Code quality and consistency
- **PostCSS 4.x**: CSS processing pipeline
- **Webpack 5.x**: Module bundling and optimization

---

## ⚙️ **Configuration Files**

### **1. `next.config.ts` - Next.js Configuration**
**Purpose**: Configures Next.js for PWA, static export, and API integration.

**Key Implementations**:
```typescript
const nextConfig: NextConfig = {
  // PWA Configuration
  pwa: {
    dest: 'public',
    sw: '/sw.js',
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\.jansathi\.com/,
        handler: 'StaleWhileRevalidate'
      }
    ]
  },
  
  // Static Export for S3 Deployment
  output: 'export',
  images: {
    unoptimized: true
  },
  
  // API Rewrites for Backend Integration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://api.jansathi.com/v1/:path*'
      }
    ]
  },
  
  // Internationalization
  i18n: {
    locales: ['hi', 'en', 'ta', 'te', 'kn', 'bn', 'gu', 'mr'],
    defaultLocale: 'hi'
  }
};
```

### **2. `tsconfig.json` - TypeScript Configuration**
**Purpose**: Strict TypeScript configuration for type safety.

**Key Settings**:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/services/*": ["./src/services/*"]
    }
  }
}
```

### **3. `postcss.config.mjs` - CSS Processing Pipeline**
**Purpose**: PostCSS configuration with TailwindCSS integration.

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    cssnano: process.env.NODE_ENV === 'production' ? {} : false
  }
}
```

### **4. `eslint.config.mjs` - Code Quality Configuration**
**Purpose**: ESLint rules for code consistency and accessibility.

---

## 🚀 **Application Structure (`/frontend/src/app`)**

### **Root Layout: `layout.tsx`**
**Purpose**: Root layout component with global providers and navigation.

**Key Implementations**:
```typescript
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="hi" className="scroll-smooth">
      <body className="min-h-screen bg-gradient-to-br from-orange-50 to-white">
        <Providers>
          <Header />
          <main className="min-h-screen pt-16">
            {children}
          </main>
          <Footer />
          <BackendStatus />
          <OfflineNotice />
        </Providers>
      </body>
    </html>
  )
}
```

**Global Providers**:
- **AmplifyProvider**: AWS authentication and API integration
- **ThemeProvider**: India-specific color palette and typography
- **LanguageProvider**: Multi-language context and switching
- **AudioProvider**: Voice interaction context management

### **Home Page: `page.tsx`**
**Purpose**: Landing page with hero section and feature showcase.

**Key Sections**:
1. **Hero Section**: Voice-first interaction demo with animated microphone
2. **Feature Cards**: Eligibility checking, grievance drafting, receipt generation
3. **Language Selector**: 10+ Indian languages with native script
4. **Statistics**: Live counters (queries processed, schemes supported, states covered)
5. **CTA Section**: "Start Speaking" button with voice permission request

**Implementation Highlights**:
```typescript
export default function HomePage() {
  const [isListening, setIsListening] = useState(false);
  const [supportedLanguages] = useState([
    { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
    // ... 7 more languages
  ]);

  return (
    <div className="space-y-16">
      <HeroSection onStartListening={handleVoiceStart} />
      <FeatureGrid features={CORE_FEATURES} />
      <LanguageGrid languages={supportedLanguages} />
      <StatsSection />
    </div>
  );
}
```

---

## 🗂️ **Core Application Pages**

### **1. Authentication Pages (`/auth`)**

#### **Sign In Page: `/auth/signin/page.tsx`**
**Purpose**: User authentication with AWS Cognito integration.

**Key Features**:
- **Phone-based authentication**: OTP verification for rural users
- **Aadhaar integration**: Optional Aadhaar linking for enhanced verification
- **Language preference**: Set during first sign-in
- **Accessibility**: Large buttons, high contrast for feature phone users

**Implementation**:
```typescript
export default function SignInPage() {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp'>('phone');

  const handlePhoneSubmit = async () => {
    await Auth.signIn(phone);
    setStep('otp');
  };

  const handleOtpVerify = async () => {
    await Auth.confirmSignIn(otp);
    router.push('/dashboard');
  };

  return (
    <AuthCard>
      {step === 'phone' ? (
        <PhoneInput onSubmit={handlePhoneSubmit} />
      ) : (
        <OtpInput onVerify={handleOtpVerify} />
      )}
    </AuthCard>
  );
}
```

#### **Sign Up Page: `/auth/signup/page.tsx`**
**Purpose**: New user registration with profile setup.

**Profile Collection**:
- Basic info: Name, phone, state, district
- Demographic info: Age, occupation, income bracket
- Preferences: Language, notification settings
- Consent: DPDP compliance checkboxes

### **2. Main Chat Interface: `/chat/page.tsx`**
**Purpose**: **Core interaction page** - voice and text chat with the AI agent.

**Key Components**:
1. **MessageList**: Chat history with message bubbles
2. **InputArea**: Text input with voice button
3. **VoiceRecorder**: Real-time audio recording with waveform
4. **AudioPlayer**: Playback of AI responses
5. **TypingIndicator**: Shows when AI is processing
6. **LanguageSwitcher**: Mid-conversation language switching

**Implementation Architecture**:
```typescript
export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const { startRecording, stopRecording, audioBlob } = useVoiceRecording();
  const { sendMessage, isLoading } = useApiClient();

  const handleVoiceMessage = async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    // Upload audio to backend
    const response = await sendMessage({
      type: 'voice',
      audio: audioBlob,
      language: currentLanguage
    });
    
    // Add messages to chat
    setMessages(prev => [...prev, 
      { type: 'user', content: response.transcript },
      { type: 'assistant', content: response.text, audio: response.audioUrl }
    ]);
    
    setIsProcessing(false);
  };

  return (
    <div className="h-screen flex flex-col">
      <MessageList messages={messages} />
      <InputArea 
        onTextMessage={handleTextMessage}
        onVoiceMessage={handleVoiceMessage}
        isProcessing={isProcessing}
      />
    </div>
  );
}
```

**Voice Recording Features**:
- **Real-time waveform**: Visual feedback during recording
- **Language detection**: Automatic language identification
- **Noise cancellation**: Basic audio preprocessing
- **Compression**: Optimized audio upload for mobile networks

### **3. User Dashboard: `/dashboard/page.tsx`**
**Purpose**: User dashboard with call history, applications, and receipts.

**Dashboard Sections**:
1. **Stats Overview**: Total queries, eligible schemes, pending applications
2. **Recent Conversations**: Last 10 interactions with summaries
3. **Application Status**: Tracking of submitted applications
4. **Document Library**: Uploaded documents and generated receipts
5. **Quick Actions**: Common tasks (check new scheme, update profile)

**Key Features**:
```typescript
export default function DashboardPage() {
  const { user } = useAuth();
  const { data: stats } = useUserStats();
  const { data: conversations } = useConversationHistory();
  const { data: applications } = useApplications();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <StatsPanel stats={stats} />
      <ConversationHistory conversations={conversations} />
      <ApplicationTracker applications={applications} />
      <DocumentLibrary userId={user.id} />
      <QuickActions />
    </div>
  );
}
```

### **4. Admin Dashboard: `/admin/page.tsx`**
**Purpose**: **HITL (Human-in-the-Loop) management** for administrators.

**Admin Features**:
1. **Live Calls Monitor**: Real-time active conversations
2. **HITL Queue**: Cases requiring human review
3. **Analytics Dashboard**: KPIs, trends, performance metrics
4. **User Management**: User profiles, support tickets
5. **System Health**: Backend status, error monitoring

**HITL Case Management**:
```typescript
export default function AdminDashboard() {
  const { data: hitlCases } = useHitlQueue();
  const { data: liveStats } = useLiveMetrics();
  const { approveCase, rejectCase } = useHitlActions();

  return (
    <AdminLayout>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard title="Active Calls" value={liveStats.activeCalls} />
        <MetricCard title="Pending HITL" value={hitlCases.length} />
        <MetricCard title="Success Rate" value={`${liveStats.successRate}%`} />
        <MetricCard title="Avg Latency" value={`${liveStats.avgLatency}ms`} />
      </div>
      
      <HitlQueue 
        cases={hitlCases} 
        onApprove={approveCase}
        onReject={rejectCase}
      />
      
      <LiveCallsMonitor calls={liveStats.activeCalls} />
    </AdminLayout>
  );
}
```

### **5. Additional Pages**

#### **Contact Page: `/contact/page.tsx`**
- **Support form**: Technical issues, feedback, feature requests
- **Regional offices**: Contact info for physical assistance
- **FAQ section**: Common questions and troubleshooting

#### **Onboarding: `/onboarding/page.tsx`** 
- **Multi-step wizard**: Profile setup, preferences, tutorial
- **Voice demo**: Practice voice interactions
- **Document upload**: Aadhaar, income certificate preparation

#### **Region Selection: `/region/page.tsx`**
- **Interactive map**: State and district selection
- **Regional info**: Local schemes and contact details
- **Language mapping**: Default language by region

---

## 🧩 **Component Architecture (`/frontend/src/components`)**

### **Feature Components (`/components/features`)**

#### **Chat Components (`/features/chat/`)**

**1. `ChatInterface.tsx`**
**Purpose**: Main chat container with state management.

```typescript
interface ChatInterfaceProps {
  initialMessages?: Message[];
  onMessageSent?: (message: Message) => void;
}

export function ChatInterface({ initialMessages = [], onMessageSent }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} isTyping={isTyping} />
      <InputArea onSendMessage={handleSendMessage} />
      <div ref={messagesEndRef} />
    </div>
  );
}
```

**2. `MessageList.tsx`**
**Purpose**: Chat message display with different message types.

**Message Types**:
- **Text messages**: User and assistant text responses
- **Voice messages**: Audio playback with transcripts
- **System messages**: Status updates, errors, confirmations
- **Receipt messages**: Eligibility results with download links
- **Document requests**: File upload prompts

**3. `VoiceRecorder.tsx`**
**Purpose**: Real-time voice recording with audio visualization.

```typescript
export function VoiceRecorder({ onRecordingComplete }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  const startRecording = async () => {  
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    
    // Audio level monitoring
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    
    // Visual feedback loop
    const updateAudioLevel = () => {
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(average / 255);
      requestAnimationFrame(updateAudioLevel);
    };
    
    updateAudioLevel();
    setIsRecording(true);
  };

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      className="relative p-4 rounded-full bg-gradient-to-r from-orange-500 to-red-500"
    >
      <Mic className={`w-6 h-6 ${isRecording ? 'animate-pulse' : ''}`} />
      {isRecording && <AudioWaveform level={audioLevel} />}
    </button>
  );
}
```

**4. `AudioPlayer.tsx`**
**Purpose**: Playback of AI-generated speech responses.

#### **Dashboard Components (`/features/dashboard/`)**

**1. `StatsPanel.tsx`**
**Purpose**: User statistics visualization.

```typescript
interface UserStats {
  totalQueries: number;
  eligibleSchemes: number;
  pendingApplications: number;
  successRate: number;
}

export function StatsPanel({ stats }: { stats: UserStats }) {
  return (
    <div className="grid grid-cols-2 gap-4 p-6 bg-white rounded-lg shadow">
      <StatCard 
        title="Total Queries" 
        value={stats.totalQueries} 
        icon={<MessageCircle />}
        trend="+12% this month"
      />
      <StatCard 
        title="Eligible Schemes" 
        value={stats.eligibleSchemes} 
        icon={<CheckCircle />}
        trend="3 new matches"
      />
      {/* Additional stat cards */}
    </div>
  );
}
```

**2. `ApplicationList.tsx`**
**Purpose**: Application status tracking with real-time updates.

**3. `ReceiptViewer.tsx`**
**Purpose**: Generated receipt display and download functionality.

#### **Community Components (`/features/community/`)**

**1. `CommunityFeed.tsx`**
**Purpose**: User-generated content and discussions.

**2. `PostCard.tsx`**  
**Purpose**: Individual post display with engagement features.

### **Authentication Components (`/components/auth/`)**

#### **`AuthGuard.tsx`**
**Purpose**: Route protection for authenticated pages.

```typescript
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/signin');
    }
  }, [user, isLoading]);

  if (isLoading) return <LoadingSpinner />;
  if (!user) return null;

  return <>{children}</>;
}
```

#### **`ProtectedRoute.tsx`**
**Purpose**: Role-based access control for admin features.

### **Layout Components (`/components/layout/`)**

#### **`Header.tsx`**
**Purpose**: Main navigation header with responsive design.

```typescript
export function Header() {
  const { user } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 w-full bg-white/95 backdrop-blur-md border-b z-50">
      <nav className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Logo />
        
        <div className="hidden md:flex items-center space-x-6">
          <NavLinks />
          <LanguageSwitcher />
          {user ? <UserMenu /> : <AuthButtons />}
        </div>
        
        <MobileMenuButton onClick={() => setMobileMenuOpen(!mobileMenuOpen)} />
      </nav>
      
      <MobileNav isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />
    </header>
  );
}
```

#### **`Footer.tsx`**
**Purpose**: Site footer with links and compliance information.

### **UI Components (`/components/ui/`)**

**Reusable component library**:
- **`Button.tsx`**: Consistent button styles and variants
- **`Input.tsx`**: Form inputs with validation states  
- **`Modal.tsx`**: Overlay modals with backdrop handling
- **`Dropdown.tsx`**: Select dropdowns with search
- **`Spinner.tsx`**: Loading indicators
- **`Tooltip.tsx`**: Contextual help tooltips

### **Status Components**

#### **`BackendStatus.tsx`**
**Purpose**: Real-time backend health monitoring.

```typescript
export function BackendStatus() {
  const [status, setStatus] = useState<'online' | 'offline' | 'degraded'>('online');
  const [latency, setLatency] = useState<number>(0);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const startTime = Date.now();
        await fetch('/api/health');
        const endTime = Date.now();
        
        setLatency(endTime - startTime);
        setStatus('online');
      } catch (error) {
        setStatus('offline');
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30s
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed bottom-4 right-4 p-2 rounded-lg bg-white shadow-lg">
      <div className="flex items-center space-x-2">
        <StatusIndicator status={status} />
        <span className="text-sm">
          {status === 'online' ? `${latency}ms` : 'Offline'}
        </span>
      </div>
    </div>
  );
}
```

#### **`OfflineNotice.tsx`**  
**Purpose**: Offline mode notification and request queueing.

---

## 🔧 **Services & API Integration (`/frontend/src/services`)**

### **1. `api.ts` - Main API Client**
**Purpose**: Centralized Axios client for all backend communications.

```typescript
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Redirect to login
          window.location.href = '/auth/signin';
        }
        return Promise.reject(error);
      }
    );
  }

  // Core API methods
  async initSession(language: string = 'hi') {
    return this.client.post('/v1/sessions/init', { language });
  }

  async sendQuery(sessionId: string, query: string, type: 'text' | 'voice') {
    return this.client.post('/v1/query', {
      session_id: sessionId,
      query,
      type
    });
  }

  async uploadAudio(audioBlob: Blob, sessionId: string) {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('session_id', sessionId);
    
    return this.client.post('/v1/audio/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  async submitApplication(applicationData: any) {
    return this.client.post('/v1/apply', applicationData);
  }

  async getApplicationStatus(applicationId: string) {
    return this.client.get(`/v1/applications/${applicationId}`);
  }

  async getAdminHitlCases() {
    return this.client.get('/v1/admin/cases');
  }

  async approveHitlCase(caseId: string, notes: string) {
    return this.client.post(`/v1/admin/cases/${caseId}/approve`, { notes });
  }
}

export const apiClient = new ApiClient();
```

### **2. `localAudit.ts` - Client-Side Audit Logging**
**Purpose**: PWA-compatible audit logging with offline capabilities.

```typescript
class LocalAuditService {
  private dbName = 'jansathi_audit';
  private version = 1;
  private db: IDBDatabase | null = null;

  async init() {
    return new Promise<void>((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // Create audit log store
        if (!db.objectStoreNames.contains('audit_logs')) {
          const store = db.createObjectStore('audit_logs', { 
            keyPath: 'id', 
            autoIncrement: true 
          });
          store.createIndex('timestamp', 'timestamp');
          store.createIndex('action', 'action');
        }
      };
    });
  }

  async logAction(action: string, details: any) {
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      details,
      userId: localStorage.getItem('user_id'),
      sessionId: localStorage.getItem('session_id'),
      userAgent: navigator.userAgent,
      offline: !navigator.onLine
    };

    // Store locally
    await this.storeLocally(entry);
    
    // Attempt to sync if online
    if (navigator.onLine) {
      await this.syncToServer(entry);
    }
  }

  private async storeLocally(entry: any) {
    if (!this.db) return;
    
    const transaction = this.db.transaction(['audit_logs'], 'readwrite');
    const store = transaction.objectStore('audit_logs');
    store.add(entry);
  }

  private async syncToServer(entry: any) {
    try {
      await apiClient.post('/v1/audit', entry);
    } catch (error) {
      console.warn('Failed to sync audit log to server:', error);
    }
  }
}

export const localAudit = new LocalAuditService();
```

### **3. `offlineQueue.ts` - Offline Request Management**
**Purpose**: Queue and sync requests when device comes back online.

```typescript
class OfflineQueueService {
  private queue: QueuedRequest[] = [];
  private isProcessing = false;

  constructor() {
    // Load persisted queue
    this.loadQueue();
    
    // Listen for online events
    window.addEventListener('online', () => this.processQueue());
  }

  async addToQueue(request: QueuedRequest) {
    this.queue.push({
      ...request,
      id: Date.now().toString(),
      timestamp: Date.now()
    });
    
    await this.persistQueue();
    
    // Try to process if online
    if (navigator.onLine && !this.isProcessing) {
      await this.processQueue();
    }
  }

  private async processQueue() {
    if (this.isProcessing || this.queue.length === 0) return;
    
    this.isProcessing = true;
    
    while (this.queue.length > 0 && navigator.onLine) {
      const request = this.queue.shift()!;
      
      try {
        await this.executeRequest(request);
        await this.persistQueue();
      } catch (error) {
        // Put back at front if failed
        this.queue.unshift(request);
        break;
      }
    }
    
    this.isProcessing = false;
  }
}

export const offlineQueue = new OfflineQueueService();
```

---

## 📱 **PWA Implementation**

### **Service Worker (`public/sw.js`)**
**Generated by next-pwa with custom caching strategies**:

- **API responses**: StaleWhileRevalidate for dynamic content
- **Static assets**: CacheFirst for images, fonts
- **Audio files**: NetworkFirst for voice responses
- **Offline fallback**: Custom offline page

### **Offline Capabilities**
- **Request queueing**: API calls queued when offline
- **Local storage**: Critical data cached in IndexedDB
- **Offline UI**: Clear indicators when offline
- **Sync on reconnect**: Automatic sync when back online

---

## 🌐 **Internationalization (`/frontend/src/lib`)**

### **Language Configuration (`languages.ts`)**
**Purpose**: Multi-language support for 10+ Indian languages.

```typescript
export const SUPPORTED_LANGUAGES = [
  { 
    code: 'hi', 
    name: 'हिन्दी', 
    nativeName: 'Hindi',
    flag: '🇮🇳',
    rtl: false,
    voice: 'Aditi'
  },
  { 
    code: 'en', 
    name: 'English', 
    nativeName: 'English',
    flag: '🇬🇧', 
    rtl: false,
    voice: 'Raveena'
  },
  { 
    code: 'ta', 
    name: 'தமிழ்', 
    nativeName: 'Tamil',
    flag: '🇮🇳', 
    rtl: false,
    voice: 'coming-soon'
  }
  // ... additional languages
];

export const TRANSLATIONS = {
  hi: {
    'welcome': 'स्वागत है',
    'start_speaking': 'बोलना शुरू करें',
    'check_eligibility': 'पात्रता जांचें'
  },
  en: {
    'welcome': 'Welcome',
    'start_speaking': 'Start Speaking',
    'check_eligibility': 'Check Eligibility'
  }
};
```

---

## 🔐 **Authentication & Security (`/frontend/src/lib`)**

### **AWS Cognito Integration (`cognito.ts`)**
**Purpose**: Authentication with AWS Cognito User Pools.

```typescript
Amplify.configure({
  Auth: {
    region: 'us-east-1',
    userPoolId: process.env.NEXT_PUBLIC_USER_POOL_ID,
    userPoolWebClientId: process.env.NEXT_PUBLIC_USER_POOL_CLIENT_ID,
    signUpVerificationMethod: 'phone_number',
    loginWith: {
      phone: true
    }
  }
});

export class AuthService {
  async signInWithPhone(phoneNumber: string) {
    return Auth.signIn(phoneNumber);
  }

  async verifyOTP(phoneNumber: string, code: string) {
    return Auth.confirmSignIn(phoneNumber, code);
  }

  async getCurrentUser() {
    try {
      return await Auth.currentAuthenticatedUser();
    } catch {
      return null;
    }
  }

  async signOut() {
    return Auth.signOut();
  }
}
```

---

## 🚀 **Deployment Configuration**

### **Vercel Deployment (`vercel.json`)**
```json
{
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "@api-url",
      "NEXT_PUBLIC_USER_POOL_ID": "@user-pool-id"
    }
  },
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "redirects": [
    {
      "source": "/api/:path*",
      "destination": "https://api.jansathi.com/v1/:path*",
      "permanent": false
    }
  ]
}
```

### **Docker Configuration (`Dockerfile`)**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source + build
COPY . .
RUN npm run build

# Serve with minimal server
EXPOSE 3000
CMD ["npm", "start"]
```

### **Deployment Scripts**

#### **`deploy_frontend.py`**
**Purpose**: Automated deployment to S3 + CloudFront.

```python
def deploy_frontend():
    # 1. Build Next.js app
    subprocess.run(['npm', 'run', 'build'], cwd='frontend')
    
    # 2. Upload to S3
    s3_sync_command = [
        'aws', 's3', 'sync', 
        'frontend/out/', 
        f's3://{BUCKET_NAME}/', 
        '--delete'
    ]
    subprocess.run(s3_sync_command)
    
    # 3. Invalidate CloudFront
    cloudfront.create_invalidation(
        DistributionId=DISTRIBUTION_ID,
        InvalidationBatch={'Paths': ['/*']}
    )
```

---

## 📊 **Performance Optimizations**

### **Image Optimization**
- **Next.js Image component**: Automatic WebP conversion, lazy loading
- **Responsive images**: Multiple breakpoints for mobile-first design
- **CDN delivery**: CloudFront caching for static assets

### **Code Splitting**
- **Dynamic imports**: Route-based code splitting
- **Component-level splitting**: Heavy components loaded on demand
- **Third-party libraries**: Bundled separately for better caching

### **Caching Strategies**
- **API responses**: React Query with stale-while-revalidate
- **Static content**: Long-term caching with cache busting
- **Service worker**: Custom caching rules for different content types

---

## 🧪 **Testing & Quality Assurance**

### **Testing Tools**  
- **Jest**: Unit testing for components and utilities
- **React Testing Library**: Component integration tests
- **Cypress**: End-to-end testing for critical flows  
- **Lighthouse**: Performance and accessibility auditing

### **Quality Tools**
- **TypeScript**: Compile-time type checking
- **ESLint**: Code quality and consistency
- **Prettier**: Code formatting
- **Husky**: Pre-commit hooks for quality gates

---

This comprehensive frontend implementation provides a modern, accessible, and performant web application that serves as the primary interface for India's first voice-first agentic civic automation system. The PWA architecture ensures reliability even in areas with poor internet connectivity, while the multi-language support makes government services accessible to India's diverse population.