'use client';

import { useCallback, useRef, useState } from 'react';

export const useResizable = (initial: number, min: number, max: number, dir: 1 | -1 = 1) => {
  const [width, setWidth] = useState(initial);
  const [isResizing, setIsResizing] = useState(false);
  const origin = useRef<{ x: number; width: number } | null>(null);

  const onPointerMove = useRef((e: PointerEvent) => {
    const o = origin.current;
    if (!o) return;
    const next = o.width + dir * (e.clientX - o.x);
    setWidth(Math.min(max, Math.max(min, next)));
  });

  const onPointerUp = useRef(() => {
    origin.current = null;
    setIsResizing(false);
    document.removeEventListener('pointermove', onPointerMove.current);
    document.removeEventListener('pointerup', onPointerUp.current);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  });

  const startResize = useCallback(
    (e: React.PointerEvent) => {
      e.preventDefault();
      origin.current = { x: e.clientX, width };
      setIsResizing(true);
      document.addEventListener('pointermove', onPointerMove.current);
      document.addEventListener('pointerup', onPointerUp.current);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    },
    [width],
  );

  return { width, isResizing, startResize };
};
