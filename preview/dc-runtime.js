/* Minimal runtime for Claude Design .dc.html components (preview and Webflow builds).
 *
 * Options read from window before this script runs:
 *   DC_SOURCES     {name: source}  component sources as strings (otherwise read from
 *                  <script type="text/plain" id="dc-src-NAME">)
 *   DC_BLOBS       {id: file}      asset map for /_blob/<id> paths built at runtime
 *   DC_ASSET_BASE  string          URL prefix for asset files (default '../assets/')
 *   DC_NO_HELMET   bool            do not copy <helmet> (fonts, CSS) into <head>
 */
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
    let raw = window.DC_SOURCES && window.DC_SOURCES[name];
    if (raw == null) {
      const el = document.getElementById('dc-src-' + name);
      if (!el) throw new Error('Missing component source: ' + name);
      raw = el.textContent.replace(/<\\\/script/g, '</script');
    }
    const doc = new DOMParser().parseFromString(raw, 'text/html');
    const root = doc.querySelector('x-dc');
    const helmet = root.querySelector('helmet');
    if (helmet) {
      if (!window.DC_NO_HELMET) {
        for (const c of Array.from(helmet.children)) document.head.appendChild(document.importNode(c, true));
      }
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

  // shareKey: mounts that render parts of one page pass the same key, so they share
  // one component instance (and its state) instead of one instance per props value.
  function renderComponent(name, props, ctx, out, shareKey) {
    const src = load(name);
    const key = shareKey || name + JSON.stringify(props);
    let inst = ctx.instances[key];
    if (!inst) inst = ctx.instances[key] = new src.Cls(props);
    inst.props = props;
    const vals = inst.renderVals() || {};
    return renderChildren(src.root, vals, ctx, out);
  }

  function dispatch(e) { const fn = this.__dcOn && this.__dcOn[e.type]; if (fn) return fn(e); }

  // Patch the live DOM in place instead of replacing it, so CSS transitions
  // (e.g. the FAQ accordion) run, images are not reloaded on every state change,
  // and server-rendered HTML is taken over without being rebuilt.
  function sameKind(a, b) {
    if (a.nodeType !== b.nodeType) return false;
    if (a.nodeType !== 1) return true;
    return a.namespaceURI === b.namespaceURI && a.tagName === b.tagName;
  }
  function morphChildren(parent, next) {
    const cur = Array.from(parent.childNodes).filter(n => n.nodeType === 1 || n.nodeType === 3);
    next.forEach((n, i) => {
      const o = cur[i];
      if (!o) { parent.appendChild(n); return; }
      if (!sameKind(o, n)) { parent.replaceChild(n, o); return; }
      if (o.nodeType !== 1) { if (o.nodeValue !== n.nodeValue) o.nodeValue = n.nodeValue; return; }
      for (const a of Array.from(o.attributes)) if (!n.hasAttribute(a.name)) o.removeAttribute(a.name);
      for (const a of Array.from(n.attributes)) if (o.getAttribute(a.name) !== a.value) o.setAttribute(a.name, a.value);
      if (n.__dcOn) {
        for (const type in n.__dcOn) if (!(o.__dcOn && o.__dcOn[type])) o.addEventListener(type, dispatch);
      }
      o.__dcOn = n.__dcOn;
      // data-dc-keep: content filled in from outside (e.g. the language switcher) stays
      if (!o.hasAttribute('data-dc-keep')) morphChildren(o, Array.from(n.childNodes));
    });
    for (let i = next.length; i < cur.length; i++) cur[i].remove();
  }

  function assetUrl(id) {
    const f = window.DC_BLOBS && window.DC_BLOBS[id];
    if (!f) return null;
    return (window.DC_ASSET_BASE != null ? window.DC_ASSET_BASE : '../assets/') + f;
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
        if (typeof fn === 'function') {
          // Handlers live on el.__dcOn so a morph can swap them without re-binding.
          const type = a.name.slice(2).toLowerCase();
          el.__dcOn = el.__dcOn || {};
          el.__dcOn[type] = fn;
          el.addEventListener(type, dispatch);
        }
        continue;
      }
      let v = a.value.indexOf('{{') < 0 ? a.value : interp(a.value, scope);
      // Paths built at runtime ('/_blob/' + id) are not rewritten by the build, so map them here.
      if (v.indexOf('/_blob/') >= 0) v = v.replace(/\/_blob\/([0-9a-f]{32})/g, (m, id) => assetUrl(id) || m);
      if (a.namespaceURI) el.setAttributeNS(a.namespaceURI, a.name, v); else el.setAttribute(a.name, v);
    }
    const kids = renderChildren(node.localName === 'template' ? node.content : node, scope, ctx, []);
    for (const k of kids) el.appendChild(k);
    out.push(el);
  }

  const mounts = [];
  const ctx = { instances: {} };
  let pending = false;

  // A slice mount shows only children a..b of the component's root element, inside a
  // shallow copy of the root (same tag and attributes).
  function sliceOf(nodes, [a, b]) {
    const root = nodes.find(n => n.nodeType === 1);
    const shell = root.cloneNode(false);
    Array.from(root.children).slice(a, b + 1).forEach(c => shell.appendChild(c));
    return [shell];
  }

  function render() {
    pending = false;
    const y = window.scrollY;
    for (const m of mounts) {
      const nodes = renderComponent(m.name, m.props, ctx, [], m.shareKey);
      morphChildren(m.el, m.slice ? sliceOf(nodes, m.slice) : nodes);
    }
    if (Math.abs(window.scrollY - y) > 1) window.scrollTo(0, y);
  }
  // Batch setState calls from one event into one render. A microtask (not
  // requestAnimationFrame) so a page opened in a background tab still updates.
  function schedule() { if (!pending) { pending = true; queueMicrotask(render); } }

  // One component in one element.
  window.DCMount = function (el, name, props) {
    mounts.push({ el, name, props: props || {} });
    render();
  };

  // One page split over several elements (e.g. Webflow Embeds): each element with
  // data-dc-part="N" renders sections N..N (or data-dc-part="N-M" for N..M), all
  // sharing one component instance. Existing (prerendered) markup is patched in place.
  window.DCMountParts = function (name, selector) {
    document.querySelectorAll(selector || '[data-dc-part]').forEach(el => {
      const [from, to] = el.getAttribute('data-dc-part').split('-').map(Number);
      mounts.push({ el, name, props: { partFrom: from, partTo: to == null || isNaN(to) ? from : to }, shareKey: name + ':page' });
    });
    render();
  };

  // Same for a component without parts: each element with data-dc-slice="N-M" shows
  // children N..M of the component's root element; all share one instance.
  window.DCMountSlices = function (name, selector) {
    document.querySelectorAll(selector || '[data-dc-slice]').forEach(el => {
      const [a, b] = el.getAttribute('data-dc-slice').split('-').map(Number);
      mounts.push({ el, name, props: {}, shareKey: name + ':page', slice: [a, b == null || isNaN(b) ? a : b] });
    });
    render();
  };
})();
