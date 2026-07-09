import { Workspace } from '@/components/Workspace';
import { ApiError, listDocuments, type LeaseDocument } from '@/lib/api';
import { DEMO_COOKIE, EMAIL_COOKIE, TOKEN_COOKIE } from '@/lib/session';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function Home() {
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_COOKIE)?.value;
  if (!token) redirect('/login');

  let documents: LeaseDocument[];
  try {
    documents = await listDocuments(token);
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) redirect('/login');
    throw e;
  }

  const email = cookieStore.get(EMAIL_COOKIE)?.value ?? '';
  const isDemo = cookieStore.get(DEMO_COOKIE)?.value === '1';

  return (
    <div className="flex h-dvh flex-col overflow-hidden">
      <Workspace key={email} documents={documents} email={email} isDemo={isDemo} />
    </div>
  );
}
