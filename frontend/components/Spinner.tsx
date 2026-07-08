'use client';

type SpinnerProps = {
  size?: number;
  className?: string;
};

export function Spinner({ size = 17, className = '' }: SpinnerProps) {
  return (
    <>
      <style>{`
        @keyframes lc-spin {
          100% { transform: rotate(360deg); }
        }
        @keyframes lc-spin-dash {
          0% { stroke-dasharray: 1, 150; stroke-dashoffset: 0; }
          50% { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
          100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
        }
        .lc-spinner { animation: lc-spin 1.1s linear infinite; display: block; }
        .lc-spinner circle { animation: lc-spin-dash 1.4s ease-in-out infinite; stroke-linecap: round; }
      `}</style>
      <svg
        width={size}
        height={size}
        viewBox="0 0 50 50"
        className={`lc-spinner shrink-0 text-current ${className}`}
      >
        <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5" />
      </svg>
    </>
  );
}
