"use client";

type ErrorPageProps = {
  reset: () => void;
};

export default function ErrorPage({ reset }: ErrorPageProps) {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 p-6">
      <div className="text-[14.5px] text-text-main">Something went wrong.</div>
      <div className="text-[13px] text-text-secondary">
        Couldn&apos;t reach the LeaseClear API — check that the backend is running.
      </div>
      <button
        onClick={reset}
        className="cursor-pointer rounded-lg border border-hairline-input bg-bg-inset px-4 py-2 text-[13px] font-medium text-text-main hover:bg-bg-inset-hover"
      >
        Try again
      </button>
    </main>
  );
}
