'use client';

import { ApiError, getDocumentChunks, type DocumentChunk } from '@/lib/api';
import { endSession } from '@/lib/session';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export type ViewerTarget = {
  slug: string;
  name: string;
  citation: string | null;
};

export const useViewer = () => {
  const router = useRouter();
  const [target, setTarget] = useState<ViewerTarget | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(false);

  const open = async (slug: string, name: string, citation: string | null = null) => {
    const sameDoc = target?.slug === slug;
    setTarget({ slug, name, citation });
    if (sameDoc && !error) return;

    setIsLoading(true);
    setError(false);
    try {
      setChunks(await getDocumentChunks(slug));
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        endSession(router);
        return;
      }
      setError(true);
    } finally {
      setIsLoading(false);
    }
  };

  const close = () => {
    setTarget(null);
    setChunks([]);
    setError(false);
  };

  return { target, chunks, isLoading, error, isOpen: target !== null, open, close };
};
