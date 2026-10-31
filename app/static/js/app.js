// AgentDesk boot: theme, skip link, router and the server status in the header.
// The server-status functions are exported so that Node tests can import this module (with a fake
// DOM that has no <main id="main">) without starting the whole page.

import { api } from "./api.js";
import { createRouter } from "./router.js";
import { initThemeControl } from "./theme.js";
import { placeholderRoutes } from "./pages/placeholder.js";
import { renderSettings } from "./pages/settings.js";

export const HEALTH_INTERVAL_MS = 10000;
export const HEALTH_TIMEOUT_MS = 4000; // short, so "Server unreachable" shows within about 10-15 seconds

// ---------- Server status (header) ----------
const STATUS = {
  checking: { icon: "…", text: "Checking server" },
  ok: { icon: "✓", text: "Server OK" },
  down: { icon: "✕", text: "Server unreachable" },
};
let healthTimer = null;

export function showServerStatus(state) {
  const element = document.getElementById("server-status");
  if (!element || element.dataset.state === state) return;
  element.dataset.state = state;
  element.querySelector(".status-icon").textContent = STATUS[state].icon;
  element.querySelector(".status-text").textContent = STATUS[state].text;
}

export async function checkHealth() {
  try {
    const data = await api.get("/api/v1/health", { timeout: HEALTH_TIMEOUT_MS });
    showServerStatus(data && data.status === "ok" ? "ok" : "down");
  } catch {
    showServerStatus("down");
  }
}

export async function healthLoop() {
  window.clearTimeout(healthTimer);
  await checkHealth();
  if (document.visibilityState === "visible") {
    healthTimer = window.setTimeout(healthLoop, HEALTH_INTERVAL_MS);
  }
}

// Only check while the tab is visible; check at once when it becomes visible again.
export function startHealthPolling() {
  document.addEventListener("visibilitychange", () => {
    window.clearTimeout(healthTimer);
    if (document.visibilityState === "visible") healthLoop();
  });
  if (document.visibilityState === "visible") healthLoop();
}

// ---------- Skip link ----------
// The page uses "#/..." addresses for navigation, so the skip link moves focus itself
// instead of changing the address to "#main".
function initSkipLink() {
  const link = document.getElementById("skip-link");
  const main = document.getElementById("main");
  if (!link || !main) return;
  link.addEventListener("click", (event) => {
    event.preventDefault();
    main.focus();
  });
}

// ---------- Boot ----------
function boot() {
  initThemeControl(document.getElementById("theme-select"));
  initSkipLink();
  const routes = [
    ...placeholderRoutes,
    { path: "/settings", title: "Settings", render: renderSettings },
  ];
  createRouter({
    routes,
    outlet: document.getElementById("main"),
    nav: document.querySelector(".app-nav"),
  }).start();
  startHealthPolling();
}

// Start only on the AgentDesk page itself, which always has <main id="main"> (module scripts run
// after the page has been parsed). Node tests import this module without that element.
if (typeof document !== "undefined" && document.getElementById("main")) boot();
