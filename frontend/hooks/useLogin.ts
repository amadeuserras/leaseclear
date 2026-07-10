'use client';

import { ApiError, login, register } from '@/lib/api';
import { beginSession } from '@/lib/session';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export type LoginNotice = {
  kind: 'error' | 'info';
  text: string;
};

const messageFor = (e: unknown): string => {
  if (e instanceof ApiError) {
    if (e.status === 401) return 'Incorrect email or password.';
    if (e.status === 429) return 'Too many attempts — try again in a minute.';
    return e.message;
  }
  return 'Could not reach the server. Please try again.';
};

export const useLogin = (onSuccess?: () => void) => {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notice, setNotice] = useState<LoginNotice | null>(null);

  const submit = async (mode: 'login' | 'register', email: string, password: string) => {
    if (!email || !password) {
      setNotice({ kind: 'error', text: 'Enter your email and password.' });
      return;
    }
    setIsSubmitting(true);
    setNotice(null);
    try {
      const auth = mode === 'login' ? login : register;
      const { access_token } = await auth(email, password);
      onSuccess?.();
      beginSession(router, access_token, email);
    } catch (e) {
      setNotice({ kind: 'error', text: messageFor(e) });
      setIsSubmitting(false);
    }
  };

  // Parked: no backend OAuth endpoint yet.
  const googleSignIn = () =>
    setNotice({ kind: 'info', text: "Google sign-in isn't available yet." });

  const tryDemo = () => router.push('/demo');

  return { isSubmitting, notice, submit, googleSignIn, tryDemo };
};
