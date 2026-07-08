'use client';

import type { ChatMessage } from '@/hooks/useChat';
import { segmentAnswer, withholdPartialCitation } from '@/lib/citations';
import { Fragment, useState } from 'react';

const SKELETON_WIDTHS = ['118px', '96px', '140px', '104px'];

type Entry = {
  id: string;
  question: string;
  answer: ChatMessage | undefined;
};

const toEntries = (messages: ChatMessage[]): Entry[] => {
  const entries: Entry[] = [];
  for (const m of messages) {
    if (m.role === 'user') {
      entries.push({ id: m.id, question: m.text, answer: undefined });
    } else if (entries.length > 0) {
      entries[entries.length - 1].answer = m;
    }
  }
  return entries;
};

type AnswerBodyProps = {
  message: ChatMessage;
  docNames: Map<string, string>;
  onCitation: (slug: string, clause: string | null) => void;
};

function AnswerBody({ message, docNames, onCitation }: AnswerBodyProps) {
  if (message.error) {
    return <div className="text-text-secondary text-[14.5px] leading-[1.7]">{message.text}</div>;
  }

  if (message.streaming && message.text.length === 0) {
    return (
      <div className="animate-lc-sweep inline-block bg-[linear-gradient(90deg,rgba(236,237,239,0.32)_25%,rgba(236,237,239,0.75)_50%,rgba(236,237,239,0.32)_78%)] bg-size-[200%_100%] bg-clip-text text-[14.5px] leading-[1.7] font-medium text-transparent">
        Reading your lease…
      </div>
    );
  }

  const text = message.streaming ? withholdPartialCitation(message.text) : message.text;
  const segments = segmentAnswer(text, docNames);

  return (
    <div className="text-[14.5px] leading-[1.7] text-[rgba(236,237,239,0.82)]">
      {segments.map((seg, i) =>
        seg.type === 'text' ? (
          message.streaming ? (
            seg.value.split(' ').map((w, j) => (
              <Fragment key={`${i}-${j}`}>
                <span className="animate-lc-fade-word inline-block">{w}</span>
                {j < seg.value.split(' ').length - 1 && ' '}
              </Fragment>
            ))
          ) : (
            <span key={i}>{seg.value}</span>
          )
        ) : (
          <span
            key={i}
            onClick={() => onCitation(seg.slug, seg.clause)}
            className={`mx-0.5 inline-flex cursor-pointer items-center gap-1 rounded-[20px] bg-white/6 px-2 py-px align-middle text-[11px] font-medium whitespace-nowrap text-[rgba(236,237,239,0.5)] hover:bg-white/12 hover:text-[#ECEDEF] ${message.streaming ? 'animate-lc-fade-word' : ''}`}
          >
            {seg.value}
          </span>
        ),
      )}
    </div>
  );
}

type EntryItemProps = {
  entry: Entry;
  docNames: Map<string, string>;
  onCitation: (slug: string, clause: string | null) => void;
};

function EntryItem({ entry, docNames, onCitation }: EntryItemProps) {
  return (
    <div className="space-y-2.5">
      <div className="text-text-main text-[16.5px] leading-[1.4] font-semibold">
        {entry.question}
      </div>
      {entry.answer && (
        <AnswerBody message={entry.answer} docNames={docNames} onCitation={onCitation} />
      )}
    </div>
  );
}

type ComposerProps = {
  draft: string;
  selectedCount: number;
  centered: boolean;
  questions: string[];
  isLoadingSuggestions: boolean;
  onDraftChange: (value: string) => void;
  onSubmit: () => void;
  onExample: (question: string) => void;
};

