// A very small stand-in for the browser DOM, just enough to run AgentDesk's modules under Node.
// Tester-agent file (T-20261030-002-TST). No npm packages (DEC-022).
import { pathToFileURL } from "node:url";
import path from "node:path";

export const STATIC_JS = path.resolve(import.meta.dirname, "..", "..", "app", "static", "js");
let counter = 0;
export function moduleUrl(relative) {
  // A fresh copy of the module each time (so module-level state such as the CSRF token starts empty).
  return pathToFileURL(path.join(STATIC_JS, relative)).href + `?fresh=${++counter}`;
}

export class FakeNode {}
export class FakeText extends FakeNode {
  constructor(text) { super(); this.text = String(text); }
  get textContent() { return this.text; }
}
export class FakeElement extends FakeNode {
  constructor(tag) {
    super();
    this.tag = tag; this.attrs = {}; this.children = []; this.listeners = {};
    this.className = ""; this.dataset = {}; this.focused = false; this.value = "";
  }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  getAttribute(name) { return name in this.attrs ? this.attrs[name] : null; }
  removeAttribute(name) { delete this.attrs[name]; }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...nodes) { this.children = nodes; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  focus() { this.focused = true; }
  set textContent(value) { this.children = [new FakeText(value)]; }
  get textContent() { return this.children.map((child) => child.textContent).join(""); }
  descendants() {
    const out = [];
    for (const child of this.children) {
      if (child instanceof FakeElement) { out.push(child, ...child.descendants()); }
    }
    return out;
  }
  querySelector(selector) {
    if (selector.startsWith(".")) return this.descendants().find((e) => e.className.split(" ").includes(selector.slice(1))) ?? null;
    return this.descendants().find((e) => e.tag === selector) ?? null;
  }
  querySelectorAll(selector) {
    if (selector === "a[href^='#/']") return this.descendants().filter((e) => e.tag === "a" && (e.attrs.href ?? "").startsWith("#/"));
    return this.descendants().filter((e) => e.tag === selector);
  }
}

export function installDom() {
  const created = [];
  const elementsById = {};
  const windowListeners = {};
  const store = new Map();
  const win = {
    location: {
      hash: "",
      replace(url) { this.hash = url.replace(/^.*#/, "#"); (windowListeners.hashchange || []).forEach((fn) => fn()); },
    },
    addEventListener(type, fn) { (windowListeners[type] ||= []).push(fn); },
    setTimeout: (fn, ms) => setTimeout(fn, ms),
    clearTimeout: (id) => clearTimeout(id),
    localStorage: {
      throwOnGet: false, throwOnSet: false,
      getItem(key) { if (this.throwOnGet) throw new Error("denied"); return store.has(key) ? store.get(key) : null; },
      setItem(key, value) { if (this.throwOnSet) throw new Error("denied"); store.set(key, String(value)); },
    },
  };
  const doc = {
    title: "", visibilityState: "visible",
    documentElement: new FakeElement("html"),
    createElement(tag) { created.push(tag); return new FakeElement(tag); },
    createTextNode(text) { return new FakeText(text); },
    getElementById(id) { return elementsById[id] ?? null; },
    addEventListener() {},
  };
  globalThis.window = win;
  globalThis.document = doc;
  globalThis.Node = FakeNode;
  return { window: win, document: doc, created, elementsById, windowListeners, store };
}

// A fake fetch. handler(path, options, calls) returns { status, json, notJson? } or throws.
export function installFetch(handler) {
  const calls = [];
  globalThis.fetch = async (path, options = {}) => {
    calls.push({ path, method: options.method ?? "GET", headers: options.headers ?? {}, body: options.body, options });
    const result = await handler(path, options, calls);
    return {
      ok: result.status >= 200 && result.status < 300,
      status: result.status,
      json: async () => { if (result.notJson) throw new SyntaxError("not json"); return result.json; },
    };
  };
  return calls;
}

export const tick = () => new Promise((resolve) => setTimeout(resolve, 0));
export async function settle(times = 6) { for (let i = 0; i < times; i += 1) await tick(); }
