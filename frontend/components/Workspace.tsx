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
  const { questions: suggestions, isLoading: isLoadingSuggestions } =
    useSuggestedQuestions(selectedIds);
  const viewer = useViewer();

  const [collapsed, setCollapsed] = useState(false);

  // Draggable panel widths. The sources handle sits on its right edge (drag
  // right → wider); the viewer handle sits on its left edge (drag left → wider).
  const sourcesResize = useResizable(320, 220, 560, 1);
  const viewerResize = useResizable(340, 260, 640, -1);

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
            width={viewerResize.width}
            onResizeStart={viewerResize.startResize}
            onClose={closeDoc}
          />
        )}
      </main>
    </>
  );
}
