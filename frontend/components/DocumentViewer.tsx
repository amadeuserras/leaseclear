'use client';

import { ResizeHandle } from '@/components/ResizeHandle';
import { CloseIcon } from '@/components/icons';
import type { ViewerTarget } from '@/hooks/useViewer';
import type { DocumentChunk, LeaseDocument } from '@/lib/api';
import { forwardRef, useEffect, useRef } from 'react';

type ChunkItemProps = {
  chunk: DocumentChunk;
  highlighted: boolean;
};

const ChunkItem = forwardRef<HTMLDivElement, ChunkItemProps>(function ChunkItem(
  { chunk, highlighted },
  ref,
) {
  return (
    <div ref={ref} className="scroll-mt-2">
      <div className="mb-1.5 flex flex-wrap items-center gap-2">
        {(chunk.clause_number || chunk.clause_title) && (
          <div className="text-text-main text-[13px] font-semibold">
            {[chunk.clause_number && `${chunk.clause_number}.`, chunk.clause_title]
              .filter(Boolean)
              .join(' ')}
          </div>
        )}
        <span className="inline-flex items-center rounded-[20px] bg-white/6 px-2 py-px text-[11px] font-medium whitespace-nowrap text-[rgba(236,237,239,0.5)]">
          {chunk.citation_id}
        </span>
      </div>
      <div
        className={`rounded box-decoration-clone text-[13.5px] leading-[1.65] text-[rgba(236,237,239,0.78)] ${
          highlighted ? 'bg-highlight px-1 py-0.5' : ''
        }`}
      >
        {chunk.text}
      </div>
    </div>
  );
});

type DocumentViewerProps = {
  target: ViewerTarget;
  documents: LeaseDocument[];
  chunks: DocumentChunk[];
  isLoading: boolean;
  error: boolean;
  width: number;
  onResizeStart: (e: React.PointerEvent) => void;
  onClose: () => void;
};

export function DocumentViewer({
  target,
  documents,
  chunks,
  isLoading,
  error,
  width,
  onResizeStart,
  onClose,
}: DocumentViewerProps) {
  const citedRef = useRef<HTMLDivElement>(null);
  const doc = documents.find((d) => d.slug === target.slug);
  const name = doc?.filename ?? target.slug;

  useEffect(() => {
    citedRef.current?.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }, [target.slug, target.citationId, chunks]);

  return (
    <section
      style={{ width }}
      className="border-hairline bg-bg-surface relative flex min-h-0 shrink-0 flex-col rounded-xl border"
    >
      <ResizeHandle side="left" onPointerDown={onResizeStart} />

      <div className="border-hairline flex shrink-0 items-center justify-between gap-2.5 border-b px-[18px] py-4">
        <div className="min-w-0">
          <div className="text-text-main truncate text-[13.5px] font-semibold">{name}</div>
          <div className="mt-0.5 text-[11.5px] text-[rgba(236,237,239,0.45)]">
            {isLoading ? 'Loading…' : `${chunks.length} chunk${chunks.length === 1 ? '' : 's'}`}
          </div>
        </div>
        <button
          onClick={onClose}
          title="Close"
          className="hover:text-text-main flex h-[26px] w-[26px] shrink-0 cursor-pointer items-center justify-center rounded-md text-[rgba(236,237,239,0.5)] hover:bg-white/8"
        >
          <CloseIcon />
        </button>
      </div>

      <div className="custom-scrollbar flex min-h-0 flex-1 flex-col gap-[18px] overflow-y-auto px-[18px] pt-3.5 pb-5">
        {error ? (
          <div className="text-text-secondary text-[13px]">Couldn’t load this document.</div>
        ) : (
          chunks.map((c) => {
            const cited = target.citationId !== null && c.citation_id === target.citationId;
            return (
              <ChunkItem
                key={c.chunk_id}
                ref={cited ? citedRef : undefined}
                chunk={c}
                highlighted={cited}
              />
            );
          })
        )}
      </div>
    </section>
  );
}
