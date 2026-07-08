'use client';

import { ApiError, streamQuery } from '@/lib/api';
import { clearSession, getToken } from '@/lib/session';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  streaming?: boolean;
  error?: boolean;
};

const errorText = (e: unknown): string => {
  if (e instanceof ApiError && e.status === 429) {
    return 'Too many questions — try again in a minute.';
  }
  return 'Something went wrong answering that. Please try again.';
};

export const useChat = (selectedIds: string[]) => {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const patchMessage = (id: string, patch: Partial<ChatMessage>) =>
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)));

  const clear = () => setMessages([]);

  const exportChat = () => {
    if (messages.length === 0) return;

    const transcript = messages
      .map((m) => `${m.role === 'user' ? 'You' : 'LeaseClear'}: ${m.text}`)
      .join('\n\n');

    const blob = new Blob([transcript], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leaseclear-chat-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const send = async (question: string) => {
    if (isStreaming || !question.trim() || selectedIds.length === 0) return;

    const answerId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', text: question.trim() },
      { id: answerId, role: 'assistant', text: '', streaming: true },
    ]);
    setIsStreaming(true);

    try {
      await streamQuery({
        question: question.trim(),
        documentIds: selectedIds,
        token: getToken() ?? '',
        onToken: (t) =>
          setMessages((prev) =>
            prev.map((m) => (m.id === answerId ? { ...m, text: m.text + t } : m)),
          ),
        onDone: () => patchMessage(answerId, { streaming: false }),
      });
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        clearSession();
        router.push('/login');
        return;
      }
      patchMessage(answerId, { text: errorText(e), streaming: false, error: true });
    } finally {
      setIsStreaming(false);
    }
  };

  return { messages, isStreaming, send, clear, exportChat };
};
