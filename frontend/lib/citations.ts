export type AnswerSegment =
  | { type: 'text'; value: string }
  | { type: 'citation'; value: string; slug: string; citation: string };

const CITATION_RE = /\[([a-z0-9-]+) (§[^\]]+|p\d+(?:\(\d+\))?)\]/g;

const prettifySlug = (slug: string) =>
  slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

export const citationLabel = (slug: string, ref: string, docNames: Map<string, string>) =>
  `${docNames.get(slug) ?? prettifySlug(slug)} · ${ref}`;

/** Split answer text on inline citation ids like [slug §3] / [slug p1]. */
export const segmentAnswer = (text: string, docNames: Map<string, string>): AnswerSegment[] => {
  const segments: AnswerSegment[] = [];
  let cursor = 0;
  for (const match of text.matchAll(CITATION_RE)) {
    if (match.index > cursor) {
      segments.push({ type: 'text', value: text.slice(cursor, match.index) });
    }
    segments.push({
      type: 'citation',
      value: citationLabel(match[1], match[2], docNames),
      slug: match[1],
      citation: match[2],
    });
    cursor = match.index + match[0].length;
  }
  if (cursor < text.length) {
    segments.push({ type: 'text', value: text.slice(cursor) });
  }
  return segments;
};

export const withholdPartialCitation = (text: string): string => {
  const open = text.lastIndexOf('[');
  if (open === -1 || text.indexOf(']', open) !== -1) return text;
  return text.slice(0, open);
};
