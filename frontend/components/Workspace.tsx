'use client';

import { ChatPanel } from '@/components/ChatPanel';
import { SourcesPanel } from '@/components/SourcesPanel';
import { useChat } from '@/hooks/useChat';
import { useSources } from '@/hooks/useSources';
import type { LeaseDocument } from '@/lib/api';
import { useMemo } from 'react';

const filenameStem = (filename: string) => filename.replace(/\.[^.]+$/, '');

type WorkspaceProps = {
  documents: LeaseDocument[];
};

export function Workspace({ documents }: WorkspaceProps) {
  const { sources, selectedIds, allChecked, toggle, toggleAll } = useSources(documents);
  const { messages, isStreaming, send } = useChat(selectedIds);

  const docNames = useMemo(
    () => new Map(documents.map((d) => [d.slug, filenameStem(d.filename)])),
    [documents],
  );

  return (
    <main className="flex min-h-0 flex-1 gap-5 px-7 py-5">
      <SourcesPanel
        sources={sources}
        selectedCount={selectedIds.length}
        allChecked={allChecked}
        onToggle={toggle}
        onToggleAll={toggleAll}
      />
      <ChatPanel
        messages={messages}
        isStreaming={isStreaming}
        selectedCount={selectedIds.length}
        docNames={docNames}
        onSend={send}
      />
    </main>
  );
}
