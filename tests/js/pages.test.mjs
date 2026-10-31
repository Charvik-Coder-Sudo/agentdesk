// Tester-agent tests (T-20261030-002-TST): placeholder.js and settings.js. FR-006, FR-008, FR-009, NFR-005.
import test from "node:test";
import assert from "node:assert/strict";
import { installDom, installFetch, moduleUrl, settle, FakeElement } from "./fake_dom.mjs";

const env = installDom();
const { placeholderRoutes } = await import(moduleUrl("pages/placeholder.js"));

test("placeholder: ten pages, each with title, purpose, phase and no data elements", () => {
  assert.deepEqual(placeholderRoutes.map((r) => r.path), [
    "/overview", "/projects", "/agents", "/activity", "/files", "/reports", "/documents", "/testing", "/security", "/approvals",
  ]);
  for (const route of placeholderRoutes) {
    env.created.length = 0;
    const view = route.render({ params: {}, query: new URLSearchParams() });
    assert.equal(view.querySelector("h1").textContent, route.title);
    const text = view.textContent;
    assert.match(text, /Placeholder/);
    assert.match(text, /Arrives in Phase [1-6]/);
    assert.match(text, /shows no data/);
    assert.ok(env.created.every((tag) => ["section", "h1", "p", "div"].includes(tag)), route.path + " " + env.created);
  }
});

// ---------- Settings ----------

const SYSTEM = {
  version: "0.1.0", python_version: "3.15.2", sqlite_version: "3.50.0",
  data_dir: "D:\\agentdesk\\data", database_path: "D:\\agentdesk\\data\\agentdesk.db", database_size_bytes: 16384,
  schema_version: 1, migrations: [{ version: 1, name: "foundation", applied_at: "2026-10-31T07:00:00.000Z" }],
  last_backup: { name: "agentdesk-20261031-070000-startup.db", reason: "startup", created_at: "2026-10-31T07:00:00.000Z", size_bytes: 16384 },
  integrity: { result: "ok", check: "quick_check", checked_at: "2026-10-31T07:00:00.000Z" },
  instance_id: "abc123", created_at: "2026-10-31T07:00:00.000Z", backup_warning: null,
};
const BACKUPS = { backups: [SYSTEM.last_backup] };

function backend(overrides = {}) {
  let backups = overrides.backups ?? BACKUPS;
  return installFetch(async (path, options) => {
    if (overrides.down) throw new TypeError("down");
    if (path === "/api/v1/session") return { status: 200, json: { csrf_token: "tok" } };
    if (path === "/api/v1/system") return { status: 200, json: overrides.system ?? SYSTEM };
    if (path === "/api/v1/system/backups" && options.method === "POST") {
      if (overrides.postFails) return { status: 500, json: { error: { code: "backup_failed", message: "The backup failed: disk full." } } };
      backups = { backups: [{ ...SYSTEM.last_backup, name: "agentdesk-20261031-080000-manual.db", reason: "manual" }, ...backups.backups] };
      return { status: 201, json: { backup: backups.backups[0], integrity: "ok", message: "Backup created: agentdesk-20261031-080000-manual.db" } };
    }
    if (path === "/api/v1/system/backups") return { status: 200, json: backups };
    return { status: 404, json: { error: { code: "not_found", message: "none" } } };
  });
}

async function open(overrides) {
  env.elementsById.announcer = new FakeElement("div");
  const calls = backend(overrides);
  const { renderSettings } = await import(moduleUrl("pages/settings.js"));
  env.created.length = 0;
  const view = renderSettings();
  await settle();
  return { view, calls };
}

const buttonOf = (view) => view.querySelectorAll("button").find((b) => b.textContent.startsWith("Create backup") || b.textContent.startsWith("Creating"));

