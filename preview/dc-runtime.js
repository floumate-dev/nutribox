/* Minimal runtime for Claude Design .dc.html components (preview build). */
(function () {
  'use strict';

  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(patch) { this.state = Object.assign({}, this.state, patch); schedule(); }
  }
  window.DCLogic = DCLogic;

  const sources = {};
  function load(name) {
    if (sources[name]) return sources[name];
    const el = document.getElementById('dc-src-' + name);
    if (!el) throw new Error('Missing component source: ' + name);
    const raw = el.textContent.replace(/<\\\/script/g, '</script');
    const doc = new DOMParser().parseFromString(raw, 'text/html');
    const root = doc.querySelector('x-dc');
    const helmet = root.querySelector('helmet');
    if (helmet) {
      for (const c of Array.from(helmet.children)) document.head.appendChild(document.importNode(c, true));
      helmet.remove();
    }
    const scr = doc.querySelector('script[type="text/x-dc"]');
    const Cls = new Function('DCLogic', scr.textContent + '\n;return Component;')(DCLogic);
    return (sources[name] = { root, Cls });
  }

  const EXPR = /\{\{\s*([^}]+?)\s*\}\}/g;
  const ONE = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/;

  function lookup(path, scope) {
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    let v = scope;
    for (const k of path.split('.')) { if (v == null) return undefined; v = v[k]; }
    return v;
  }
  function value(str, scope) {
    const m = ONE.exec(str);
    if (m) return lookup(m[1], scope);
    return interp(str, scope);
  }
  function interp(str, scope) {
    return str.replace(EXPR, (_, p) => { const v = lookup(p, scope); return v == null ? '' : String(v); });
  }
  const truthy = v => !!v && v !== 'false';
  const camel = s => s.replace(/-([a-z])/g, (_, c) => c.toUpperCase());

  function renderChildren(node, scope, ctx, out) {
    for (const c of Array.from(node.childNodes)) renderNode(c, scope, ctx, out);
    return out;
  }

  function renderComponent(name, props, ctx, out) {
    const src = load(name);
    const key = name + JSON.stringify(props);
    let inst = ctx.instances[key];
    if (!inst) inst = ctx.instances[key] = new src.Cls(props);
    inst.props = props;
    const vals = inst.renderVals() || {};
    return renderChildren(src.root, vals, ctx, out);
  }

  function renderNode(node, scope, ctx, out) {
    if (node.nodeType === 3) {
      out.push(document.createTextNode(node.nodeValue.indexOf('{{') < 0 ? node.nodeValue : interp(node.nodeValue, scope)));
      return;
    }
    if (node.nodeType !== 1) return;
    const tag = node.localName;
    if (tag === 'sc-for') {
      const list = value(node.getAttribute('list') || '', scope) || [];
      const as = node.getAttribute('as') || 'item';
      list.forEach((item, i) => {
        const s = Object.create(scope);
        s[as] = item; s.$index = i;
        renderChildren(node, s, ctx, out);
      });
      return;
    }
    if (tag === 'sc-if') {
      if (truthy(value(node.getAttribute('value') || '', scope))) renderChildren(node, scope, ctx, out);
      return;
    }
    if (tag === 'dc-import') {
      const props = {};
      for (const a of Array.from(node.attributes)) {
        if (a.name === 'name' || a.name.indexOf('hint-') === 0) continue;
        props[camel(a.name)] = value(a.value, scope);
      }
      renderComponent(node.getAttribute('name'), props, ctx, out);
      return;
    }
    const el = document.createElementNS(node.namespaceURI, node.tagName.indexOf(':') < 0 && node.namespaceURI === 'http://www.w3.org/1999/xhtml' ? tag : node.tagName);
    for (const a of Array.from(node.attributes)) {
      if (a.name.indexOf('hint-') === 0) continue;
      if (/^on[a-z]+$/i.test(a.name) && a.value.indexOf('{{') >= 0) {
        const fn = value(a.value, scope);
        if (typeof fn === 'function') el.addEventListener(a.name.slice(2).toLowerCase(), fn);
        continue;
      }
      let v = a.value.indexOf('{{') < 0 ? a.value : interp(a.value, scope);
      // Paths built at runtime ('/_blob/' + id) are not rewritten by the build, so map them here.
      if (v.indexOf('/_blob/') >= 0 && window.DC_BLOBS) {
        v = v.replace(/\/_blob\/([0-9a-f]{32})/g, (m, id) => window.DC_BLOBS[id] ? '../assets/' + window.DC_BLOBS[id] : m);
      }
      if (a.namespaceURI) el.setAttributeNS(a.namespaceURI, a.name, v); else el.setAttribute(a.name, v);
    }
    const kids = renderChildren(node.localName === 'template' ? node.content : node, scope, ctx, []);
    for (const k of kids) el.appendChild(k);
    out.push(el);
  }

  // Root render with scroll/focus preservation
  let mount = null, rootName = null, rootProps = null, pending = false;
  const ctx = { instances: {} };

  function pathOf(el) {
    const p = [];
    while (el && el !== mount) { p.unshift(Array.prototype.indexOf.call(el.parentNode.children, el)); el = el.parentNode; }
    return el === mount ? p : null;
  }
  function byPath(p) {
    let el = mount;
    for (const i of p) { if (!el || !el.children[i]) return null; el = el.children[i]; }
    return el;
  }

  function render() {
    pending = false;
    const scrolled = [];
    if (mount.firstChild) {
      mount.querySelectorAll('*').forEach(el => { if (el.scrollLeft > 0) scrolled.push([pathOf(el), el.scrollLeft]); });
    }
    const focusPath = document.activeElement && mount.contains(document.activeElement) ? pathOf(document.activeElement) : null;
    const y = window.scrollY;
    const nodes = renderComponent(rootName, rootProps, ctx, []);
    const frag = document.createDocumentFragment();
    nodes.forEach(n => frag.appendChild(n));
    mount.replaceChildren(frag);
    for (const [p, x] of scrolled) { const el = p && byPath(p); if (el) el.scrollLeft = x; }
    if (focusPath) { const el = byPath(focusPath); if (el && el.focus) el.focus({ preventScroll: true }); }
    if (Math.abs(window.scrollY - y) > 1) window.scrollTo(0, y);
  }
  function schedule() { if (!pending) { pending = true; requestAnimationFrame(render); } }

  window.DCMount = function (el, name, props) {
    mount = el; rootName = name; rootProps = props || {};
    render();
  };
})();
