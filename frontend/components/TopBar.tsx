'use client';

import { LogoMark } from '@/components/Logo';
import { useKebabMenu } from '@/hooks/useKebabMenu';
import { clearSession } from '@/lib/session';
import { useRouter } from 'next/navigation';

type TopBarProps = {
  initials: string;
  email: string;
  isDemo?: boolean;
  onClearChat: () => void;
};

export function TopBar({ initials, email, isDemo, onClearChat }: TopBarProps) {
  const router = useRouter();
  const menu = useKebabMenu();

  const logOut = () => {
    clearSession();
    router.push('/login');
  };

  return (
    <header className="border-hairline flex shrink-0 items-center justify-between border-b px-7 py-3.5">
      <div className="flex items-center gap-2.5">
        <LogoMark size="topbar" />
        <div className="text-text-main text-[15px] font-semibold tracking-[-0.01em]">
          LeaseClear
        </div>
      </div>

      <div className="flex items-center gap-3.5">
        {isDemo && (
          <div className="text-[12px] whitespace-nowrap text-[rgba(236,237,239,0.5)]">
            You&apos;re in demo mode &middot;{' '}
            <span
              onClick={logOut}
              className="cursor-pointer text-[rgba(236,237,239,0.85)] underline underline-offset-2 hover:text-[#ECEDEF]"
            >
              sign up
            </span>
          </div>
        )}

        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              menu.toggle('account');
            }}
            title="More"
            className="hover:text-text-main flex h-7 w-7 cursor-pointer items-center justify-center rounded-md text-[15px] leading-none text-[rgba(236,237,239,0.5)] hover:bg-white/8"
          >
            ⋯
          </button>
          {menu.openId === 'account' && (
            <div className="border-hairline-input bg-bg-inset absolute top-8 right-0 z-10 w-[170px] rounded-[10px] border p-[5px] shadow-[0_8px_24px_rgba(0,0,0,0.4)]">
              {/* Parked: no chat-export endpoint yet — visual only. */}
              <div className="text-text-main cursor-pointer rounded-md px-2.5 py-2 text-[12.5px] hover:bg-white/6">
                Export chat
              </div>
              <div
                onClick={onClearChat}
                className="cursor-pointer rounded-md px-2.5 py-2 text-[12.5px] text-[#e0776f] hover:bg-[rgba(224,119,111,0.12)]"
              >
                Clear chat
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <div
            onClick={(e) => {
              e.stopPropagation();
              menu.toggle('avatar');
            }}
            className="bg-avatar text-text-main flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-[12.5px] font-semibold"
          >
            {initials}
          </div>
          {menu.openId === 'avatar' && (
            <div className="border-hairline-input bg-bg-inset absolute top-10 right-0 z-10 w-[200px] rounded-[10px] border p-[5px] shadow-[0_8px_24px_rgba(0,0,0,0.4)]">
              <div className="border-hairline mb-1 truncate border-b px-2.5 pt-2.5 pb-2 text-[12.5px] text-[rgba(236,237,239,0.5)]">
                {email}
              </div>
              <div
                onClick={logOut}
                className="text-text-main cursor-pointer rounded-md px-2.5 py-2 text-[12.5px] hover:bg-white/6"
              >
                Log out
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
