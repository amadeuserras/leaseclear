'use client';

import { listSuggestedQuestions } from '@/lib/api';
import { getToken } from '@/lib/session';
import { useEffect, useState } from 'react';

// Fetches LLM-suggested starter questions for the current documents. The backend
// caches these per document set, so this is effectively one call per deploy.
// Returns [] on any failure — callers fall back to static example prompts.
export const useSuggestedQuestions = (): string[] => {
  const [questions, setQuestions] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await listSuggestedQuestions(getToken() ?? '');
        if (!cancelled) setQuestions(result);
      } catch {
        // Keep the fallback prompts.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return questions;
};
