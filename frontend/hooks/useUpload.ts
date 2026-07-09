'use client';

import { ApiError, uploadDocuments } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export const useUpload = () => {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);
    setError(null);
    try {
      await uploadDocuments(Array.from(files));
      router.refresh();
    } catch (e) {
      if (e instanceof ApiError && e.status === 429) {
        setError('Too many uploads — try again in a minute.');
      } else if (e instanceof ApiError) {
        setError(e.message);
      } else {
        setError('Upload failed. Please try again.');
      }
    } finally {
      setIsUploading(false);
    }
  };

  return { isUploading, error, upload };
};
