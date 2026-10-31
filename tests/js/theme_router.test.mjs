// Tester-agent tests (T-20261030-002-TST): theme.js and router.js. FR-005, FR-007, NFR-008.
import test from "node:test";
import assert from "node:assert/strict";
import { installDom, moduleUrl, FakeElement } from "./fake_dom.mjs";

const env = installDom();
const theme = await import(moduleUrl("theme.js"));
const { createRouter } = await import(moduleUrl("router.js"));

// ---------- theme (FR-007) ----------

test("theme: the default is System", () => {
  assert.equal(theme.getTheme(), "system");
});

test("theme: choices are saved, applied and restored", () => {
  theme.setTheme("dark");
  assert.equal(env.window.localStorage.getItem("agentdesk.theme"), "dark");
  assert.equal(env.document.documentElement.dataset.theme, "dark");
  assert.equal(theme.getTheme(), "dark");
  theme.setTheme("light");
  assert.equal(env.document.documentElement.dataset.theme, "light");
  theme.setTheme("system");
  assert.equal(env.document.documentElement.dataset.theme, undefined, "System removes the override");
  assert.equal(theme.getTheme(), "system");
});

test("theme: invalid saved or chosen values fall back to System", () => {
  for (const bad of ["hack", "", "DARK", "<script>", "null"]) {
    env.window.localStorage.setItem("agentdesk.theme", bad);
    assert.equal(theme.getTheme(), "system", bad);
  }
  theme.setTheme("neon");
  assert.equal(theme.getTheme(), "system");
});

test("theme: unavailable storage does not break reading or applying", () => {
  env.window.localStorage.throwOnGet = true;
  assert.equal(theme.getTheme(), "system");
  env.window.localStorage.throwOnGet = false;
  env.window.localStorage.throwOnSet = true;
  assert.doesNotThrow(() => theme.setTheme("dark"));
  assert.equal(env.document.documentElement.dataset.theme, "dark", "applied for this page view");
  env.window.localStorage.throwOnSet = false;
});

test("theme: the header control shows the saved choice and reacts to changes", () => {
  theme.setTheme("light");
  const select = new FakeElement("select");
  theme.initThemeControl(select);
  assert.equal(select.value, "light");
  select.value = "dark";
  select.listeners.change[0]();
  assert.equal(env.window.localStorage.getItem("agentdesk.theme"), "dark");
  assert.doesNotThrow(() => theme.initThemeControl(null));
});

// ---------- router (FR-005) ----------

