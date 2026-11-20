// Port of Store.retrieve / Store.answer in rag/core.py: authorization first, then BM25-style scoring whose
// corpus and IDF statistics contain only the documents the principal may read. Documents are short, so each
// is one chunk (chunks() splits at 120 words).
export const tokens = text => (text.toLowerCase().match(/[\p{L}\p{N}_-]+/gu) || []);
const count = arr => arr.reduce((m, t) => m.set(t, (m.get(t) || 0) + 1), new Map());
export function retrieve(docs, groups, query, top = 4) {
  if (!query.trim() || query.length > 2000) throw new Error('Query must contain 1..2000 characters');
  const allowed = docs.filter(d => d.groups.some(g => groups.includes(g)));
  const bags = allowed.map(d => count(tokens(d.text)));
  const size = b => [...b.values()].reduce((a, x) => a + x, 0);
  const avg = bags.reduce((a, b) => a + size(b), 0) / Math.max(1, bags.length);
  const results = [];
  allowed.forEach((d, i) => {
    const bag = bags[i]; let score = 0;
    for (const term of new Set(tokens(query))) {
      const freq = bag.get(term) || 0, df = bags.filter(b => b.has(term)).length;
      const idf = Math.log(1 + (bags.length - df + 0.5) / (df + 0.5));
      score += idf * freq * 2.2 / (freq + 1.2 * (0.25 + 0.75 * size(bag) / Math.max(1, avg)));
    }
    if (score > 0) results.push({ document_id: d.id, title: d.title, text: d.text, score: Math.round(score * 1e6) / 1e6 });
  });
  results.sort((a, b) => b.score - a.score || (a.document_id < b.document_id ? -1 : 1));
  return { allowed: allowed.map(d => d.id), hits: results.slice(0, top) };
}
