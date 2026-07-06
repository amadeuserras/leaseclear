'use client';

import { useEffect, useState } from 'react';

// One open menu at a time; any click elsewhere closes it.
export const useKebabMenu = () => {
  const [openId, setOpenId] = useState<string | null>(null);

  useEffect(() => {
    if (openId === null) return;
    const close = () => setOpenId(null);
    document.addEventListener('click', close);
    return () => document.removeEventListener('click', close);
  }, [openId]);

  const toggle = (id: string) => setOpenId((prev) => (prev === id ? null : id));

  return { openId, toggle, close: () => setOpenId(null) };
};
