import { LoginCard } from '@/components/LoginCard';
import { TOKEN_COOKIE } from '@/lib/session';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function LoginPage() {
  const cookieStore = await cookies();
  if (cookieStore.has(TOKEN_COOKIE)) redirect('/');

  return (
    <main className="flex min-h-dvh items-center justify-center p-6">
      <LoginCard />
    </main>
  );
}
