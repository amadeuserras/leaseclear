'use client';

import { ApiError, deleteDocument } from '@/lib/api';
import { clearSession } from '@/lib/session';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export const useDeleteDocument = () => {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const remove = async (id: string): Promise<boolean> => {
    setError(null);
    try {
      await deleteDocument(id);
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