function Composer({
  draft,
  selectedCount,
  centered,
  questions,
  isLoadingSuggestions,
  onDraftChange,
  onSubmit,
  onExample,
}: ComposerProps) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <div className="border-hairline-input bg-bg-inset flex items-center gap-2.5 rounded-[26px] border py-2.5 pr-2.5 pl-5 focus-within:border-white/35">
        <input
          type="text"
          placeholder="Ask a question about your lease…"
          className="text-text-main flex-1 border-none bg-transparent text-[15px] outline-none"
          value={draft}
          onChange={(e) => onDraftChange(e.target.value)}
        />
        <div className="text-text-muted shrink-0 text-xs whitespace-nowrap">
          {selectedCount} source{selectedCount === 1 ? '' : 's'}
        </div>
        <button
          type="submit"
          disabled={selectedCount === 0}
          className="bg-emphasis hover:bg-emphasis-hover disabled:hover:bg-emphasis flex h-[34px] w-[34px] shrink-0 cursor-pointer items-center justify-center rounded-full disabled:cursor-not-allowed disabled:opacity-40"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 19V5M12 5l-6 6M12 5l6 6"
              stroke="#17181b"
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <div
        className={`mt-3 flex min-h-16 flex-wrap gap-2 ${centered ? 'justify-center' : 'justify-start'}`}
      >
        {isLoadingSuggestions
          ? SKELETON_WIDTHS.map((w, i) => (
              <div
                key={i}
                style={{ width: w, animationDelay: `${i * 0.15}s` }}
                className="animate-lc-pulse h-[26px] rounded-[20px] bg-white/[0.07] opacity-[0.35]"
              />
            ))
          : questions.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => onExample(q)}
                className="cursor-pointer rounded-[20px] border border-white/8 px-3 py-[5px] text-xs whitespace-nowrap text-[rgba(236,237,239,0.42)] hover:border-white/14 hover:bg-white/5 hover:text-[rgba(236,237,239,0.7)]"
              >
                {q}
              </button>
            ))}
      </div>
    </form>
  );
}

type ChatPanelProps = {
  messages: ChatMessage[];
  isStreaming: boolean;
  selectedCount: number;
  docNames: Map<string, string>;
  suggestions: string[];
  isLoadingSuggestions: boolean;
  onSend: (question: string) => void;
  onCitation: (slug: string, clause: string | null) => void;
};

export function ChatPanel({
  messages,
  isStreaming,
  selectedCount,
  docNames,
  suggestions,
  isLoadingSuggestions,
  onSend,
  onCitation,
}: ChatPanelProps) {
  const [draft, setDraft] = useState('');
  const entries = toEntries(messages).reverse();
  const canSubmit = !isStreaming && selectedCount > 0;

  const submit = () => {
    if (!canSubmit || draft.trim().length === 0) return;
    onSend(draft);
    setDraft('');
  };

  const sendExample = (question: string) => {
    if (canSubmit) onSend(question);
    else setDraft(question);
  };

  return (
    <div className="flex min-h-0 min-w-[380px] flex-1 justify-center">
      <div className="flex min-h-0 w-full max-w-[760px] min-w-0 flex-col">
        {entries.length > 0 ? (
          <>
            <div className="shrink-0 px-1 pt-10 pb-7">
              <Composer
                draft={draft}
                selectedCount={selectedCount}
                centered={false}
                questions={suggestions}
                isLoadingSuggestions={isLoadingSuggestions}
                onDraftChange={setDraft}
                onSubmit={submit}
                onExample={sendExample}
              />
            </div>
            <div className="custom-scrollbar min-h-0 flex-1 space-y-11 overflow-y-auto px-1 pt-9 pb-8">
              {entries.map((entry) => (
                <EntryItem
                  key={entry.id}
                  entry={entry}
                  docNames={docNames}
                  onCitation={onCitation}
                />
              ))}
            </div>
          </>
        ) : (
          <div className="flex flex-1 flex-col items-center justify-center gap-[26px] px-1 pt-5 pb-[12vh]">
            <div className="text-center">
              <div className="text-text-main text-[30px] font-semibold tracking-[-0.02em]">
                Ask your lease anything
              </div>
            </div>
            <div className="w-full">
              <Composer
                draft={draft}
                selectedCount={selectedCount}
                centered={true}
                questions={suggestions}
                isLoadingSuggestions={isLoadingSuggestions}
                onDraftChange={setDraft}
                onSubmit={submit}
                onExample={sendExample}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
