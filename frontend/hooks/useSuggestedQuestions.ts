'use client';

import { listSuggestedQuestions } from '@/lib/api';
import { getToken } from '@/lib/session';
import { useEffect, useState } from 'react';

// Fetches LLM-suggested starter questions for the current documents. The backend
// caches these per document set, so this is effectively one call per deploy.
export const useSuggestedQuestions = () => {
  const [questions, setQuestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await listSuggestedQuestions(getToken() ?? '');
        if (!cancelled) setQuestions(result);
      } catch {
        // Leave questions empty on failure.
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { questions, isLoading };
};
