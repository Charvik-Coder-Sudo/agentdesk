// A small hash router: "#/settings", "#/agents/:key", with optional "?query=strings".
// It renders the matching page into <main>, sets the browser title, marks the active
// navigation entry with aria-current="page" and, after navigation, moves focus to the
// page heading so keyboard and screen-reader users start at the new content.

import { h } from "./dom.js";

const DEFAULT_PATH = "/overview";

function compile(pattern) {
  const names = [];
  const source = pattern
    .split("/")
    .map((part) => {
      if (part.startsWith(":")) {
        names.push(part.slice(1));
        return "([^/]+)";
      }
      return part.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    })
    .join("/");
  return { regex: new RegExp(`^${source}$`), names };
}

// decodeURIComponent throws on a malformed escape such as "%E0%A4%A"; return null instead.
function decodeParam(text) {
  try {
    return decodeURIComponent(text);
  } catch {
    return null;
  }
}

function parseHash(hash) {
  const raw = hash.replace(/^#/, "");
  const [path, query = ""] = raw.split("?");
  return { path: path || "/", query: new URLSearchParams(query) };
}

function notFoundView() {
  return h(
    "section",
    {},
    h("h1", { tabindex: "-1" }, "Page not found"),
    h("p", {}, "There is no page at this address."),
    h("p", {}, h("a", { href: "#/overview" }, "Go to Overview")),
  );
}

// routes: [{ path: "/settings", title: "Settings", nav: "/settings", render: (ctx) => Node }]
export function createRouter({ routes, outlet, nav }) {
  const compiled = routes.map((route) => ({ ...route, ...compile(route.path) }));
  let firstRender = true;

  function match(path) {
    for (const route of compiled) {
      const found = route.regex.exec(path);
      if (found) {
        const params = {};
        for (const [index, name] of route.names.entries()) {
          const value = decodeParam(found[index + 1]);
          if (value === null) return null; // a malformed "%" escape: show "Page not found"
          params[name] = value;
        }
        return { route, params };
      }
    }
    return null;
  }

  function markNavigation(navPath) {
    if (!nav) return;
    for (const link of nav.querySelectorAll("a[href^='#/']")) {
      if (link.getAttribute("href") === `#${navPath}`) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    }
  }

  function render() {
    const { path, query } = parseHash(window.location.hash);
    if (path === "/") {
      window.location.replace(`#${DEFAULT_PATH}`); // triggers hashchange -> render
      return;
    }

    const found = match(path);
    let view;
    let title;
    if (found) {
      title = found.route.title;
      view = found.route.render({ params: found.params, query });
      markNavigation(found.route.nav ?? found.route.path);
    } else {
      title = "Page not found";
      view = notFoundView();
      markNavigation(null);
    }

    document.title = `${title} - AgentDesk`;
    outlet.replaceChildren(view);

    // Move focus to the new heading, except on the first page load, so that the
    // "Skip to main content" link is still the first thing Tab reaches.
    if (!firstRender) {
      const heading = outlet.querySelector("h1");
      if (heading) {
        heading.setAttribute("tabindex", "-1");
        heading.focus();
      }
    }
    firstRender = false;
  }

  return {
    start() {
      window.addEventListener("hashchange", render);
      render();
    },
  };
}
