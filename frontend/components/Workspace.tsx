'use client';

import { ChatPanel } from '@/components/ChatPanel';
import { DocumentViewer } from '@/components/DocumentViewer';
import { SourcesPanel } from '@/components/SourcesPanel';
import { TopBar } from '@/components/TopBar';
import { useChat } from '@/hooks/useChat';
import type { Source } from '@/hooks/useSources';
import { useSources } from '@/hooks/useSources';
import { useSuggestedQuestions } from '@/hooks/useSuggestedQuestions';
import { useViewer } from '@/hooks/useViewer';
import type { LeaseDocument } from '@/lib/api';
import { initialsFromEmail } from '@/lib/session';
import { useMemo, useState } from 'react';

const filenameStem = (filename: string) => filename.replace(/\.[^.]+$/, '');

type WorkspaceProps = {
  documents: LeaseDocument[];
  email: string;
  isDemo: boolean;
};

export function Workspace({ documents, email, isDemo }: WorkspaceProps) {
  const { sources, selectedIds, allChecked, toggle, toggleAll } = useSources(documents);
  const { messages, isStreaming, send, clear, exportChat } = useChat(selectedIds);
  // Re-fetch suggestions whenever the document set changes (upload/delete), since
  // the backend keys them per document set.
  const documentKey = useMemo(
    () => documents.map((d) => d.id).sort().join(','),
    [documents],
  );
  const { questions: suggestions, isLoading: isLoadingSuggestions } =
    useSuggestedQuestions(documentKey);
  const viewer = useViewer();

  const [collapsed, setCollapsed] = useState(false);

  const docNames = useMemo(
    () => new Map(documents.map((d) => [d.slug, filenameStem(d.filename)])),
    [documents],
  );

  const openDoc = (slug: string, name: string, citationRef: string | null = null) =>
    viewer.open(slug, name, citationRef);

  const closeDoc = () => viewer.close();

  const openSource = (source: Source) => openDoc(source.slug, filenameStem(source.filename));

  const onDeleted = (source: Source) => {
    if (viewer.target?.slug === source.slug) closeDoc();
  };

  const openCitation = (slug: string, ref: string) =>
    openDoc(slug, docNames.get(slug) ?? slug, ref);

  return (
    <>
      <TopBar
        initials={initialsFromEmail(email)}
        email={email}
        isDemo={isDemo}
        hasMessages={messages.length > 0}
        onClearChat={clear}
        onExportChat={exportChat}
      />
      <main className="flex min-h-0 flex-1 gap-4 overflow-x-auto px-6 py-5">
        <SourcesPanel
          sources={sources}
          allChecked={allChecked}
          collapsed={collapsed}
          isDemo={isDemo}
          onToggle={toggle}
          onToggleAll={toggleAll}
          onToggleCollapsed={() => setCollapsed((c) => !c)}
          onOpen={openSource}
          onDeleted={onDeleted}
        />
        <ChatPanel
          messages={messages}
          isStreaming={isStreaming}
          selectedCount={selectedIds.length}
          docNames={docNames}
          suggestions={suggestions}
          isLoadingSuggestions={isLoadingSuggestions}
          onSend={send}
          onCitation={openCitation}
        />
        {viewer.target && (
          <DocumentViewer
            target={viewer.target}
            chunks={viewer.chunks}
            isLoading={viewer.isLoading}
            error={viewer.error}
            onClose={closeDoc}
          />
        )}
      </main>
    </>
  );
}
