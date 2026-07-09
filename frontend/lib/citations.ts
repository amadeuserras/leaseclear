export type AnswerSegment =
  | { type: 'text'; value: string }
  | { type: 'citation'; value: string; slug: string; ref: string };

const CITATION_RE = /\[([a-z0-9-]+) (§[^\]]+|p\.[^\]]+)\]/g;

const displayRef = (ref: string) => (ref.startsWith('p.') ? ref.split('@')[0] : ref);

const prettifySlug = (slug: string) =>
  slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

export const citationLabel = (slug: string, ref: string, docNames: Map<string, string>) =>
  `${docNames.get(slug) ?? prettifySlug(slug)} · ${displayRef(ref)}`;

// The bracketed id shown next to a chunk in the viewer, mirroring the format the
// backend emits in answers: [slug §clause] for numbered clauses, else [slug p.N@char].
export const chunkCitationId = (
  slug: string,
  chunk: { clause_number: string | null; page_number: number; char_start: number },
): string =>
  chunk.clause_number
    ? `[${slug} §${chunk.clause_number}]`
    : `[${slug} p.${chunk.page_number}@${chunk.char_start}]`;

// Whether a viewer chunk is the one a citation `ref` (e.g. "§4.1" or "p.3@1024")
// points at, by reconstructing the bracketed id the backend would emit for it.
export const chunkMatchesCitation = (
  slug: string,
  ref: string,
  chunk: { clause_number: string | null; page_number: number; char_start: number },
): boolean => chunkCitationId(slug, chunk) === `[${slug} ${ref}]`;

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
      ref: match[2],
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
