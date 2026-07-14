export type AnswerSegment = { type: 'text'; value: string } | { type: 'citation'; id: string };

const CITATION_RE = /\[([a-z0-9-]+) (§[^\]]+|p\d+(?:\(\d+\))?)\]/g;

/** Split answer text on inline citation ids like [slug §3] / [slug p1]. */
export const segmentAnswer = (text: string): AnswerSegment[] => {
  const segments: AnswerSegment[] = [];
  let cursor = 0;
  for (const match of text.matchAll(CITATION_RE)) {
    if (match.index > cursor) {
      segments.push({ type: 'text', value: text.slice(cursor, match.index) });
    }
    segments.push({ type: 'citation', id: match[0] });
    cursor = match.index + match[0].length;
  }
  if (cursor < text.length) {
    segments.push({ type: 'text', value: text.slice(cursor) });
  }
  return segments;
};

export const slugFromCitationId = (citationId: string): string | null => {
  const match = /^\[([a-z0-9-]+) /.exec(citationId);
  return match?.[1] ?? null;
};

export const withholdPartialCitation = (text: string): string => {
  const open = text.lastIndexOf('[');
  if (open === -1 || text.indexOf(']', open) !== -1) return text;
  return text.slice(0, open);
};
