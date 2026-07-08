'use client';

import type { ViewerTarget } from '@/hooks/useViewer';
import type { DocumentChunk } from '@/lib/api';
import { chunkCitationId } from '@/lib/citations';

type ChunkItemProps = {
  slug: string;
  chunk: DocumentChunk;
  highlighted: boolean;
};

function ChunkItem({ slug, chunk, highlighted }: ChunkItemProps) {
  return (
    <div>
      <div className="mb-1.5 flex flex-wrap items-center gap-2">
        {chunk.clause_label && (
          <div className="text-text-main text-[13px] font-semibold">{chunk.clause_label}</div>
        )}
        <span className="inline-flex items-center rounded-[20px] bg-white/6 px-2 py-px text-[11px] font-medium whitespace-nowrap text-[rgba(236,237,239,0.5)]">
          {chunkCitationId(slug, chunk)}
        </span>
      </div>
      <div
        className={`rounded box-decoration-clone text-[13.5px] leading-[1.65] text-[rgba(236,237,239,0.78)] ${
          highlighted ? 'bg-highlight px-1 py-0.5' : ''
        }`}
      >
        {chunk.passage}
      </div>
    </div>
  );
}

type DocumentViewerProps = {
  target: ViewerTarget;
  chunks: DocumentChunk[];
  isLoading: boolean;
  error: boolean;
  onClose: () => void;
};

export function DocumentViewer({ target, chunks, isLoading, error, onClose }: DocumentViewerProps) {
  return (
    <section className="border-hairline bg-bg-surface flex min-h-0 w-[340px] shrink-0 flex-col rounded-xl border">
      <div className="border-hairline flex shrink-0 items-center justify-between gap-2.5 border-b px-[18px] py-4">
        <div className="min-w-0">
          <div className="text-text-main truncate text-[13.5px] font-semibold">{target.name}</div>
          <div className="mt-0.5 text-[11.5px] text-[rgba(236,237,239,0.45)]">
            {isLoading ? 'Loading…' : `${chunks.length} chunk${chunks.length === 1 ? '' : 's'}`}
          </div>
        </div>
        <button
          onClick={onClose}
          title="Close"
          className="hover:text-text-main flex h-[26px] w-[26px] shrink-0 cursor-pointer items-center justify-center rounded-md text-[rgba(236,237,239,0.5)] hover:bg-white/8"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M6 6l12 12M18 6L6 18"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      <div className="custom-scrollbar flex min-h-0 flex-1 flex-col gap-[18px] overflow-y-auto px-[18px] pt-3.5 pb-5">
        {error ? (
          <div className="text-text-secondary text-[13px]">Couldn’t load this document.</div>
        ) : (
          chunks.map((c) => (
            <ChunkItem
              key={c.chunk_id}
              slug={target.slug}
              chunk={c}
              highlighted={
                target.highlightClause !== null && c.clause_number === target.highlightClause
              }
            />
          ))
        )}
      </div>
    </section>
  );
}
