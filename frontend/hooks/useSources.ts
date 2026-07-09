'use client';

import type { LeaseDocument } from '@/lib/api';
import { useMemo, useState } from 'react';

export type Source = LeaseDocument & { checked: boolean };

export const useSources = (documents: LeaseDocument[]) => {
  const [uncheckedIds, setUncheckedIds] = useState<ReadonlySet<string>>(new Set());

  const sources: Source[] = useMemo(
    () => documents.map((d) => ({ ...d, checked: !uncheckedIds.has(d.id) })),
    [documents, uncheckedIds],
  );

  const selectedIds = useMemo(() => sources.filter((s) => s.checked).map((s) => s.id), [sources]);

  const allChecked = sources.length > 0 && sources.every((s) => s.checked);

  const toggle = (id: string) =>
    setUncheckedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const toggleAll = () =>
    setUncheckedIds(allChecked ? new Set(documents.map((d) => d.id)) : new Set());

  return { sources, selectedIds, allChecked, toggle, toggleAll };
};
