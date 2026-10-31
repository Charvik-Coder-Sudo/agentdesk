// Tester-agent tests (T-20261030-002-TST): app/static/js/api.js. NFR-003 (client side), FR-009.
import test from "node:test";
import assert from "node:assert/strict";
import { installDom, installFetch, moduleUrl } from "./fake_dom.mjs";

installDom();
const SESSION = "/api/v1/session";
const BACKUPS = "/api/v1/system/backups";

function server({ tokens = ["token-A"], failCsrf = 0, postStatus = 201 } = {}) {
  let sessionCount = 0;
  let csrfFailures = failCsrf;
  return installFetch(async (path, options) => {
    if (path === SESSION) return { status: 200, json: { csrf_token: tokens[Math.min(sessionCount++, tokens.length - 1)] } };
    if (options.method === "POST") {
      if (csrfFailures > 0) {
        csrfFailures -= 1;
        return { status: 403, json: { error: { code: "csrf_token_invalid", message: "Reload the page." } } };
      }
      return { status: postStatus, json: postStatus === 201 ? { ok: true } : { error: { code: "backup_failed", message: "Disk full." } } };
    }
    return { status: 200, json: { hello: "world" } };
  });
}

test("GET sends no CSRF header and no body, and returns the JSON", async () => {
  const calls = server();
  const { api } = await import(moduleUrl("api.js"));
  assert.deepEqual(await api.get("/api/v1/health"), { hello: "world" });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].method, "GET");
  assert.equal(calls[0].headers["X-AgentDesk-CSRF"], undefined);
  assert.equal(calls[0].body, undefined);
  assert.equal(calls[0].options.credentials, "same-origin");
  assert.equal(calls[0].options.cache, "no-store");
});

test("POST fetches the token first, then sends it with a JSON content type", async () => {
  const calls = server();
  const { api } = await import(moduleUrl("api.js"));
  await api.post(BACKUPS, {});
  assert.deepEqual(calls.map((c) => [c.method, c.path]), [["GET", SESSION], ["POST", BACKUPS]]);
  assert.equal(calls[1].headers["X-AgentDesk-CSRF"], "token-A");
  assert.equal(calls[1].headers["Content-Type"], "application/json");
  assert.equal(calls[1].body, "{}");
});

test("the token is cached for later POSTs and a missing body becomes {}", async () => {
  const calls = server();
  const { api } = await import(moduleUrl("api.js"));
  await api.post(BACKUPS);
  await api.post(BACKUPS, {});
  assert.equal(calls.filter((c) => c.path === SESSION).length, 1);
  assert.equal(calls[1].body, "{}");
});

test("after a restart (CSRF 403) a new token is fetched and the request is retried exactly once", async () => {
  const calls = server({ tokens: ["old", "new"], failCsrf: 1 });
  const { api } = await import(moduleUrl("api.js"));
  const data = await api.post(BACKUPS, {});
  assert.deepEqual(data, { ok: true });
  assert.deepEqual(calls.map((c) => c.path), [SESSION, BACKUPS, SESSION, BACKUPS]);
  assert.equal(calls[1].headers["X-AgentDesk-CSRF"], "old");
  assert.equal(calls[3].headers["X-AgentDesk-CSRF"], "new");
});

test("a CSRF refusal that persists stops after one retry with the server's plain message", async () => {
  const calls = server({ failCsrf: 99 });
  const { api, ApiError } = await import(moduleUrl("api.js"));
  await assert.rejects(api.post(BACKUPS, {}), (error) => {
    assert.ok(error instanceof ApiError);
    assert.equal(error.status, 403);
    assert.equal(error.code, "csrf_token_invalid");
    assert.equal(error.message, "Reload the page.");
    return true;
  });
  assert.equal(calls.filter((c) => c.method === "POST").length, 2, "no endless retry loop");
});

test("other 403 codes (for example a refused Origin) are not retried", async () => {
  const calls = installFetch(async (path) =>
    path === SESSION
      ? { status: 200, json: { csrf_token: "t" } }
      : { status: 403, json: { error: { code: "origin_not_allowed", message: "Not from the page." } } });
  const { api } = await import(moduleUrl("api.js"));
  await assert.rejects(api.post(BACKUPS, {}), { code: "origin_not_allowed" });
  assert.equal(calls.filter((c) => c.method === "POST").length, 1);
});

test("a server error message is passed on and a body that is not JSON gets a generic message", async () => {
  server({ postStatus: 500 });
  let { api } = await import(moduleUrl("api.js"));
  await assert.rejects(api.post(BACKUPS, {}), { message: "Disk full.", code: "backup_failed", status: 500 });

  installFetch(async () => ({ status: 502, notJson: true }));
  ({ api } = await import(moduleUrl("api.js")));
  await assert.rejects(api.get("/api/v1/health"), { message: "The server answered with status 502.", code: "http_error" });
});

test("a network failure becomes a plain-language error and never leaks the raw message", async () => {
  installFetch(async () => { throw new TypeError("Failed to fetch: ECONNREFUSED 127.0.0.1:8765"); });
  const { api } = await import(moduleUrl("api.js"));
  await assert.rejects(api.get("/api/v1/health"), (error) => {
    assert.equal(error.code, "network");
    assert.match(error.message, /Cannot reach the AgentDesk server/);
    assert.doesNotMatch(error.message, /ECONNREFUSED/);
    return true;
  });
});

test("a request that does not answer is aborted after the timeout", async () => {
  installFetch((path, options) => new Promise((resolve, reject) => {
    options.signal.addEventListener("abort", () => { const e = new Error("aborted"); e.name = "AbortError"; reject(e); });
  }));
  const { api } = await import(moduleUrl("api.js"));
  await assert.rejects(api.get("/api/v1/health", { timeout: 30 }), { code: "timeout" });
});

test("success responses with an empty or non-JSON body return null rather than crashing", async () => {
  installFetch(async () => ({ status: 200, notJson: true }));
  const { api } = await import(moduleUrl("api.js"));
  assert.equal(await api.get("/x"), null);
});
