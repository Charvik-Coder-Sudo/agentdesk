// Settings page: real system and database status from the server, the backup list and
// "Create backup now". All values are inserted as text.

import { api } from "../api.js";
import { announce, formatBytes, formatDateTime, h } from "../dom.js";

function facts(rows) {
  return h("dl", { class: "facts" }, rows.map(([label, value]) => [h("dt", {}, label), h("dd", {}, value)]));
}

function table(caption, columns, rows, emptyText) {
  if (rows.length === 0) return h("p", { class: "state-empty" }, emptyText);
  return h(
    "table",
    { class: "table" },
    h("caption", { class: "visually-hidden" }, caption),
    h("thead", {}, h("tr", {}, columns.map((column) => h("th", { scope: "col" }, column)))),
    h(
      "tbody",
      {},
      rows.map((cells) => h("tr", {}, cells.map((cell, index) => h("td", { "data-label": columns[index] }, cell)))),
    ),
  );
}

function integrityText(integrity) {
  const when = formatDateTime(integrity.checked_at);
  if (integrity.result === "ok") return `OK (SQLite ${integrity.check}, ${when})`;
  return `Problem found: ${integrity.result} (${when})`;
}

function renderSystem(system) {
  const lastBackup = system.last_backup
    ? `${formatDateTime(system.last_backup.created_at)} (${system.last_backup.name})`
    : "No backup yet";
  return [
    h(
      "div",
      { class: "card" },
      h("h2", {}, "System"),
      facts([
        ["AgentDesk version", system.version],
        ["Python version", system.python_version],
        ["SQLite version", system.sqlite_version],
        ["Data folder", h("code", {}, system.data_dir)],
        ["Installation ID", system.instance_id ?? "unknown"],
        ["Database created", formatDateTime(system.created_at)],
      ]),
    ),
    h(
      "div",
      { class: "card" },
      h("h2", {}, "Database"),
      system.backup_warning ? h("p", { class: "notice notice-warn" }, `Warning: ${system.backup_warning}`) : null,
      facts([
        ["Database file", h("code", {}, system.database_path)],
        ["Database file size", formatBytes(system.database_size_bytes)],
        ["Schema version", String(system.schema_version)],
        ["Integrity check", integrityText(system.integrity)],
        ["Last backup", lastBackup],
      ]),
      h("h3", {}, "Applied migrations"),
      table(
        "Applied database migrations",
        ["Version", "Name", "Applied"],
        system.migrations.map((m) => [String(m.version), m.name, formatDateTime(m.applied_at)]),
        "No migrations have been applied.",
      ),
    ),
  ];
}

function renderBackups(backups) {
  return table(
    "Database backups, newest first",
    ["Name", "Reason", "Size", "Created"],
    backups.map((b) => [b.name, b.reason, formatBytes(b.size_bytes), formatDateTime(b.created_at)]),
    "There are no backups yet.",
  );
}

function errorNotice(message, onRetry) {
  return h(
    "div",
    { class: "notice notice-error" },
    h("p", {}, `Could not load this information: ${message}`),
    h("p", {}, "Check that AgentDesk is still running, then try again."),
    h("button", { type: "button", class: "button button-secondary", onClick: onRetry }, "Try again"),
  );
}

export function renderSettings() {
  const systemArea = h("div", {}, h("p", { class: "state-loading" }, "Loading system information..."));
  const backupArea = h("div", {}, h("p", { class: "state-loading" }, "Loading backups..."));
  const result = h("p", { class: "result" });
  const button = h("button", { type: "button", class: "button" }, "Create backup now");
  let busy = false;

  async function refresh() {
    try {
      const [system, backupData] = await Promise.all([
        api.get("/api/v1/system"),
        api.get("/api/v1/system/backups"),
      ]);
      systemArea.replaceChildren(...renderSystem(system));
      backupArea.replaceChildren(renderBackups(backupData.backups));
    } catch (error) {
      systemArea.replaceChildren(errorNotice(error.message, refresh));
      backupArea.replaceChildren();
    }
  }

  // aria-disabled (not "disabled") keeps keyboard focus on the button while it works.
  button.addEventListener("click", async () => {
    if (busy) return;
    busy = true;
    button.setAttribute("aria-disabled", "true");
    button.textContent = "Creating backup...";
    result.className = "result";
    result.textContent = "";
    try {
      const data = await api.post("/api/v1/system/backups", {});
      result.className = "result notice notice-ok";
      result.textContent = `✓ ${data.message}. Integrity check: OK.`;
      announce(`${data.message}. Integrity check OK.`);
      await refresh();
    } catch (error) {
      result.className = "result notice notice-error";
      result.textContent = `✕ The backup was not created. ${error.message}`;
      announce(`The backup was not created. ${error.message}`);
    } finally {
      busy = false;
      button.removeAttribute("aria-disabled");
      button.textContent = "Create backup now";
    }
  });

  refresh();

  return h(
    "section",
    {},
    h("h1", {}, "Settings"),
    h(
      "p",
      { class: "lead" },
      "The status of this AgentDesk installation and its database. Choose light, dark or system colours with the Theme control at the top of the page.",
    ),
    systemArea,
    h(
      "div",
      { class: "card" },
      h("h2", {}, "Backups"),
      h(
        "p",
        {},
        "AgentDesk keeps the newest 10 backups in the backups folder inside the data folder. It also makes one automatically at startup when the newest backup is more than 24 hours old, and before every database update.",
      ),
      h("div", { class: "actions" }, button, result),
      backupArea,
      h(
        "p",
        {},
        "To restore a backup, stop AgentDesk first and follow the steps under “Backup and restore” in README.md.",
      ),
    ),
  );
}
