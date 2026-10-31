// Tester-agent tests (T-20261030-002-TST): app/static/js/dom.js. NFR-005, FR-008.
import test from "node:test";
import assert from "node:assert/strict";
import { installDom, moduleUrl, FakeText, FakeElement } from "./fake_dom.mjs";

const env = installDom();
const { h, formatBytes, formatDateTime, announce } = await import(moduleUrl("dom.js"));

test("formatBytes: boundaries and units", () => {
  assert.equal(formatBytes(0), "0 bytes");
  assert.equal(formatBytes(1), "1 bytes");
  assert.equal(formatBytes(1023), "1023 bytes");
  assert.equal(formatBytes(1024), "1.0 KB");
  assert.equal(formatBytes(1536), "1.5 KB");
  assert.equal(formatBytes(1024 * 1024 - 1), "1024.0 KB");
  assert.equal(formatBytes(1024 * 1024), "1.0 MB");
  assert.equal(formatBytes(1024 ** 3), "1.0 GB");
  assert.equal(formatBytes(1024 ** 4), "1024.0 GB");
  assert.equal(formatBytes(16384), "16.0 KB");
});

test("formatBytes: invalid input is shown as unknown", () => {
  for (const bad of [-1, "5", null, undefined, {}, [], true]) assert.equal(formatBytes(bad), "unknown");
});

test("formatDateTime: empty, invalid and valid values", () => {
  assert.equal(formatDateTime(null), "unknown");
  assert.equal(formatDateTime(""), "unknown");
  assert.equal(formatDateTime(undefined), "unknown");
  assert.equal(formatDateTime("garbage"), "garbage");
  const shown = formatDateTime("2026-10-30T13:35:12.000Z");
  assert.match(shown, /2026|26/);
  assert.notEqual(shown, "Invalid Date");
});

test("h: data is always inserted as a text node, never parsed as HTML", () => {
  env.created.length = 0;
  const payload = '<img src=x onerror="alert(1)"><script>alert(2)</script>';
  const node = h("p", {}, payload, 42, null, false, undefined, [h("b", {}, payload)]);
  assert.deepEqual([...env.created].sort(), ["b", "p"], "only the requested elements are created");
  assert.ok(node.children[0] instanceof FakeText);
  assert.equal(node.children[0].textContent, payload);
  assert.equal(node.children[1].textContent, "42");
  assert.equal(node.children.length, 3);
  assert.equal(node.children[2].children[0].textContent, payload);
});

test("h: style and any html attribute are refused", () => {
  for (const name of ["style", "innerHTML", "outerHTML", "dangerouslySetInnerHTML", "innerhtml", "HTML"]) {
    assert.throws(() => h("div", { [name]: "x" }), /not allowed/, name);
  }
});

test("h: attribute handling", () => {
  const clicked = [];
  const node = h("button", { class: "button x", disabled: true, hidden: false, title: null, "data-label": 5, onClick: () => clicked.push(1) });
  assert.equal(node.className, "button x");
  assert.equal(node.getAttribute("disabled"), "");
  assert.equal(node.getAttribute("hidden"), null);
  assert.equal(node.getAttribute("title"), null);
  assert.equal(node.getAttribute("data-label"), "5");
  node.listeners.click[0]();
  assert.deepEqual(clicked, [1]);
  assert.doesNotThrow(() => h("div", null));
});

test("h: an onXxx attribute with a string value is a plain attribute, not code", () => {
  const node = h("div", { onclick: "alert(1)" });
  assert.equal(node.listeners.click, undefined);
});

test("announce: writes to the live region after a short delay and tolerates a missing region", async () => {
  announce("nothing there");
  const region = new FakeElement("div");
  env.elementsById.announcer = region;
  announce("Backup created");
  assert.equal(region.textContent, "");
  await new Promise((resolve) => setTimeout(resolve, 120));
  assert.equal(region.textContent, "Backup created");
});
