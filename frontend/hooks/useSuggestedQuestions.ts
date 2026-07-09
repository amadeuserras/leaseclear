'use client';

import { listSuggestedQuestions } from '@/lib/api';
import { getToken } from '@/lib/session';
import { useEffect, useState } from 'react';

// Fetches LLM-suggested starter questions for the current documents. Re-fetches
// whenever `documentKey` changes (upload/delete) so suggestions track the live
// document set; the backend caches the pool per set, so this stays cheap.
export const useSuggestedQuestions = (documentKey: string) => {
  const [questions, setQuestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setIsLoading(true);
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
  }, [documentKey]);

  return { questions, isLoading };
};
