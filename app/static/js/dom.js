// Small DOM helpers. Data is always inserted as text (textContent / text nodes), never as HTML.

// The attributes h() may set. This is an allow-list: any other attribute (for example style, or an
// attribute whose value the browser would treat as HTML) is refused with an error.
const ALLOWED_ATTRIBUTE =
  /^(?:aria-[a-z]+|data-[a-z0-9-]+|id|role|title|lang|dir|tabindex|hidden|type|name|value|for|scope|colspan|rowspan|alt|width|height|disabled|checked|selected|readonly|required|placeholder|autocomplete|maxlength|min|max|step|datetime|open|rel|target|download|method|href|src|action|formaction|xlink:href)$/;
const URL_ATTRIBUTES = new Set(["href", "src", "action", "formaction", "xlink:href"]);

// URL attributes accept only addresses inside AgentDesk ("#/settings", "/static/x", "./x", "../x",
// "?q=1") and ordinary web addresses (http and https). Every other scheme, for example javascript:
// or data:, is refused in any letter case and with surrounding spaces.
function isAllowedUrl(value) {
  const url = String(value).trim();
  return /^(?:#|\/|\.\/|\.\.\/|\?)/.test(url) || /^https?:/i.test(url);
}

// h("p", { class: "lead" }, "Hello ", h("strong", {}, name))
// Attributes: "class" sets className, "onClick"-style keys with a function add event listeners,
// true/false set or remove boolean attributes, and the allowed attributes above use setAttribute.
export function h(tag, attributes = {}, ...children) {
  const element = document.createElement(tag);
  for (const [name, value] of Object.entries(attributes || {})) {
    if (value === null || value === undefined || value === false) continue;
    const lower = name.toLowerCase();
    if (lower.startsWith("on")) {
      // Only a function becomes a listener. Any other value is never set as an attribute, so the
      // browser can never treat it as inline code.
      if (typeof value === "function") element.addEventListener(lower.slice(2), value);
      continue;
    }
    if (name === "class") {
      element.className = value;
      continue;
    }
    if (!ALLOWED_ATTRIBUTE.test(lower)) {
      throw new Error(`h(): attribute "${name}" is not allowed`);
    }
    if (URL_ATTRIBUTES.has(lower) && !isAllowedUrl(value)) {
      throw new Error(`h(): attribute "${name}" only accepts an AgentDesk address or an http(s) address`);
    }
    if (value === true) {
      element.setAttribute(name, "");
    } else {
      element.setAttribute(name, String(value));
    }
  }
  appendChildren(element, children);
  return element;
}

function appendChildren(element, children) {
  for (const child of children) {
    if (child === null || child === undefined || child === false) continue;
    if (Array.isArray(child)) {
      appendChildren(element, child);
    } else if (child instanceof Node) {
      element.appendChild(child);
    } else {
      element.appendChild(document.createTextNode(String(child)));
    }
  }
}

// Show an ISO time in the user's local time, for example "30/10/2026, 19:05:12".
export function formatDateTime(iso) {
  if (!iso) return "unknown";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? String(iso) : date.toLocaleString();
}

// 1536 -> "1.5 KB"
export function formatBytes(bytes) {
  if (typeof bytes !== "number" || !Number.isFinite(bytes) || bytes < 0) return "unknown"; // also NaN, Infinity
  const units = ["bytes", "KB", "MB", "GB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return unit === 0 ? `${value} bytes` : `${value.toFixed(1)} ${units[unit]}`;
}

// Read a message out to screen-reader users through the page's polite live region.
export function announce(message) {
  const region = document.getElementById("announcer");
  if (!region) return;
  region.textContent = "";
  // A short delay makes screen readers announce the same message twice in a row too.
  window.setTimeout(() => {
    region.textContent = message;
  }, 50);
}
