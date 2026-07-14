'use client';

import { ChatPanel } from '@/components/ChatPanel';
import { DocumentViewer } from '@/components/DocumentViewer';
import { SourcesPanel } from '@/components/SourcesPanel';
import { TopBar } from '@/components/TopBar';
import { useChat } from '@/hooks/useChat';
import { useResizable } from '@/hooks/useResizable';
import type { Source } from '@/hooks/useSources';
import { useSources } from '@/hooks/useSources';
import { useSuggestedQuestions } from '@/hooks/useSuggestedQuestions';
import { useViewer } from '@/hooks/useViewer';
import type { LeaseDocument } from '@/lib/api';
import { slugFromCitationId } from '@/lib/citations';
import { initialsFromEmail } from '@/lib/session';
import { useState } from 'react';

type WorkspaceProps = {
  documents: LeaseDocument[];
  email: string;
  isDemo: boolean;
};

export function Workspace({ documents, email, isDemo }: WorkspaceProps) {
  const { sources, selectedIds, allChecked, toggle, toggleAll } = useSources(documents);
  const { messages, isStreaming, send, clear, exportChat } = useChat(selectedIds);
  const { questions: suggestions, isLoading: isLoadingSuggestions } =
    useSuggestedQuestions(selectedIds);
  const viewer = useViewer();

  const [collapsed, setCollapsed] = useState(false);

  const sourcesResize = useResizable(320, 220, 560, 1);
  const viewerResize = useResizable(340, 260, 640, -1);

  const openDoc = (slug: string, citationId: string | null = null) => viewer.open(slug, citationId);

  const closeDoc = () => viewer.close();

  const openSource = (source: Source) => openDoc(source.slug);

  const onDeleted = (source: Source) => {
    if (viewer.target?.slug === source.slug) closeDoc();
  };

  const openCitation = (citationId: string) => {
    const slug = slugFromCitationId(citationId);
    if (!slug) return;
    openDoc(slug, citationId);
  };

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
          width={sourcesResize.width}
          isResizing={sourcesResize.isResizing}
          isDemo={isDemo}
          onToggle={toggle}
          onToggleAll={toggleAll}
          onToggleCollapsed={() => setCollapsed((c) => !c)}
          onResizeStart={sourcesResize.startResize}
          onOpen={openSource}
          onDeleted={onDeleted}
        />
        <ChatPanel
          messages={messages}
          isStreaming={isStreaming}
          selectedCount={selectedIds.length}
          suggestions={suggestions}
          isLoadingSuggestions={isLoadingSuggestions}
          onSend={send}
          onCitation={openCitation}
        />
        {viewer.target && (
          <DocumentViewer
            target={viewer.target}
            documents={documents}
            chunks={viewer.chunks}
            isLoading={viewer.isLoading}
            error={viewer.error}
            width={viewerResize.width}
            onResizeStart={viewerResize.startResize}
            onClose={closeDoc}
          />
        )}
      </main>
    </>
  );
}
