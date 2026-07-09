'use client';

import { listSuggestedQuestions } from '@/lib/api';
import { getToken } from '@/lib/session';
import { useEffect, useState } from 'react';

// Re-fetches on `documentKey` change; cheap since the backend caches the pool per document set.
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
