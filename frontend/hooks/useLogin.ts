'use client';

import { ApiError, googleLogin, login, register } from '@/lib/api';
import { requestGoogleAccessToken } from '@/lib/google';
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
    if (e.status === 503) return 'Google sign-in is not configured.';
    return e.message;
  }
  if (e instanceof Error) return e.message;
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

  const googleSignIn = async () => {
    setIsSubmitting(true);
    setNotice(null);
    try {
      const googleAccessToken = await requestGoogleAccessToken();
      const { access_token, email } = await googleLogin(googleAccessToken);
      onSuccess?.();
      beginSession(router, access_token, email);
    } catch (e) {
      setNotice({ kind: 'error', text: messageFor(e) });
      setIsSubmitting(false);
    }
  };

  const tryDemo = () => router.push('/demo');

  return { isSubmitting, notice, submit, googleSignIn, tryDemo };
};
