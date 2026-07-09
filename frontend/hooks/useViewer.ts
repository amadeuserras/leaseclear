'use client';

import { ApiError, getDocumentChunks, type DocumentChunk } from '@/lib/api';
import { clearSession, getToken } from '@/lib/session';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export type ViewerTarget = {
  slug: string;
  name: string;
  citationRef: string | null;
};

// Drives the right-hand document panel: which document is open, its chunks, and
// the citation reference to highlight/scroll to when arriving from a citation click.
export const useViewer = () => {
  const router = useRouter();
  const [target, setTarget] = useState<ViewerTarget | null>(null);
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(false);

  const open = async (slug: string, name: string, citationRef: string | null = null) => {
    const sameDoc = target?.slug === slug;
    setTarget({ slug, name, citationRef });
    if (sameDoc && !error) return; // chunks already loaded; just move the highlight

    setIsLoading(true);
    setError(false);
    try {
      setChunks(await getDocumentChunks(slug, getToken() ?? ''));
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        clearSession();
        router.push('/login');
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
