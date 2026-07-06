import { LogoMark } from "@/components/Logo";

type TopBarProps = {
  initials: string;
};

export function TopBar({ initials }: TopBarProps) {
  return (
    <header className="flex shrink-0 items-center justify-between border-b border-hairline px-7 py-3.5">
      <div className="flex items-center gap-2.5">
        <LogoMark size="topbar" />
        <div className="text-[15px] font-semibold tracking-[-0.01em] text-text-main">
          LeaseClear
        </div>
      </div>
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-avatar text-[12.5px] font-semibold text-text-main">
        {initials}
      </div>
    </header>
  );
}
