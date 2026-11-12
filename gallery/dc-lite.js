/*! dc-lite: a tiny renderer for single-file design boards.
 * Supports {{ path }} holes, <sc-for list as>, <sc-if value>, onX="{{ fn }}" handlers,
 * ref="{{ fn | {current} }}" and a DCLogic class with state, setState and lifecycle hooks.
 * MIT licence, Vlad Yasinski. Uses morphdom (MIT) for in-place DOM updates.
 */
(function () {
  "use strict";
  var HOLE = /\{\{\s*([^}]*?)\s*\}\}/g;
  var WHOLE = /^\{\{\s*([^}]*?)\s*\}\}$/;

  function lookup(expr, scope) {
    if (expr === "true") return true;
    if (expr === "false") return false;
    if (expr === "null") return null;
    if (expr === "undefined" || expr === "") return undefined;
    if (/^-?\d+(\.\d+)?$/.test(expr)) return Number(expr);
    if (/^(['"]).*\1$/.test(expr)) return expr.slice(1, -1);
    var parts = expr.split("."), v = scope;
    for (var i = 0; i < parts.length; i++) {
      if (v == null) return undefined;
      v = v[parts[i]];
    }
    return v;
  }
  function interp(str, scope) {
    return str.replace(HOLE, function (_, e) {
      var v = lookup(e, scope);
      return v == null || v === false ? "" : String(v);
    });
  }

  function DCLogic(props) { this.props = props || {}; this.state = {}; }
  DCLogic.prototype.setState = function (u, cb) {
    var patch = typeof u === "function" ? u(this.state, this.props) : u;
    if (patch) this.state = Object.assign({}, this.state, patch);
    this.__host && this.__host.schedule(cb);
  };
  DCLogic.prototype.forceUpdate = function (cb) { this.__host && this.__host.schedule(cb); };
  window.DCLogic = DCLogic;
  if (!window.React) window.React = { createRef: function () { return { current: null }; } };

  function Host(container, tpl, Comp, props) {
    this.container = container;
    this.tpl = tpl;
    this.events = {};
    this.handlers = [];
    this.refs = [];
    this.pending = false;
    this.cbs = [];
    var c = new Comp(props);
    c.props = props;
    if (!c.state) c.state = {};
    c.__host = this;
    this.c = c;
  }
  Host.prototype.schedule = function (cb) {
    if (cb) this.cbs.push(cb);
    if (this.pending || !this.mounted) return;
    this.pending = true;
    var self = this;
    Promise.resolve().then(function () { self.pending = false; self.update(); });
  };
  Host.prototype.build = function () {
    this.handlers = [];
    this.refs = [];
    var vals = (this.c.renderVals && this.c.renderVals()) || {};
    var out = document.createElement("div");
    var nodes = this.walk(this.tpl.content.childNodes, vals);
    for (var i = 0; i < nodes.length; i++) out.appendChild(nodes[i]);
    return out;
  };
  Host.prototype.walk = function (list, scope) {
    var res = [];
    for (var i = 0; i < list.length; i++) {
      var n = list[i];
      if (n.nodeType === 3) {
        res.push(document.createTextNode(n.nodeValue.indexOf("{{") < 0 ? n.nodeValue : interp(n.nodeValue, scope)));
      } else if (n.nodeType === 1) {
        var tag = n.localName;
        if (tag === "sc-for") {
          var arr = lookup((WHOLE.exec(n.getAttribute("list") || "") || [])[1] || "", scope) || [];
          var as = n.getAttribute("as") || "item";
          for (var j = 0; j < arr.length; j++) {
            var s = Object.create(scope);
            s[as] = arr[j];
            s[as + "Index"] = j;
            res.push.apply(res, this.walk(n.childNodes, s));
          }
        } else if (tag === "sc-if") {
          var v = lookup((WHOLE.exec(n.getAttribute("value") || "") || [])[1] || "", scope);
          if (v) res.push.apply(res, this.walk(n.childNodes, scope));
        } else {
          res.push(this.el(n, scope));
        }
      }
    }
    return res;
  };
  Host.prototype.el = function (n, scope) {
    var el = document.importNode(n, false);
    var attrs = n.attributes;
    for (var i = 0; i < attrs.length; i++) {
      var a = attrs[i], val = a.value;
      if (val.indexOf("{{") < 0) continue;
      var m = WHOLE.exec(val);
      if (m) {
        var v = lookup(m[1], scope);
        if (a.name === "ref") {
          el.removeAttribute("ref");
          if (v) this.refs.push([this.handlers.length + ":" + this.refs.length, v]), el.setAttribute("data-dc-ref", String(this.refs.length - 1));
          continue;
        }
        if (/^on[a-z]/i.test(a.name) && a.name.length > 2) {
          el.removeAttribute(a.name);
          if (typeof v === "function") {
            var evt = a.name.slice(2).toLowerCase();
            this.handlers.push(v);
            el.setAttribute("data-dc-on-" + evt, String(this.handlers.length - 1));
            this.listen(evt);
          }
          continue;
        }
        if (v === false || v == null) el.removeAttribute(a.name);
        else el.setAttribute(a.name, String(v));
      } else {
        el.setAttribute(a.name, interp(val, scope));
      }
    }
    if (n.localName !== "template") {
      var kids = this.walk(n.childNodes, scope);
      for (var k = 0; k < kids.length; k++) el.appendChild(kids[k]);
    }
    return el;
  };
  Host.prototype.listen = function (evt) {
    if (this.events[evt]) return;
    this.events[evt] = true;
    var self = this, key = "data-dc-on-" + evt;
    this.container.addEventListener(evt, function (e) {
      var t = e.target;
      while (t && t !== self.container) {
        if (t.nodeType === 1 && t.hasAttribute(key)) {
          var h = self.handlers[+t.getAttribute(key)];
          if (h) h.call(self.c, e);
          return;
        }
        t = t.parentNode;
      }
    }, true);
  };
  Host.prototype.applyRefs = function () {
    var nodes = this.container.querySelectorAll("[data-dc-ref]");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i], r = this.refs[+el.getAttribute("data-dc-ref")];
      if (!r) continue;
      var fn = r[1];
      if (el.__dcRef === fn) continue;
      el.__dcRef = fn;
      if (typeof fn === "function") fn(el);
      else if (typeof fn === "object") fn.current = el;
    }
  };
  Host.prototype.mount = function () {
    var out = this.build();
    while (out.firstChild) this.container.appendChild(out.firstChild);
    mark(this.container);
    this.mounted = true;
    this.applyRefs();
    if (this.c.componentDidMount) this.c.componentDidMount();
  };
  Host.prototype.update = function () {
    var prevState = this.prevState || {};
    var out = this.build();
    window.morphdom(this.container, out, {
      childrenOnly: true,
      onBeforeElUpdated: function (from, to) {
        var html = to.outerHTML;
        if (from.__dcLast === html) return false;
        from.__dcLast = html;
        return true;
      },
      onNodeAdded: function (node) { if (node.nodeType === 1) mark(node); return node; }
    });
    this.applyRefs();
    if (this.c.componentDidUpdate) this.c.componentDidUpdate(this.c.props, prevState);
    this.prevState = this.c.state;
    var cbs = this.cbs; this.cbs = [];
    for (var i = 0; i < cbs.length; i++) cbs[i]();
  };
  function mark(root) {
    if (root.nodeType !== 1) return;
    root.__dcLast = root.outerHTML;
    var all = root.querySelectorAll("*");
    for (var i = 0; i < all.length; i++) all[i].__dcLast = all[i].outerHTML;
  }

  function boot() {
    var tpl = document.getElementById("dc-template");
    var script = document.querySelector('script[type="text/x-dc"]');
    var container = document.getElementById("dc-root");
    if (!tpl || !script || !container) return;
    var props = {};
    try {
      var decl = JSON.parse(script.getAttribute("data-props") || "{}");
      Object.keys(decl).forEach(function (k) { if (k.charAt(0) !== "$" && "default" in decl[k]) props[k] = decl[k]["default"]; });
    } catch (e) { /* no props */ }
    var Comp = new Function("DCLogic", script.textContent + "\n;return Component;")(DCLogic);
    var host = new Host(container, tpl, Comp, props);
    host.mount();
    window.__dcHost = host;
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
