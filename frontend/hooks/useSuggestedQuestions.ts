'use client';

import { listSuggestedQuestions } from '@/lib/api';
import { getToken } from '@/lib/session';
import { useEffect, useState } from 'react';

export const useSuggestedQuestions = (selectedIds: string[]) => {
  const [questions, setQuestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const key = [...selectedIds].sort().join(',');
  const empty = key === '';

  useEffect(() => {
    if (key === '') return;
    let cancelled = false;
    (async () => {
      setIsLoading(true);
      try {
        const result = await listSuggestedQuestions(getToken() ?? '', key.split(','));
        if (!cancelled) setQuestions(result);
      } catch {
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [key]);

  return empty ? { questions: [], isLoading: false } : { questions, isLoading };
};
