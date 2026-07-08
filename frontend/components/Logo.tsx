import { CheckIcon } from '@/components/icons';

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
      <CheckIcon size={isLogin ? 19 : 14} color="#ffffff" strokeWidth={isLogin ? 2.6 : 2.8} />
    </div>
  );
}
