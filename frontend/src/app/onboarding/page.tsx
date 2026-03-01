'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import { User, MapPin, Briefcase, FileText, CheckCircle2, Languages, ArrowRight, ArrowLeft } from 'lucide-react';
import { buildClient } from '@/services/api';

const STEPS = [
  { id: 'personal', title: 'Personal Details', icon: User },
  { id: 'location', title: 'Location', icon: MapPin },
  { id: 'socioeconomic', title: 'Socioeconomic', icon: Briefcase },
  { id: 'documents', title: 'Documents', icon: FileText },
  { id: 'language', title: 'Language', icon: Languages },
];

export default function OnboardingWizard() {
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
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

  // Pre-fill from Clerk if available
  useEffect(() => {
    if (isLoaded && user) {
      setFormData(prev => ({
        ...prev,
        full_name: `${user.firstName || ''} ${user.lastName || ''}`.trim(),
        phone: user.primaryPhoneNumber?.phoneNumber || '',
      }));
    }
  }, [isLoaded, user]);

  const handleChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) setCurrentStep(prev => prev + 1);
  };

  const handleBack = () => {
    if (currentStep > 0) setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const token = await getToken();
      const client = buildClient(token || undefined);
      await client.put('/v1/profile', {
        ...formData,
        profile_complete: true
      });
      router.push('/dashboard');
    } catch (err: unknown) {
      console.error("Failed to save profile:", err);
      // Clean up unique phone number error message
      if (typeof err === 'object' && err !== null && 'response' in err) {
         const respErr = err as { response?: { status?: number } };
         if (respErr.response?.status === 409) {
            setError("This phone number is already registered to another account.");
            setIsSubmitting(false);
            return;
         }
      }
      setError("Failed to save your profile. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      
      {/* Background Decor */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 -z-10 h-[500px] w-[500px] rounded-full bg-primary/10 blur-[120px]"></div>
        <div className="absolute bottom-0 left-0 -z-10 h-[400px] w-[400px] rounded-full bg-blue-500/10 blur-[100px]"></div>
      </div>

      <div className="w-full max-w-2xl relative z-10">
        
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-orange-600 shadow-lg mb-6">
            <span className="font-bold text-2xl text-white">JS</span>
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Welcome to JanSathi</h1>
          <p className="text-secondary-foreground opacity-80">Let&apos;s set up your profile to match you with the right schemes.</p>
        </div>

        {/* Progress Tracker */}
        <div className="flex items-center justify-between mb-8 px-2">
          {STEPS.map((step, index) => {
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            return (
              <div key={step.id} className="flex flex-col items-center relative z-10 w-1/5">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isActive ? 'bg-primary text-white shadow-lg shadow-primary/30 ring-4 ring-primary/20' : 
                  isCompleted ? 'bg-emerald-500 text-white' : 'bg-secondary text-secondary-foreground/40'
                }`}>
                  {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : <step.icon className="w-5 h-5" />}
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-widest mt-3 hidden sm:block ${
                  isActive ? 'text-primary' : isCompleted ? 'text-emerald-500' : 'text-secondary-foreground/40'
                }`}>{step.title}</span>
                
                {/* Connector Line */}
                {index < STEPS.length - 1 && (
                  <div className={`absolute top-5 left-[60%] w-[80%] h-0.5 -z-10 ${
                    isCompleted ? 'bg-emerald-500' : 'bg-secondary'
                  }`}></div>
                )}
              </div>
            );
          })}
        </div>

        {/* Form Container */}
        <div className="bg-card border border-border/50 rounded-[2rem] shadow-xl p-8 sm:p-12 mb-8 relative overflow-hidden">
          
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 text-sm font-medium">
              {error}
            </div>
          )}

          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -20, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              
              {/* STEP 1: Personal Details */}
              {currentStep === 0 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-foreground">Basic Information</h2>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Full Name</label>
                      <input type="text" value={formData.full_name} onChange={(e) => handleChange('full_name', e.target.value)} placeholder="e.g. Ramesh Kumar" className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 placeholder:text-secondary-foreground/30 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Mobile Number (For IVR/SMS)</label>
                      <input type="tel" value={formData.phone} onChange={(e) => handleChange('phone', e.target.value)} placeholder="+91" className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 placeholder:text-secondary-foreground/30 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Age</label>
                      <input type="number" value={formData.age} onChange={(e) => handleChange('age', e.target.value)} placeholder="Years" className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 placeholder:text-secondary-foreground/30 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" />
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Gender</label>
                      <select value={formData.gender} onChange={(e) => handleChange('gender', e.target.value)} className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all appearance-none">
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 2: Location */}
              {currentStep === 1 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-foreground">Where are you from?</h2>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">State</label>
                      <select value={formData.state} onChange={(e) => handleChange('state', e.target.value)} className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all appearance-none">
                        <option value="">Select State</option>
                        <option value="Uttar Pradesh">Uttar Pradesh</option>
                        <option value="Madhya Pradesh">Madhya Pradesh</option>
                        <option value="Maharashtra">Maharashtra</option>
                        <option value="Karnataka">Karnataka</option>
                        <option value="Tamil Nadu">Tamil Nadu</option>
                      </select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">District</label>
                      <input type="text" value={formData.district} onChange={(e) => handleChange('district', e.target.value)} className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Village / Town</label>
                      <input type="text" value={formData.village} onChange={(e) => handleChange('village', e.target.value)} className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" />
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Pincode</label>
                      <input type="text" value={formData.pincode} onChange={(e) => handleChange('pincode', e.target.value)} className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" />
                    </div>
                  </div>
                </div>
              )}

              {/* STEP 3: Socioeconomic */}
              {currentStep === 2 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-foreground">Socioeconomic Profile</h2>
                  <p className="text-sm text-secondary-foreground opacity-80 mb-6">This helps us match you with highly targeted government schemes.</p>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Occupation</label>
                      <select value={formData.occupation} onChange={(e) => handleChange('occupation', e.target.value)} className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all appearance-none">
                        <option value="Farmer">Farmer</option>
                        <option value="Agricultural Laborer">Agricultural Laborer</option>
                        <option value="Daily Wage Worker">Daily Wage Worker</option>
                        <option value="Artisan">Artisan / Weaver</option>
                        <option value="Student">Student</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Caste Category</label>
                      <select value={formData.category} onChange={(e) => handleChange('category', e.target.value)} className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all appearance-none">
                        <option value="General">General</option>
                        <option value="OBC">OBC</option>
                        <option value="SC">SC</option>
                        <option value="ST">ST</option>
                      </select>
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Annual Income (₹)</label>
                      <input type="number" value={formData.annual_income} onChange={(e) => handleChange('annual_income', e.target.value)} placeholder="e.g. 150000" className="w-full bg-secondary/30 border border-border/50 rounded-xl px-4 py-3 placeholder:text-secondary-foreground/30 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" />
                    </div>

                    {formData.occupation === 'Farmer' && (
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-secondary-foreground uppercase tracking-widest ml-1">Land Holding (Acres)</label>
                        <input type="number" step="0.1" value={formData.land_holding_acres} onChange={(e) => handleChange('land_holding_acres', e.target.value)} placeholder="e.g. 2.5" className="w-full bg-emerald-500/10 border border-emerald-500/30 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-emerald-700 dark:text-emerald-400 font-medium" />
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* STEP 4: Documents */}
              {currentStep === 3 && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-foreground">Which documents do you have?</h2>
                  <p className="text-sm text-secondary-foreground opacity-80 mb-6">Select the official documents you currently possess. We don&apos;t need the actual files right now.</p>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[
                      { id: 'has_aadhaar', label: 'Aadhaar Card' },
                      { id: 'has_ration_card', label: 'Ration Card' },
                      { id: 'has_bank_account', label: 'Active Bank Account' },
                      { id: 'has_pm_kisan', label: 'PM-KISAN Beneficiary' },
                    ].map((doc) => (
                      <div 
                        key={doc.id}
                        onClick={() => handleChange(doc.id, !formData[doc.id as keyof typeof formData])}
                        className={`p-4 rounded-xl border flex items-center gap-4 cursor-pointer transition-all ${
                          formData[doc.id as keyof typeof formData] 
                            ? 'bg-primary/10 border-primary/40 shadow-[0_0_15px_rgba(255,107,0,0.1)]' 
                            : 'bg-secondary/30 border-border/50 hover:bg-secondary/50'
                        }`}
                      >
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
                          formData[doc.id as keyof typeof formData] ? 'border-primary bg-primary' : 'border-secondary-foreground/30 bg-background'
                        }`}>
                          {formData[doc.id as keyof typeof formData] && <CheckCircle2 className="w-4 h-4 text-white" />}
                        </div>
                        <span className={`font-medium ${formData[doc.id as keyof typeof formData] ? 'text-primary' : 'text-foreground'}`}>
                          {doc.label}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* STEP 5: Language */}
              {currentStep === 4 && (
                <div className="space-y-6">
                  <div className="text-center mb-8">
                    <div className="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Languages className="w-10 h-10 text-blue-500" />
                    </div>
                    <h2 className="text-2xl font-bold text-foreground mb-2">Platform Language</h2>
                    <p className="text-sm text-secondary-foreground opacity-80 max-w-sm mx-auto">
                      Choose your preferred language for Voice Calls (IVR), text messages, and the dashboard.
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg mx-auto">
                    {[
                      { id: 'hi', label: 'Hindi (हिन्दी)', local: 'हिन्दी' },
                      { id: 'en', label: 'English', local: 'English' },
                      { id: 'ta', label: 'Tamil (தமிழ்)', local: 'தமிழ்' },
                      { id: 'kn', label: 'Kannada (ಕನ್ನಡ)', local: 'ಕನ್ನಡ' },
                    ].map((lang) => (
                      <div 
                        key={lang.id}
                        onClick={() => handleChange('preferred_language', lang.id)}
                        className={`p-4 rounded-xl border text-center cursor-pointer transition-all ${
                          formData.preferred_language === lang.id 
                            ? 'bg-blue-500/10 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.15)]' 
                            : 'bg-secondary/30 border-border/50 hover:bg-secondary/50'
                        }`}
                      >
                        <p className={`font-bold text-lg mb-1 ${formData.preferred_language === lang.id ? 'text-blue-600 dark:text-blue-400' : 'text-foreground'}`}>
                          {lang.local}
                        </p>
                        <p className="text-xs text-secondary-foreground opacity-60 uppercase tracking-widest">{lang.label}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </motion.div>
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between mt-12 pt-6 border-t border-border/50">
            <button 
              onClick={handleBack}
              disabled={currentStep === 0 || isSubmitting}
              className={`px-6 py-3 rounded-xl font-bold text-sm flex items-center gap-2 transition-all ${
                currentStep === 0 ? 'opacity-0 pointer-events-none' : 'bg-secondary text-foreground hover:bg-secondary/80'
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
                {isSubmitting ? 'Saving...' : 'Complete Setup'}
                {!isSubmitting && <CheckCircle2 className="w-4 h-4" />}
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
