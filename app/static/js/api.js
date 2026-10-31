// Fetch wrapper for the AgentDesk API.
// - JSON in and out, 10 second timeout (configurable per call).
// - State-changing requests send the CSRF token in the X-AgentDesk-CSRF header. The token comes
//   from GET /api/v1/session. After a server restart the old token is refused, so on a CSRF 403
//   the token is fetched again and the request is retried once.
// - Every failure becomes an ApiError with a plain-language message.

const DEFAULT_TIMEOUT_MS = 10000;
let csrfToken = null;

export class ApiError extends Error {
  constructor(message, { status = 0, code = "error" } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function getCsrfToken() {
  if (!csrfToken) {
    const data = await request("GET", "/api/v1/session");
    csrfToken = data.csrf_token;
  }
  return csrfToken;
}

async function request(method, path, body, { timeout = DEFAULT_TIMEOUT_MS, retry = true } = {}) {
  const stateChanging = !["GET", "HEAD"].includes(method);
  const headers = { Accept: "application/json" };
  if (stateChanging) {
    headers["Content-Type"] = "application/json";
    headers["X-AgentDesk-CSRF"] = await getCsrfToken();
  }

  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeout);
  let response;
  let data = null;
  try {
    response = await fetch(path, {
      method,
      headers,
      body: stateChanging ? JSON.stringify(body ?? {}) : undefined,
      signal: controller.signal,
      credentials: "same-origin",
      cache: "no-store",
    });
    try {
      data = await response.json();
    } catch {
      data = null; // not JSON; handled below
    }
  } catch (error) {
    if (error.name === "AbortError") {
      throw new ApiError(`The server did not answer within ${Math.round(timeout / 1000)} seconds.`, { code: "timeout" });
    }
    throw new ApiError("Cannot reach the AgentDesk server. Check that it is still running.", { code: "network" });
  } finally {
    window.clearTimeout(timer);
  }

  if (!response.ok) {
    const code = data?.error?.code ?? "http_error";
    if (stateChanging && response.status === 403 && code === "csrf_token_invalid" && retry) {
      csrfToken = null; // probably a server restart: get a fresh token and try once more
      return request(method, path, body, { timeout, retry: false });
    }
    const message = data?.error?.message ?? `The server answered with status ${response.status}.`;
    throw new ApiError(message, { status: response.status, code });
  }
  return data;
}

export const api = {
  get: (path, options) => request("GET", path, undefined, options),
  post: (path, body, options) => request("POST", path, body, options),
};
