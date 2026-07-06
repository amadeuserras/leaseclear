import { LogoMark } from '@/components/Logo';

type TopBarProps = {
  initials: string;
};

export function TopBar({ initials }: TopBarProps) {
  return (
    <header className="border-hairline flex shrink-0 items-center justify-between border-b px-7 py-3.5">
      <div className="flex items-center gap-2.5">
        <LogoMark size="topbar" />
        <div className="text-text-main text-[15px] font-semibold tracking-[-0.01em]">
          LeaseClear
        </div>
      </div>
      <div className="bg-avatar text-text-main flex h-8 w-8 items-center justify-center rounded-full text-[12.5px] font-semibold">
        {initials}
      </div>
    </header>
  );
}
