import { LoginCard } from '@/components/LoginCard';
import { ApiError, getMe } from '@/lib/api';
import { TOKEN_COOKIE } from '@/lib/session';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function LoginPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_COOKIE)?.value;
  if (token) {
    try {
      await getMe(token);
      redirect('/');
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) redirect('/logout');
      throw e;
    }
  }

  return (
    <main className="flex min-h-dvh items-center justify-center p-6">
      <LoginCard />
    </main>
  );
}
