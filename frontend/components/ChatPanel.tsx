"use client";

import { useEffect, useRef, useState } from "react";
import { segmentAnswer, withholdPartialCitation } from "@/lib/citations";
import type { ChatMessage } from "@/hooks/useChat";

type AssistantMessageProps = {
  message: ChatMessage;
  docNames: Map<string, string>;
};

function AssistantMessage({ message, docNames }: AssistantMessageProps) {
  if (message.error) {
    return (
      <div className="max-w-[84%] text-[14.5px] leading-[1.7] text-text-secondary">
        {message.text}
      </div>
    );
  }
  const text = message.streaming ? withholdPartialCitation(message.text) : message.text;
  return (
    <div className="max-w-[84%] text-[14.5px] leading-[1.7] text-[rgba(236,237,239,0.9)]">
      {segmentAnswer(text, docNames).map((seg, i) =>
        seg.type === "text" ? (
          <span key={i}>{seg.value}</span>
        ) : (
          <span
            key={i}
            className="mx-0.5 inline-flex cursor-default items-center gap-1 rounded-[20px] border border-white/18 bg-white/10 px-2 py-px align-middle text-[11.5px] font-medium whitespace-nowrap text-text-main"
          >
            {seg.value}
          </span>
        ),
      )}
    </div>
  );
}

type MessageListProps = {
  messages: ChatMessage[];
  docNames: Map<string, string>;
};

function MessageList({ messages, docNames }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  return (
    <div
      ref={scrollRef}
      className="custom-scrollbar flex min-h-0 flex-1 flex-col gap-[22px] overflow-y-auto px-8 py-7"
    >
      {messages.map((m) =>
        m.role === "user" ? (
          <div key={m.id} className="flex justify-end">
            <div className="max-w-[72%] rounded-[14px] bg-bg-inset px-[15px] py-2.5 text-[14.5px] leading-[1.55] text-text-main">
              {m.text}
            </div>
          </div>
        ) : (
          <AssistantMessage key={m.id} message={m} docNames={docNames} />
        ),
      )}
    </div>
  );
}

type ChatPanelProps = {
  messages: ChatMessage[];
  isStreaming: boolean;
  selectedCount: number;
  docNames: Map<string, string>;
  onSend: (question: string) => void;
};

export function ChatPanel({
  messages,
  isStreaming,
  selectedCount,
  docNames,
  onSend,
}: ChatPanelProps) {
  const [draft, setDraft] = useState("");

  const canSend = !isStreaming && draft.trim().length > 0 && selectedCount > 0;

  const submit = () => {
    if (!canSend) return;
    onSend(draft);
    setDraft("");
  };

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col rounded-xl border border-hairline bg-bg-surface">
      <MessageList messages={messages} docNames={docNames} />

      <form
        className="shrink-0 border-t border-hairline px-5 pt-4 pb-5"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <div className="flex items-center gap-2.5 rounded-[24px] border border-hairline-input bg-bg-inset py-2 pr-2 pl-[18px] focus-within:border-white/35">
          <input
            type="text"
            placeholder="Ask a question about your lease…"
            className="flex-1 border-none bg-transparent text-sm text-text-main outline-none"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <div className="shrink-0 text-xs whitespace-nowrap text-text-muted">
            {selectedCount} source{selectedCount === 1 ? "" : "s"}
          </div>
          <button
            type="submit"
            disabled={!canSend}
            className="flex h-[34px] w-[34px] shrink-0 cursor-pointer items-center justify-center rounded-full bg-emphasis hover:bg-emphasis-hover disabled:cursor-default"
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
      </form>
    </section>
  );
}
