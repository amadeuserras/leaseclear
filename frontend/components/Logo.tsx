type LogoMarkProps = {
  size: 'login' | 'topbar';
};

export function LogoMark({ size }: LogoMarkProps) {
  const isLogin = size === 'login';
  return (
    <div
      className={
        isLogin
          ? 'bg-logo flex h-[38px] w-[46px] items-center justify-center rounded-[14px_14px_14px_4px]'
          : 'bg-logo flex h-[26px] w-[32px] items-center justify-center rounded-[10px_10px_10px_3px]'
      }
    >
      <svg width={isLogin ? 19 : 14} height={isLogin ? 19 : 14} viewBox="0 0 24 24" fill="none">
        <path
          d="M5 13l4 4L19 7"
          stroke="#ffffff"
          strokeWidth={isLogin ? 2.6 : 2.8}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}