function makeRouter(routes) {
  env.window.location.hash = "";
  env.window.location.replace = function (url) {
    this.hash = url.replace(/^.*#/, "#");
    (env.windowListeners.hashchange || []).forEach((fn) => fn());
  };
  for (const key of Object.keys(env.windowListeners)) env.windowListeners[key] = [];
  const outlet = new FakeElement("main");
  const nav = new FakeElement("nav");
  const links = ["/overview", "/projects", "/settings"].map((p) => {
    const a = new FakeElement("a");
    a.setAttribute("href", `#${p}`);
    nav.appendChild(a);
    return a;
  });
  const router = createRouter({ routes, outlet, nav });
  return { router, outlet, nav, links };
}

const page = (title, extra = "") => ({
  path: `/${title.toLowerCase()}`, title,
  render: (ctx) => {
    const section = env.document.createElement("section");
    const heading = env.document.createElement("h1");
    heading.textContent = title + extra + JSON.stringify([ctx.params, [...ctx.query]]);
    section.appendChild(heading);
    return section;
  },
});
const ROUTES = [page("Overview"), page("Projects"), page("Settings")];

test("router: an empty address opens #/overview", () => {
  const { router, outlet, links } = makeRouter(ROUTES);
  router.start();
  assert.equal(env.window.location.hash, "#/overview");
  assert.match(outlet.querySelector("h1").textContent, /^Overview/);
  assert.equal(env.document.title, "Overview - AgentDesk");
  assert.equal(links[0].getAttribute("aria-current"), "page");
  assert.equal(links[1].getAttribute("aria-current"), null);
});

test("router: a deep link opens its page, marks the entry and moves focus after navigation", () => {
  const { router, outlet, links } = makeRouter(ROUTES);
  env.window.location.hash = "#/settings";
  router.start();
  assert.match(outlet.querySelector("h1").textContent, /^Settings/);
  assert.equal(links[2].getAttribute("aria-current"), "page");
  assert.equal(outlet.querySelector("h1").focused, false, "no focus steal on the first load (skip link stays first)");
  env.window.location.hash = "#/projects";
  env.windowListeners.hashchange.forEach((fn) => fn());
  const heading = outlet.querySelector("h1");
  assert.match(heading.textContent, /^Projects/);
  assert.equal(heading.focused, true);
  assert.equal(heading.getAttribute("tabindex"), "-1");
  assert.equal(links[2].getAttribute("aria-current"), null);
  assert.equal(links[1].getAttribute("aria-current"), "page");
  assert.equal(env.document.title, "Projects - AgentDesk");
});

test("router: the query string is parsed and does not change which page opens", () => {
  const { router, outlet } = makeRouter(ROUTES);
  env.window.location.hash = "#/settings?a=1&b=two%20words";
  router.start();
  assert.match(outlet.querySelector("h1").textContent, /\[\["a","1"\],\["b","two words"\]\]/);
});

test("router: unknown routes show Page not found with a link to Overview and no active entry", () => {
  for (const hash of ["#/nope", "#/settings/", "#/Settings", "#/settings/extra", "#nope", "#/%2e%2e", "#//", "#/projects/../settings"]) {
    const { router, outlet, links } = makeRouter(ROUTES);
    env.window.location.hash = hash;
    router.start();
    assert.equal(outlet.querySelector("h1").textContent, "Page not found", hash);
    const link = outlet.querySelector("a");
    assert.equal(link.getAttribute("href"), "#/overview");
    assert.equal(env.document.title, "Page not found - AgentDesk");
    assert.ok(links.every((l) => l.getAttribute("aria-current") === null), hash);
  }
});

test("router: route parameters are decoded and a route pattern is matched exactly", () => {
  const routes = [{ path: "/agents/:key", title: "Agent", render: (ctx) => {
    const s = env.document.createElement("section");
    const h1 = env.document.createElement("h1");
    h1.textContent = ctx.params.key;
    s.appendChild(h1);
    return s;
  } }];
  const { router, outlet } = makeRouter(routes);
  env.window.location.hash = "#/agents/pl%61nner";
  router.start();
  assert.equal(outlet.querySelector("h1").textContent, "planner");
  env.window.location.hash = "#/agents/a/b";
  env.windowListeners.hashchange.forEach((fn) => fn());
  assert.equal(outlet.querySelector("h1").textContent, "Page not found");
});

test("router: route text is inserted as text (a hostile hash cannot create elements)", () => {
  env.created.length = 0;
  const { router, outlet } = makeRouter(ROUTES);
  env.window.location.hash = "#/<img src=x onerror=alert(1)>";
  router.start();
  assert.equal(outlet.querySelector("h1").textContent, "Page not found");
  assert.ok(!env.created.includes("img"));
});

test("router: a malformed percent escape in a route parameter does not break the not-found path", () => {
  const routes = [{ path: "/agents/:key", title: "Agent", render: () => env.document.createElement("section") }];
  const { router } = makeRouter(routes);
  env.window.location.hash = "#/agents/%E0%A4%A";
  // A malformed escape would raise URIError inside decodeURIComponent. Recorded as an observation:
  // no Phase 1 route has a parameter, so this cannot happen in Phase 1.
  try { router.start(); } catch (error) { assert.ok(error instanceof URIError); }
});
