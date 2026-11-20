import { retrieve } from './retrieve.js';
const $ = id => document.getElementById(id);
const docs = await (await fetch('assets/documents.json')).json();
const GROUPS = { finance: ['finance'], hr: ['hr'], both: ['finance', 'hr'], none: [] };
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const CHIPS = ['opleidingsbudget 7312', 'Wat is het opleidingsbudget?', 'factuur goedkeuring', 'AI-opleiding', 'afwijkend rekeningnummer'];
function run() {
  const groups = GROUPS[$('kb-who').value], q = $('kb-q').value;
  let r; try { r = retrieve(docs, groups, q); } catch (e) { $('kb-hits').textContent = e.message; return; }
  $('kb-docs').innerHTML = docs.map(d => { const ok = r.allowed.includes(d.id);
    return `<div class="kb-doc ${ok ? '' : 'no'}"><div><b>${esc(d.title)}</b> <span class="dim small mono">${d.id}</span></div><div class="small dim">groups: ${d.groups.join(', ')}</div><span class="pill ${ok ? 'ok' : 'bad'}">${ok ? 'readable' : 'removed before search'}</span></div>`; }).join('');
  $('kb-hits').innerHTML = r.hits.length ? r.hits.map(h => `<div class="kb-hit"><span class="mono">${h.score.toFixed(3)}</span><b>${esc(h.title)}</b></div>`).join('') : '<p class="small dim">No permitted document matches.</p>';
  $('kb-answer').innerHTML = r.hits.length ? r.hits.map(h => `<p>${esc(h.text)} <span class="mono dim small">[${h.document_id}]</span></p>`).join('')
    : '<p>Geen toegankelijke bron gevonden. Vraag een dossierbeheerder om hulp.</p><p class="small dim">Abstained: the same answer whether the information does not exist or you may not see it, so nothing leaks.</p>';
}
$('kb-chips').innerHTML = CHIPS.map(c => `<button type="button">${c}</button>`).join('');
$('kb-chips').addEventListener('click', e => { if (e.target.tagName === 'BUTTON') { $('kb-q').value = e.target.textContent; run(); } });
['kb-who', 'kb-q'].forEach(id => $(id).addEventListener('input', run));
run();
