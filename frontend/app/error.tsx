'use client';

type ErrorPageProps = {
  reset: () => void;
};

export default function ErrorPage({ reset }: ErrorPageProps) {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 p-6">
      <div className="text-text-main text-[14.5px]">Something went wrong.</div>
      <div className="text-text-secondary text-[13px]">
        Couldn&apos;t reach the LeaseClear API — check that the backend is running.
      </div>
      <button
        onClick={reset}
        className="border-hairline-input bg-bg-inset text-text-main hover:bg-bg-inset-hover cursor-pointer rounded-lg border px-4 py-2 text-[13px] font-medium"
      >
        Try again
      </button>
    </main>
  );
}
