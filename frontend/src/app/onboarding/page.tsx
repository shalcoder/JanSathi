'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useAuth, getToken } from '@/hooks/useAuth';
import {
    User, MapPin, Briefcase, FileText, CheckCircle2,
    Languages, ArrowRight, ArrowLeft, AlertCircle, ChevronDown,
} from 'lucide-react';
import { buildClient } from '@/services/api';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';

// ─── Shared input / label styles (works in both light and dark mode) ──────────
const INPUT_CLS =
    'w-full bg-white dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 ' +
    'text-slate-900 dark:text-zinc-100 rounded-xl px-4 py-3 ' +
    'placeholder:text-slate-400 dark:placeholder:text-zinc-500 ' +
    'focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all';

const SELECT_CLS =
    'w-full bg-white dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 ' +
    'text-slate-900 dark:text-zinc-100 rounded-xl px-4 py-3 ' +
    'focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 ' +
    'transition-all appearance-none cursor-pointer';

const LABEL_CLS =
    'block text-xs font-bold text-slate-500 dark:text-zinc-400 ' +
    'uppercase tracking-wider mb-1.5';

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
  'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
  'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
  'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu & Kashmir', 'Ladakh', 'Puducherry',
];

const STEPS = [
  { id: 'personal',      title: 'Personal',      icon: User },
  { id: 'location',      title: 'Location',      icon: MapPin },
  { id: 'socioeconomic', title: 'Socioeconomic', icon: Briefcase },
  { id: 'documents',     title: 'Documents',     icon: FileText },
  { id: 'language',      title: 'Language',      icon: Languages },
];

// Wrap a <select> with a ChevronDown overlay
function SelectWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative">
      {children}
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-zinc-500" />
    </div>
  );
}