test("settings: loads the system and backup endpoints and shows every FR-008 value", async () => {
  const { view, calls } = await open();
  assert.deepEqual(calls.filter((c) => c.method === "GET").map((c) => c.path).sort(), ["/api/v1/system", "/api/v1/system/backups"]);
  const text = view.textContent;
  for (const expected of ["0.1.0", "3.15.2", "3.50.0", "D:\\agentdesk\\data", "16.0 KB", "foundation", "abc123",
                          "OK (SQLite quick_check", "agentdesk-20261031-070000-startup.db", "startup", "Schema version"]) {
    assert.ok(text.includes(expected), "missing: " + expected);
  }
  assert.doesNotMatch(text, /owner|profile/i);
  assert.equal(view.querySelectorAll("table").length, 2);
});

test("settings: server data is only ever inserted as text", async () => {
  const hostile = '<img src=x onerror="alert(1)">';
  const system = { ...SYSTEM, instance_id: hostile, data_dir: hostile, backup_warning: hostile, version: hostile,
    migrations: [{ version: 1, name: hostile, applied_at: hostile }] };
  const { view } = await open({ system, backups: { backups: [{ ...SYSTEM.last_backup, name: hostile }] } });
  assert.ok(view.textContent.includes(hostile));
  assert.ok(!env.created.includes("img") && !env.created.includes("script"), "created: " + env.created);
});

test("settings: a warning from a failed startup backup is shown", async () => {
  const { view } = await open({ system: { ...SYSTEM, backup_warning: "The automatic startup backup failed: disk full" } });
  assert.match(view.textContent, /Warning: The automatic startup backup failed: disk full/);
});

test("settings: an integrity problem and an empty backup list are described in words", async () => {
  const system = { ...SYSTEM, last_backup: null, integrity: { result: "bad page", check: "quick_check", checked_at: SYSTEM.created_at } };
  const { view } = await open({ system, backups: { backups: [] } });
  assert.match(view.textContent, /Problem found: bad page/);
  assert.match(view.textContent, /No backup yet/);
  assert.match(view.textContent, /There are no backups yet\./);
});

test("settings: Create backup now sends a CSRF-protected POST, shows the result and refreshes the list", async () => {
  const { view, calls } = await open();
  const button = buttonOf(view);
  await button.listeners.click[0]();
  await settle();
  const post = calls.find((c) => c.method === "POST");
  assert.equal(post.path, "/api/v1/system/backups");
  assert.equal(post.headers["X-AgentDesk-CSRF"], "tok");
  assert.equal(post.headers["Content-Type"], "application/json");
  assert.match(view.textContent, /✓ Backup created: agentdesk-20261031-080000-manual\.db\. Integrity check: OK\./);
  assert.match(view.textContent, /agentdesk-20261031-080000-manual\.db/);
  assert.equal(buttonOf(view).textContent, "Create backup now");
  assert.equal(button.getAttribute("aria-disabled"), null);
  assert.ok(calls.filter((c) => c.method === "GET" && c.path === "/api/v1/system/backups").length >= 2, "list reloaded without a page reload");
});

test("settings: a second click while a backup is running does not send a second request", async () => {
  const { view, calls } = await open();
  const button = buttonOf(view);
  const first = button.listeners.click[0]();
  const second = button.listeners.click[0]();
  assert.equal(button.getAttribute("aria-disabled"), "true");
  assert.equal(button.textContent, "Creating backup...");
  await Promise.all([first, second]);
  await settle();
  assert.equal(calls.filter((c) => c.method === "POST").length, 1);
});

test("settings: a failed backup shows a plain error and re-enables the button", async () => {
  const { view } = await open({ postFails: true });
  const button = buttonOf(view);
  await button.listeners.click[0]();
  await settle();
  assert.match(view.textContent, /✕ The backup was not created\. The backup failed: disk full\./);
  assert.equal(button.textContent, "Create backup now");
  assert.equal(button.getAttribute("aria-disabled"), null);
});

test("settings: when the server is down the page offers Try again, which reloads", async () => {
  const { view, calls } = await open({ down: true });
  assert.match(view.textContent, /Could not load this information: Cannot reach the AgentDesk server/);
  const retry = view.querySelectorAll("button").find((b) => b.textContent === "Try again");
  assert.ok(retry);
  const before = calls.length;
  await retry.listeners.click[0]();
  await settle();
  assert.ok(calls.length > before);
});
