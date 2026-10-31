// Theme choice: "system" (default, follows Windows), "light" or "dark", kept in localStorage.

const STORAGE_KEY = "agentdesk.theme";
const CHOICES = ["system", "light", "dark"];

export function getTheme() {
  let saved = null;
  try {
    saved = window.localStorage.getItem(STORAGE_KEY);
  } catch {
    // Storage can be unavailable (for example in some private windows); use the default.
  }
  return CHOICES.includes(saved) ? saved : "system";
}

export function applyTheme(choice) {
  if (choice === "light" || choice === "dark") {
    document.documentElement.dataset.theme = choice;
  } else {
    delete document.documentElement.dataset.theme; // the stylesheet follows the system setting
  }
}

export function setTheme(choice) {
  const theme = CHOICES.includes(choice) ? choice : "system";
  try {
    window.localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Not saved, but still applied for this page view.
  }
  applyTheme(theme);
}

// Connect the header's <select> to the saved theme.
export function initThemeControl(select) {
  const theme = getTheme();
  applyTheme(theme);
  if (!select) return;
  select.value = theme;
  select.addEventListener("change", () => setTheme(select.value));
}
