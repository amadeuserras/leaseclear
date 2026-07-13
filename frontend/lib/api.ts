import { config } from '@/lib/config';
import { getToken } from '@/lib/session';

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type LeaseDocument = {
  id: string;
  filename: string;
  slug: string;
  landlord_name: string | null;
  tenant_names: string[];
  property_address: string | null;
};

export type Citation = {
  chunk_id: string;
  clause_label: string;
  page_number: number;
  passage: string;
};

export type DocumentChunk = {
  chunk_id: string;
  clause_number: string | null;
  clause_label: string | null;
  page_number: number;
  char_start: number;
  passage: string;
};

export type QueryResult = {
  answer: string;
  citations: Citation[];
};

export type StreamQueryParams = {
  question: string;
  documentIds: string[];
  onToken: (token: string) => void;
  onDone: (result: QueryResult) => void;
  signal?: AbortSignal;
};

export type GoogleAuthResponse = TokenResponse & {
  email: string;
};

export type MeResponse = {
  email: string;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

const authHeader = (): Record<string, string> => {
  const token = getToken() ?? '';
  return { Authorization: `Bearer ${token}` };
};

const errorFromResponse = async (res: Response): Promise<ApiError> => {
  let detail = '';
  try {
    const body: unknown = await res.json();
    if (body && typeof body === 'object' && 'detail' in body) {
      detail = String((body as { detail: unknown }).detail);
    }
  } catch {}
  return new ApiError(res.status, detail || `Request failed (${res.status})`);
};

const postJson = async <T>(path: string, body: unknown): Promise<T> => {
  const res = await fetch(`${config.apiUrl}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await errorFromResponse(res);
  return (await res.json()) as T;
};

export const login = (email: string, password: string) =>
  postJson<TokenResponse>('/auth/login', { email, password });

export const register = (email: string, password: string) =>
  postJson<TokenResponse>('/auth/register', { email, password });

export const demoLogin = () => postJson<TokenResponse>('/auth/demo', {});

export const googleLogin = (accessToken: string) =>
  postJson<GoogleAuthResponse>('/auth/google', { access_token: accessToken });

export const getMe = async (token: string): Promise<MeResponse> => {
  const res = await fetch(`${config.apiUrl}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: 'no-store',
  });
  if (!res.ok) throw await errorFromResponse(res);
  return (await res.json()) as MeResponse;
};

export const listSuggestedQuestions = async (documentIds: string[]): Promise<string[]> => {
  const res = await fetch(`${config.apiUrl}/documents/suggested-questions/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(),
    },
    cache: 'no-store',
    body: JSON.stringify({ document_ids: documentIds }),
  });
  if (!res.ok) throw await errorFromResponse(res);
  const body = (await res.json()) as { questions: string[] };
  return body.questions;
};

export const listDocuments = async (token: string): Promise<LeaseDocument[]> => {
  const res = await fetch(`${config.apiUrl}/documents`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: 'no-store',
  });
  if (!res.ok) throw await errorFromResponse(res);
  return (await res.json()) as LeaseDocument[];
};

export const getDocumentChunks = async (slug: string): Promise<DocumentChunk[]> => {
  const res = await fetch(`${config.apiUrl}/documents/${encodeURIComponent(slug)}/chunks`, {
    headers: authHeader(),
    cache: 'no-store',
  });
  if (!res.ok) throw await errorFromResponse(res);
  return (await res.json()) as DocumentChunk[];
};

export const deleteDocument = async (id: string): Promise<void> => {
  const res = await fetch(`${config.apiUrl}/documents/${encodeURIComponent(id)}`, {
    method: 'DELETE',
    headers: authHeader(),
  });
  if (!res.ok) throw await errorFromResponse(res);
};

export const uploadDocuments = async (files: File[]): Promise<void> => {
  const form = new FormData();
  for (const f of files) form.append('files', f);
  const res = await fetch(`${config.apiUrl}/documents`, {
    method: 'POST',
    headers: authHeader(),
    body: form,
  });
  if (!res.ok) throw await errorFromResponse(res);
};

type SseEvent = {
  event: string;
  data: string;
};

const parseSseEvent = (block: string): SseEvent => {
  let event = 'message';
  const data: string[] = [];
  for (const line of block.split(/\r?\n/)) {
    if (line.startsWith('event:')) event = line.slice(6).trimStart();
    else if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /, ''));
  }
  return { event, data: data.join('\n') };
};

export const streamQuery = async ({
  question,
  documentIds,
  onToken,
  onDone,
  signal,
}: StreamQueryParams): Promise<void> => {
  const res = await fetch(`${config.apiUrl}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(),
    },
    body: JSON.stringify({ question, document_ids: documentIds }),
    signal,
  });
  if (!res.ok || !res.body) throw await errorFromResponse(res);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  const dispatch = (block: string) => {
    const { event, data } = parseSseEvent(block);
    if (event === 'token') onToken(data);
    else if (event === 'done') onDone(JSON.parse(data) as QueryResult);
  };

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split(/\r?\n\r?\n/);
    buffer = blocks.pop() ?? '';
    for (const b of blocks) if (b.trim()) dispatch(b);
  }
  if (buffer.trim()) dispatch(buffer);
};
