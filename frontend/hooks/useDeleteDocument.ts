'use client';

import { ApiError, deleteDocument } from '@/lib/api';
import { clearSession, getToken } from '@/lib/session';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

// Deletes a document server-side, then refreshes the server-fetched list so the
// row disappears (mirrors useUpload). Returns whether the delete succeeded so
// the caller can react — e.g. close the viewer if the open document was removed.
export const useDeleteDocument = () => {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const remove = async (id: string): Promise<boolean> => {
    setError(null);
    try {
      await deleteDocument(id, getToken() ?? '');
      router.refresh();
      return true;
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        clearSession();
        router.push('/login');
      } else {
        setError('Couldn’t delete this document.');
      }
      return false;
    }
  };

  return { error, remove };
};
