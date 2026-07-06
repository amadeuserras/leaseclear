'use client';

import { useKebabMenu } from '@/hooks/useKebabMenu';
import type { Source } from '@/hooks/useSources';
import { useUpload } from '@/hooks/useUpload';
import { useRef } from 'react';

type CheckboxProps = {
  checked: boolean;
  onToggle: () => void;
};

function Checkbox({ checked, onToggle }: CheckboxProps) {
  return (
    <div
      role="checkbox"
      aria-checked={checked}
      onClick={onToggle}
      className={`flex h-[19px] w-[19px] shrink-0 cursor-pointer items-center justify-center rounded-[5px] border-[1.5px] ${
        checked ? 'border-checkbox-checked bg-checkbox-checked' : 'border-white/25 bg-transparent'
      }`}
    >
      {checked && (
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
          <path
            d="M5 13l4 4L19 7"
            stroke="#ECEDEF"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </div>
  );
}

function PdfIcon() {
  return (
    <div className="border-hairline bg-bg-inset-hover relative flex h-[30px] w-[26px] shrink-0 items-end justify-center overflow-hidden rounded-[3px] border">
      <div className="border-r-bg-main absolute top-0 right-0 h-0 w-0 border-t-0 border-r-[8px] border-b-[8px] border-l-0 border-solid border-b-transparent" />
      <div className="mb-[3px] text-[6px] font-bold tracking-[0.02em] text-[rgba(236,237,239,0.5)]">
        PDF
      </div>
    </div>
  );
}

type SourceRowProps = {
  source: Source;
  menuOpen: boolean;
  onToggle: () => void;
  onMenuToggle: () => void;
  onMenuClose: () => void;
};

function SourceRow({ source, menuOpen, onToggle, onMenuToggle, onMenuClose }: SourceRowProps) {
  return (
    <div className="relative mb-0.5 flex items-center gap-2.5 rounded-lg px-2 py-[9px] hover:bg-white/5">
      <PdfIcon />
      <div className="text-text-main min-w-0 flex-1 truncate text-[13px]">{source.filename}</div>
      <Checkbox checked={source.checked} onToggle={onToggle} />
      <div className="relative shrink-0">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onMenuToggle();
          }}
          className="hover:text-text-main flex h-[22px] w-[22px] cursor-pointer items-center justify-center rounded-md text-sm leading-none text-[rgba(236,237,239,0.5)] hover:bg-white/8"
        >
          ⋯
        </button>
        {menuOpen && (
          <div className="border-hairline-input bg-bg-inset absolute top-[26px] right-0 z-10 min-w-[110px] rounded-lg border p-1 shadow-[0_6px_20px_rgba(0,0,0,0.4)]">
            {/* Parked: no DELETE /documents endpoint — visual only per handoff. */}
            <div
              onClick={onMenuClose}
              className="text-text-main cursor-pointer rounded-[5px] px-2.5 py-[7px] text-[12.5px] hover:bg-white/6"
            >
              Remove
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

type SourcesPanelProps = {
  sources: Source[];
  selectedCount: number;
  allChecked: boolean;
  onToggle: (id: string) => void;
  onToggleAll: () => void;
};

export function SourcesPanel({
  sources,
  selectedCount,
  allChecked,
  onToggle,
  onToggleAll,
}: SourcesPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { isUploading, error, upload } = useUpload();
  const menu = useKebabMenu();

  return (
    <section className="border-hairline bg-bg-surface flex min-h-0 w-[450px] shrink-0 flex-col rounded-xl border">
      <div className="flex shrink-0 items-center justify-between px-[18px] pt-4 pb-2.5">
        <div className="text-text-main text-[13.5px] font-semibold">Sources</div>
        <div className="text-text-muted text-xs">
          {selectedCount} of {sources.length}
        </div>
      </div>

      <div className="shrink-0 px-[18px] pb-3.5">
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          multiple
          className="hidden"
          onChange={(e) => {
            upload(e.target.files);
            e.target.value = '';
          }}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="border-hairline-input bg-bg-inset text-text-main hover:border-hairline-hover hover:bg-bg-inset-hover flex w-full cursor-pointer items-center justify-center gap-[7px] rounded-lg border p-[9px] text-[13px] font-medium disabled:cursor-default disabled:opacity-70"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 4v12M12 4l-5 5M12 4l5 5"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          {isUploading ? 'Uploading…' : 'Upload documents'}
        </button>
        {error && <div className="mt-2 text-[12px] text-[#e07f84]">{error}</div>}
      </div>

      <div className="border-hairline flex shrink-0 items-center justify-end gap-[9px] border-b px-[18px] pt-1 pb-3">
        <label
          onClick={onToggleAll}
          className="shrink-0 cursor-pointer text-[13px] whitespace-nowrap text-[rgba(236,237,239,0.7)]"
        >
          Select all
        </label>
        <Checkbox checked={allChecked} onToggle={onToggleAll} />
        <div className="w-[22px] shrink-0" />
      </div>

      <div className="custom-scrollbar min-h-0 flex-1 overflow-y-auto px-2.5 py-2">
        {sources.map((s) => (
          <SourceRow
            key={s.id}
            source={s}
            menuOpen={menu.openId === s.id}
            onToggle={() => onToggle(s.id)}
            onMenuToggle={() => menu.toggle(s.id)}
            onMenuClose={menu.close}
          />
        ))}
      </div>
    </section>
  );
}
