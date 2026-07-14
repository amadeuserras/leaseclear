type CitationChipProps = {
  citationId: string;
  onClick?: () => void;
  className?: string;
};

const unwrapCitationId = (citationId: string): string =>
  citationId.startsWith('[') && citationId.endsWith(']') ? citationId.slice(1, -1) : citationId;

export function CitationChip({ citationId, onClick, className = '' }: CitationChipProps) {
  return (
    <span
      onClick={onClick}
      className={`inline-flex items-center rounded-[20px] bg-white/6 px-2 py-px text-[11px] font-medium whitespace-nowrap text-[rgba(236,237,239,0.5)] ${
        onClick ? 'cursor-pointer hover:bg-white/12 hover:text-[#ECEDEF]' : ''
      } ${className}`}
    >
      {unwrapCitationId(citationId)}
    </span>
  );
}
