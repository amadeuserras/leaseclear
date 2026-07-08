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

const MOCK_MESSAGES: ChatMessage[] = [
  { id: 'mock-1', role: 'user', text: 'What happens if I pay rent 5 days late?' },
  {
    id: 'mock-2',
    role: 'assistant',
    text: 'Rent is due on the 1st, with a 5-day grace period [lease §3.2]. After that, a late fee of $75 plus $10/day applies [lease §3.2]. On day 5 you would owe the base late fee only, since it falls within the grace window.',
  },
  { id: 'mock-3', role: 'user', text: 'Can I have a cat? Is there a pet deposit?' },
  {
    id: 'mock-4',
    role: 'assistant',
    text: 'Yes — one cat is allowed with prior written approval [pet-addendum §1]. A separate pet deposit of $350 applies, plus a non-refundable $25/month pet fee [pet-addendum §2].',
  },
  {
    id: 'mock-5',
    role: 'user',
    text: 'What is the security deposit, and when do I get it back after move-out?',
  },
  {
    id: 'mock-6',
    role: 'assistant',
    text: "The security deposit is $2,400, equal to one month's rent [lease §4.1]. Your landlord must return it, minus any lawful deductions, within 21 days of move-out [lease §4.3].",
  },
];

export const useChat = (selectedIds: string[]) => {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>(MOCK_MESSAGES);
  const [isStreaming, setIsStreaming] = useState(false);

  const patchMessage = (id: string, patch: Partial<ChatMessage>) =>
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)));

  const clear = () => setMessages([]);

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

  return { messages, isStreaming, send, clear };
};
