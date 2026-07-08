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
import { useMemo, useRef, useState } from 'react';

const filenameStem = (filename: string) => filename.replace(/\.[^.]+$/, '');

type WorkspaceProps = {
  documents: LeaseDocument[];
  email: string;
  isDemo: boolean;
};

export function Workspace({ documents, email, isDemo }: WorkspaceProps) {
  const { sources, selectedIds, allChecked, toggle, toggleAll } = useSources(documents);
  const { messages, isStreaming, send, clear } = useChat(selectedIds);
  const suggestions = useSuggestedQuestions();
  const viewer = useViewer();

  const [collapsed, setCollapsed] = useState(false);
  const priorCollapsed = useRef(false);

  const docNames = useMemo(
    () => new Map(documents.map((d) => [d.slug, filenameStem(d.filename)])),
    [documents],
  );

  // Opening a document collapses the sources rail to make room; closing restores it.
  const openDoc = (slug: string, name: string, clause: string | null = null) => {
    if (!viewer.isOpen) priorCollapsed.current = collapsed;
    setCollapsed(true);
    viewer.open(slug, name, clause);
  };

  const closeDoc = () => {
    viewer.close();
    setCollapsed(priorCollapsed.current);
  };

  const openSource = (source: Source) => openDoc(source.slug, filenameStem(source.filename));

  const openCitation = (slug: string, clause: string | null) =>
    openDoc(slug, docNames.get(slug) ?? slug, clause);

  return (
    <>
      <TopBar initials={initialsFromEmail(email)} email={email} onClearChat={clear} />
      <main className="flex min-h-0 flex-1 gap-4 overflow-x-auto px-6 py-5">
        <SourcesPanel
          sources={sources}
          allChecked={allChecked}
          collapsed={collapsed}
          readOnly={isDemo}
          onToggle={toggle}
          onToggleAll={toggleAll}
          onToggleCollapsed={() => setCollapsed((c) => !c)}
          onOpen={openSource}
        />
        <ChatPanel
          messages={messages}
          isStreaming={isStreaming}
          selectedCount={selectedIds.length}
          docNames={docNames}
          suggestions={suggestions}
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
