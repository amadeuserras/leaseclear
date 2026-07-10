'use client';

import { LogoMark } from '@/components/Logo';
import { demoLogin } from '@/lib/api';
import { beginSession, DEMO_EMAIL } from '@/lib/session';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function DemoPage() {
  const router = useRouter();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { access_token } = await demoLogin();
        if (cancelled) return;
        beginSession(router, access_token, DEMO_EMAIL, { demo: true, replace: true });
      } catch {
        if (!cancelled) setFailed(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [router]);

  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 p-6">
      <LogoMark size="login" />
      {failed ? (
        <>
          <div className="text-text-main text-[14.5px]">
            The demo isn&apos;t available right now.
          </div>
          <button
            onClick={() => router.push('/login')}
            className="border-hairline-input bg-bg-inset text-text-main hover:bg-bg-inset-hover cursor-pointer rounded-lg border px-4 py-2 text-[13px] font-medium"
          >
            Go to sign in
          </button>
        </>
      ) : (
        <div className="text-text-secondary text-[13px]">Loading your demo…</div>
      )}
    </main>
  );
}
