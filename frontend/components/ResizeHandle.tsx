'use client';

type ResizeHandleProps = {
  side: 'left' | 'right';
  onPointerDown: (e: React.PointerEvent) => void;
};

// An invisible drag strip straddling a panel's inner edge. It gives the panel a
// col-resize cursor along that edge and starts the drag, with no visible line.
export function ResizeHandle({ side, onPointerDown }: ResizeHandleProps) {
  return (
    <div
      role="separator"
      aria-orientation="vertical"
      onPointerDown={onPointerDown}
      className={`absolute top-0 bottom-0 z-10 w-4 cursor-col-resize ${
        side === 'right' ? '-right-2' : '-left-2'
      }`}
    />
  );
}
