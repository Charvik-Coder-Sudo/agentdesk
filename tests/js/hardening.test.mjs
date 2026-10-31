// Developer tests (T-20261030-002-DEV-2, TASK-097): DOM builder allow-list (SEC-009), formatBytes (O-4),
// malformed route escapes (O-5) and the header server status of app.js (FR-004). No npm packages.
import test from "node:test";
import assert from "node:assert/strict";
import { installDom, installFetch, moduleUrl, settle, FakeElement } from "./fake_dom.mjs";

const env = installDom();
const { h, formatBytes } = await import(moduleUrl("dom.js"));
const { createRouter } = await import(moduleUrl("router.js"));
// The fake DOM has no <main id="main">, so importing app.js does not start the page.
const app = await import(moduleUrl("app.js"));

// ---------- DOM builder (SEC-009) ----------

test("h: a string onclick is never set, and a function listener still works", () => {
  const node = h("div", { onclick: "alert(1)", ONMOUSEOVER: "alert(2)", onFocus: 5 });
  assert.equal(node.getAttribute("onclick"), null);
  assert.equal(node.getAttribute("ONMOUSEOVER"), null);
  assert.equal(node.getAttribute("onFocus"), null);
  assert.deepEqual(node.listeners, {});

  const clicked = [];
  const button = h("button", { onClick: () => clicked.push("yes") });
  button.listeners.click[0]();
  assert.deepEqual(clicked, ["yes"]);
});

test("h: srcdoc is refused in any letter case", () => {
  for (const name of ["srcdoc", "SRCDOC", "srcDoc"]) {
    assert.throws(() => h("iframe", { [name]: "<script>alert(1)</script>" }), /not allowed/, name);
  }
});

test("h: unknown attributes are refused, the ones the pages use are accepted", () => {
  assert.throws(() => h("div", { formtarget: "x" }), /not allowed/);
  assert.throws(() => h("div", { "xlink:actuate": "x" }), /not allowed/);
  const node = h("td", { class: "c", "data-label": "Name", scope: "col", tabindex: "-1", "aria-current": "page" });
  assert.equal(node.getAttribute("data-label"), "Name");
  assert.equal(node.getAttribute("aria-current"), "page");
});

test("h: dangerous URL schemes are refused in href and src", () => {
  const bad = ["javascript:alert(1)", "  JaVaScRiPt:x", "data:text/html,x", "vbscript:x", "java\tscript:x", "file:///C:/x", ""];
  for (const name of ["href", "src", "action", "formaction", "xlink:href"]) {
    for (const value of bad) {
      assert.throws(() => h("a", { [name]: value }), /only accepts/, `${name}=${JSON.stringify(value)}`);
    }
  }
});

test("h: AgentDesk addresses and http(s) addresses are accepted", () => {
  for (const value of ["#/settings", "/static/x", "./x", "../x", "?q=1", "https://example.org/", "HTTP://127.0.0.1:8765/"]) {
    assert.equal(h("a", { href: value }).getAttribute("href"), value);
  }
  assert.equal(h("img", { src: "/static/favicon.svg", alt: "" }).getAttribute("src"), "/static/favicon.svg");
});

// ---------- formatBytes (O-4) ----------

test("formatBytes: NaN, Infinity, negative and missing values are unknown", () => {
  for (const bad of [NaN, Infinity, -Infinity, -1, undefined]) assert.equal(formatBytes(bad), "unknown", String(bad));
  assert.equal(formatBytes(0), "0 bytes");
  assert.equal(formatBytes(2048), "2.0 KB");
});

// ---------- router (O-5) ----------

