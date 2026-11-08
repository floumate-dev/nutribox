// Minimal stand-in for the Design Component runtime, only to measure section heights.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const file = process.argv[2];
const widths = (process.argv[3] || '1440,390').split(',').map(Number);
const shot = process.argv[4] || '';
const src = fs.readFileSync(file, 'utf8');
const tpl = src.slice(src.indexOf('<x-dc>') + 6, src.indexOf('</x-dc>'));
const helmet = tpl.slice(tpl.indexOf('<helmet>') + 8, tpl.indexOf('</helmet>')).replace(/<link[^>]*>/g, '').replace(/\/_blob\//g, 'blob/');
const body = tpl.slice(tpl.indexOf('</helmet>') + 9).replace(/\/_blob\//g, 'blob/').replace(/loading="lazy"/g, '');
const script = src.slice(src.indexOf('<script type="text/x-dc"'));
const code = script.slice(script.indexOf('>') + 1, script.indexOf('</script>'));
const fontDir = path.join(__dirname, 'package/files');
const f1 = fs.readFileSync(path.join(fontDir, 'outfit-latin-wght-normal.woff2')).toString('base64');
const f2 = fs.readFileSync(path.join(fontDir, 'outfit-latin-ext-wght-normal.woff2')).toString('base64');

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Outfit';src:url(data:font/woff2;base64,${f1}) format('woff2');font-weight:100 900;unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2600-26FF}
@font-face{font-family:'Outfit';src:url(data:font/woff2;base64,${f2}) format('woff2');font-weight:100 900;unicode-range:U+0100-024F,U+1E00-1EFF}
</style>${helmet}</head><body><template id="t">${body}</template><div id="root"></div>
<script>
class DCLogic { constructor(p){ this.props = p || {}; } setState(s){ this.state = Object.assign({}, this.state, s); } }
${code}
function look(path, scope){ path = path.trim(); if (path==='true') return true; if (path==='false') return false; if (/^-?\\d+(\\.\\d+)?$/.test(path)) return Number(path);
  let v = scope; for (const k of path.split('.')) { if (v == null) return undefined; v = v[k]; } return v; }
function interp(str, scope){ return str.replace(/\\{\\{([^}]+)\\}\\}/g, (_, p) => { const v = look(p, scope); return v == null ? '' : String(v); }); }
function render(node, scope, out){
  for (const n of [...node.childNodes]) {
    if (n.nodeType === 3) { out.appendChild(document.createTextNode(interp(n.nodeValue, scope))); continue; }
    if (n.nodeType !== 1) continue;
    const tag = n.tagName.toLowerCase();
    if (tag === 'sc-for') { const list = look(n.getAttribute('list').replace(/[{}]/g,''), scope) || []; const as = n.getAttribute('as');
      list.forEach((it, i) => render(n, Object.assign(Object.create(scope), {[as]: it, $index: i}), out)); continue; }
    if (tag === 'sc-if') { if (look(n.getAttribute('value').replace(/[{}]/g,''), scope)) render(n, scope, out); continue; }
    const el = document.createElementNS(n.namespaceURI, n.localName);
    for (const a of n.attributes) { if (/^on[A-Z]/.test(a.name) || /^on[a-z]+$/.test(a.name)) continue; el.setAttribute(a.name, interp(a.value, scope)); }
    render(n.content || n, scope, el); out.appendChild(el);
  }
}
window.run = (props) => { const c = new Component(props || {}); const vals = c.renderVals(); const root = document.getElementById('root'); root.innerHTML='';
  render(document.getElementById('t').content, vals, root); };
</script></body></html>`;
fs.writeFileSync(path.join(__dirname, 'page.html'), html);

(async () => {
  const browser = await chromium.launch();
  for (const w of widths) {
    const page = await browser.newPage({ viewport: { width: w, height: 900 } });
    await page.goto('file://' + path.join(__dirname, 'page.html'));
    await page.evaluate(() => run({ partFrom: 0, partTo: 16 })); await page.waitForTimeout(800);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    const r = await page.evaluate(() => {
      const root = document.getElementById('root').firstElementChild;
      const kids = [...root.children].map(e => ({ tag: e.tagName, h: Math.round(e.getBoundingClientRect().height), top: Math.round(e.getBoundingClientRect().top + scrollY), label: (e.id || e.className || e.textContent.trim().slice(0, 28)) }));
      return { total: document.documentElement.scrollHeight, kids };
    });
    console.log('WIDTH', w, 'TOTAL', r.total);
    r.kids.forEach((k, i) => console.log(String(i).padStart(2), k.tag.padEnd(7), String(k.top).padStart(6), String(k.h).padStart(6), k.label));
    if (shot) await page.screenshot({ path: shot.replace('.png', '-' + w + '.png'), fullPage: true });
    await page.close();
  }
  await browser.close();
})();