export default function OnboardingWizard() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    age: '',
    gender: 'Male',
    state: '',
    district: '',
    village: '',
    pincode: '',
    occupation: 'Farmer',
    category: 'General',
    annual_income: '',
    land_holding_acres: '',
    has_aadhaar: false,
    has_ration_card: false,
    has_bank_account: false,
    has_pm_kisan: false,
    preferred_language: 'hi',
  });

  useEffect(() => {
    if (authLoading) return;
    if (!user) { router.push('/auth/signin'); return; }
    setFormData(prev => ({ ...prev, full_name: user.name || '' }));
  }, [authLoading, user, router]);

  const handleChange = (field: string, value: string | boolean) =>
    setFormData(prev => ({ ...prev, [field]: value }));

  const handleNext = () => { if (currentStep < STEPS.length - 1) setCurrentStep(p => p + 1); };
  const handleBack = () => { if (currentStep > 0) setCurrentStep(p => p - 1); };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const token = await getToken();
      if (!token) {
        setError('Your session has expired. Please sign in again.');
        router.push('/auth/signin');
        return;
      }
      const client = buildClient(token);
      await client.put('/v1/profile', { ...formData, profile_complete: true });
      router.push('/dashboard');
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 409) setError('This phone number is already registered to another account.');
      else if (status === 401) setError('Session expired. Please sign in again.');
      else if (status && status >= 500) setError('Server error. Please try again in a moment.');
      else setError('Failed to save your profile. Check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show skeleton while Cognito resolves
  if (authLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-full max-w-2xl space-y-4 p-8">
          <div className="h-8 bg-slate-200 dark:bg-zinc-700 rounded-xl animate-pulse w-1/2 mx-auto" />
          <div className="h-64 bg-slate-200 dark:bg-zinc-700 rounded-2xl animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-background flex flex-col items-center justify-center p-4">
      {/* Background blobs */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 h-[500px] w-[500px] rounded-full bg-primary/10 blur-[120px]" />
        <div className="absolute bottom-0 left-0 h-[400px] w-[400px] rounded-full bg-blue-500/10 blur-[100px]" />
      </div>

      <div className="w-full max-w-2xl relative z-10">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-orange-600 shadow-lg mb-6">
            <span className="font-bold text-2xl text-white">JS</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-foreground mb-2">Welcome to JanSathi</h1>
          <p className="text-slate-500 dark:text-zinc-400">Let&apos;s set up your profile to match you with the right schemes.</p>
        </div>

        {/* Step tracker */}
        <div className="flex items-center justify-between mb-8 px-2">
          {STEPS.map((step, index) => {
            const isActive    = index === currentStep;
            const isCompleted = index < currentStep;
            return (
              <div key={step.id} className="flex flex-col items-center relative z-10 w-1/5">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isActive    ? 'bg-primary text-white shadow-lg shadow-primary/30 ring-4 ring-primary/20' :
                  isCompleted ? 'bg-emerald-500 text-white' :
                                'bg-slate-200 dark:bg-zinc-700 text-slate-400 dark:text-zinc-500'
                }`}>
                  {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : <step.icon className="w-5 h-5" />}
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-widest mt-3 hidden sm:block ${
                  isActive    ? 'text-primary' :
                  isCompleted ? 'text-emerald-500' :
                                'text-slate-400 dark:text-zinc-500'
                }`}>{step.title}</span>
                {index < STEPS.length - 1 && (
                  <div className={`absolute top-5 left-[60%] w-[80%] h-0.5 -z-10 ${
                    isCompleted ? 'bg-emerald-500' : 'bg-slate-200 dark:bg-zinc-700'
                  }`} />
                )}
              </div>
            );
          })}
        </div>

        {/* Card */}
        <div className="bg-white dark:bg-card border border-slate-200 dark:border-border/50 rounded-[2rem] shadow-xl p-8 sm:p-12 mb-8">

          {/* Error banner */}
          {error && (
            <div className="mb-6 flex items-start gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400 text-sm font-medium">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -20, opacity: 0 }}
              transition={{ duration: 0.25 }}
            >

              {/* ── STEP 1: Personal ──────────────────────────────────────── */}
              {currentStep === 0 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-foreground">Basic Information</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label className={LABEL_CLS}>Full Name</label>
                      <input type="text" value={formData.full_name}
                        onChange={e => handleChange('full_name', e.target.value)}
                        placeholder="e.g. Ramesh Kumar" className={INPUT_CLS} />
                    </div>
                    <div>
                      <label className={LABEL_CLS}>Mobile Number</label>
                      <input type="tel" value={formData.phone}
                        onChange={e => handleChange('phone', e.target.value)}
                        placeholder="+91 98765 43210" className={INPUT_CLS} />
                    </div>
                    <div>
                      <label className={LABEL_CLS}>Age</label>
                      <input type="number" value={formData.age}
                        onChange={e => handleChange('age', e.target.value)}
                        placeholder="Years" className={INPUT_CLS} />
                    </div>
                    <div>
                      <label className={LABEL_CLS}>Gender</label>
                      <SelectWrapper>
                        <select title="Gender" value={formData.gender}
                          onChange={e => handleChange('gender', e.target.value)}
                          className={SELECT_CLS}>
                          <option value="Male">Male</option>
                          <option value="Female">Female</option>
                          <option value="Other">Other</option>
                        </select>
                      </SelectWrapper>
                    </div>
                  </div>
                </div>
              )}

              {/* ── STEP 2: Location ──────────────────────────────────────── */}
              {currentStep === 1 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-foreground">Where are you from?</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label className={LABEL_CLS}>State</label>
                      <SelectWrapper>
                        <select title="State" value={formData.state}
                          onChange={e => handleChange('state', e.target.value)}
                          className={SELECT_CLS}>
                          <option value="">Select State</option>
                          {INDIAN_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                      </SelectWrapper>
                    </div>
                    <div>
                      <label className={LABEL_CLS}>District</label>
                      <input type="text" value={formData.district}
                        onChange={e => handleChange('district', e.target.value)}
                        placeholder="District" className={INPUT_CLS} />
                    </div>
                    <div>
                      <label className={LABEL_CLS}>Village / Town</label>
                      <input type="text" value={formData.village}
                        onChange={e => handleChange('village', e.target.value)}
                        placeholder="Village / Town" className={INPUT_CLS} />
                    </div>
                    <div>
                      <label className={LABEL_CLS}>Pincode</label>
                      <input type="text" value={formData.pincode}
                        onChange={e => handleChange('pincode', e.target.value)}
                        placeholder="6-digit pincode" className={INPUT_CLS} />
                    </div>
                  </div>
                </div>
              )}

              {/* ── STEP 3: Socioeconomic ─────────────────────────────────── */}
              {currentStep === 2 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-foreground">Socioeconomic Profile</h2>
                    <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1">Helps us match you with highly targeted government schemes.</p>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label className={LABEL_CLS}>Occupation</label>
                      <SelectWrapper>
                        <select title="Occupation" value={formData.occupation}
                          onChange={e => handleChange('occupation', e.target.value)}
                          className={SELECT_CLS}>
                          <option value="Farmer">Farmer</option>
                          <option value="Agricultural Laborer">Agricultural Laborer</option>
                          <option value="Daily Wage Worker">Daily Wage Worker</option>
                          <option value="Artisan">Artisan / Weaver</option>
                          <option value="Student">Student</option>
                          <option value="Other">Other</option>
                        </select>
                      </SelectWrapper>
                    </div>
                    <div>
                      <label className={LABEL_CLS}>Caste Category</label>
                      <SelectWrapper>
                        <select title="Caste Category" value={formData.category}
                          onChange={e => handleChange('category', e.target.value)}
                          className={SELECT_CLS}>
                          <option value="General">General</option>
                          <option value="EWS">EWS</option>
                          <option value="OBC">OBC</option>
                          <option value="SC">SC</option>
                          <option value="ST">ST</option>
                        </select>
                      </SelectWrapper>
                    </div>
                    <div>
                      <label className={LABEL_CLS}>Annual Income (₹)</label>
                      <input type="number" value={formData.annual_income}
                        onChange={e => handleChange('annual_income', e.target.value)}
                        placeholder="e.g. 150000" className={INPUT_CLS} />
                    </div>
                    {formData.occupation === 'Farmer' && (
                      <div>
                        <label className={LABEL_CLS}>Land Holding (Acres)</label>
                        <input type="number" step="0.1" value={formData.land_holding_acres}
                          onChange={e => handleChange('land_holding_acres', e.target.value)}
                          placeholder="e.g. 2.5"
                          className="w-full bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-300 dark:border-emerald-500/30 text-emerald-800 dark:text-emerald-400 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all font-medium placeholder:text-emerald-400 dark:placeholder:text-emerald-600" />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ── STEP 4: Documents ─────────────────────────────────────── */}
              {currentStep === 3 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-foreground">Which documents do you have?</h2>
                    <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1">We don&apos;t need the actual files — just select what you possess.</p>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {([
                      { id: 'has_aadhaar',      label: 'Aadhaar Card' },
                      { id: 'has_ration_card',  label: 'Ration Card' },
                      { id: 'has_bank_account', label: 'Active Bank Account' },
                      { id: 'has_pm_kisan',     label: 'PM-KISAN Beneficiary' },
                    ] as { id: keyof typeof formData; label: string }[]).map(doc => (
                      <div
                        key={doc.id}
                        onClick={() => handleChange(doc.id, !formData[doc.id])}
                        className={`p-4 rounded-xl border-2 flex items-center gap-4 cursor-pointer select-none transition-all ${
                          formData[doc.id]
                            ? 'bg-primary/5 dark:bg-primary/10 border-primary shadow-primary/10 shadow-md'
                            : 'bg-white dark:bg-zinc-800 border-slate-200 dark:border-zinc-700 hover:border-primary/40'
                        }`}
                      >
                        <div className={`w-6 h-6 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-colors ${
                          formData[doc.id] ? 'border-primary bg-primary' : 'border-slate-300 dark:border-zinc-600'
                        }`}>
                          {formData[doc.id] && <CheckCircle2 className="w-4 h-4 text-white" />}
                        </div>
                        <span className={`font-semibold text-sm ${formData[doc.id] ? 'text-primary' : 'text-slate-700 dark:text-zinc-200'}`}>
                          {doc.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── STEP 5: Language ──────────────────────────────────────── */}
              {currentStep === 4 && (
                <div className="space-y-6">
                  <div className="text-center mb-6">
                    <div className="w-20 h-20 bg-blue-100 dark:bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Languages className="w-10 h-10 text-blue-500" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-foreground mb-1">Platform Language</h2>
                    <p className="text-sm text-slate-500 dark:text-zinc-400 max-w-sm mx-auto">
                      Your preferred language for voice calls (IVR), SMS, and the dashboard.
                    </p>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-w-lg mx-auto">
                    {SUPPORTED_LANGUAGES.map(lang => (
                      <div
                        key={lang.code}
                        onClick={() => handleChange('preferred_language', lang.code)}
                        className={`p-4 rounded-xl border-2 text-center cursor-pointer select-none transition-all ${
                          formData.preferred_language === lang.code
                            ? 'bg-blue-50 dark:bg-blue-500/10 border-blue-500 shadow-blue-500/10 shadow-md'
                            : 'bg-white dark:bg-zinc-800 border-slate-200 dark:border-zinc-700 hover:border-blue-400/50'
                        }`}
                      >
                        <p className={`font-bold text-lg mb-0.5 ${formData.preferred_language === lang.code ? 'text-blue-600 dark:text-blue-400' : 'text-slate-800 dark:text-zinc-100'}`}>
                          {lang.native}
                        </p>
                        <p className="text-[10px] text-slate-400 dark:text-zinc-500 uppercase tracking-wider">{lang.name}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-10 pt-6 border-t border-slate-100 dark:border-border/50">
            <button
              onClick={handleBack}
              disabled={currentStep === 0 || isSubmitting}
              className={`px-6 py-3 rounded-xl font-bold text-sm flex items-center gap-2 transition-all ${
                currentStep === 0
                  ? 'invisible'
                  : 'bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 hover:bg-slate-200 dark:hover:bg-zinc-700'
              }`}
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>

            {currentStep < STEPS.length - 1 ? (
              <button
                onClick={handleNext}
                className="px-8 py-3 bg-primary text-white rounded-xl font-bold text-sm shadow-lg shadow-primary/20 hover:shadow-primary/40 hover:-translate-y-0.5 flex items-center gap-2 transition-all"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className={`px-8 py-3 bg-emerald-500 text-white rounded-xl font-bold text-sm shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition-all ${
                  isSubmitting ? 'opacity-70 cursor-not-allowed' : 'hover:shadow-emerald-500/40 hover:-translate-y-0.5'
                }`}
              >
                {isSubmitting ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                    Saving…
                  </>
                ) : (
                  <>Complete Setup <CheckCircle2 className="w-4 h-4" /></>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