test("router: a malformed percent escape in a route parameter shows Page not found without an exception", () => {
  env.window.location.hash = "#/agents/%E0%A4%A";
  for (const key of Object.keys(env.windowListeners)) env.windowListeners[key] = [];
  const outlet = new FakeElement("main");
  const routes = [{ path: "/agents/:key", title: "Agent", render: () => h("section", {}, h("h1", {}, "Agent page")) }];
  const router = createRouter({ routes, outlet, nav: new FakeElement("nav") });
  assert.doesNotThrow(() => router.start());
  assert.equal(outlet.querySelector("h1").textContent, "Page not found");
  assert.equal(env.document.title, "Page not found - AgentDesk");
  env.window.location.hash = "#/agents/pl%61nner"; // a well-formed escape still opens the page
  env.windowListeners.hashchange.forEach((fn) => fn());
  assert.equal(outlet.querySelector("h1").textContent, "Agent page");
});

// ---------- header server status (FR-004) ----------

function statusElement() {
  const element = new FakeElement("p");
  const icon = new FakeElement("span");
  icon.className = "status-icon";
  const text = new FakeElement("span");
  text.className = "status-text";
  element.appendChild(icon);
  element.appendChild(text);
  element.dataset.state = "checking";
  env.elementsById["server-status"] = element;
  return { element, icon, text };
}

function fakeTimers() {
  const timers = [];
  env.window.setTimeout = (fn, ms) => {
    timers.push({ fn, ms });
    return timers.length;
  };
  env.window.clearTimeout = () => {};
  return timers;
}

const healthy = () => installFetch(async () => ({ status: 200, json: { status: "ok", version: "0.1.0", uptime: 1 } }));
const unreachable = () => installFetch(async () => { throw new TypeError("Failed to fetch"); });

test("status: Server unreachable after a failed poll, shown as icon and text", async () => {
  const { element, icon, text } = statusElement();
  fakeTimers();
  env.document.visibilityState = "visible";
  unreachable();
  await app.checkHealth();
  assert.equal(element.dataset.state, "down");
  assert.equal(icon.textContent, "✕");
  assert.equal(text.textContent, "Server unreachable");
});

test("status: Server OK after a successful poll, and the next poll is planned in 10 seconds", async () => {
  const { element, icon, text } = statusElement();
  const timers = fakeTimers();
  env.document.visibilityState = "visible";
  const calls = healthy();
  await app.healthLoop();
  assert.equal(element.dataset.state, "ok");
  assert.equal(icon.textContent, "✓");
  assert.equal(text.textContent, "Server OK");
  assert.equal(calls.length, 1);
  assert.equal(calls[0].path, "/api/v1/health");
  assert.ok(timers.some((t) => t.ms === app.HEALTH_TIMEOUT_MS), "the poll uses the short 4 second timeout");
  assert.ok(timers.some((t) => t.ms === app.HEALTH_INTERVAL_MS && t.fn === app.healthLoop), "next poll in 10 s");
});

test("status: the status changes back and forth without a page reload", async () => {
  const { element } = statusElement();
  fakeTimers();
  unreachable();
  await app.checkHealth();
  assert.equal(element.dataset.state, "down");
  healthy();
  await app.checkHealth();
  assert.equal(element.dataset.state, "ok");
});

test("status: no poll while the tab is hidden; a poll at once when it becomes visible", async () => {
  statusElement();
  const timers = fakeTimers();
  const listeners = {};
  env.document.addEventListener = (type, fn) => {
    listeners[type] = fn;
  };
  env.document.visibilityState = "hidden";
  env.document.hidden = true;
  const calls = healthy();
  app.startHealthPolling();
  await settle();
  assert.equal(calls.length, 0, "no health call while hidden");
  assert.ok(!timers.some((t) => t.ms === app.HEALTH_INTERVAL_MS), "no poll planned while hidden");

  env.document.visibilityState = "visible";
  env.document.hidden = false;
  listeners.visibilitychange();
  await settle();
  assert.equal(calls.length, 1, "checked at once when the tab became visible");
});

test("status: a poll that finishes while the tab is hidden plans no further poll", async () => {
  statusElement();
  const timers = fakeTimers();
  env.document.visibilityState = "hidden";
  healthy();
  await app.healthLoop();
  assert.ok(!timers.some((t) => t.ms === app.HEALTH_INTERVAL_MS));
  env.document.visibilityState = "visible";
});
