// One module for the ten Phase 1 placeholder pages. Each states its purpose and the phase that
// delivers it, and shows no data. Later phases replace entries here with real page modules.

import { h } from "../dom.js";

const PAGES = [
  {
    path: "/overview",
    title: "Overview",
    purpose: "A summary of your projects, agent activity, file changes, tests, security findings and the decisions waiting for you.",
    phase: "Arrives in Phase 2 as a preview layout; real data from Phase 3.",
  },
  {
    path: "/projects",
    title: "Projects",
    purpose: "Register your software projects and see each project's Git and connection status.",
    phase: "Arrives in Phase 3.",
  },
  {
    path: "/agents",
    title: "Agents",
    purpose: "Profiles of the planner, developer, testing and security-audit agents, with their current task and recent activity.",
    phase: "Arrives in Phase 2 as a preview; live data in Phase 4.",
  },
  {
    path: "/activity",
    title: "Activity",
    purpose: "A timeline of what the agents did, with filters by project, agent, event type and date.",
    phase: "Arrives in Phase 2 as a preview; real data from Phase 3.",
  },
  {
    path: "/files",
    title: "File changes",
    purpose: "Every file change that Git shows, with the evidence about who changed it and why, and a before-and-after view.",
    phase: "Arrives in Phase 3.",
  },
  {
    path: "/reports",
    title: "Reports",
    purpose: "The agents' change reports and activity logs, read from your projects or pasted in by you.",
    phase: "Arrives in Phase 3.",
  },
  {
    path: "/documents",
    title: "Documents",
    purpose: "Your projects' documents, such as requirements and designs, shown as plain text with their version and status.",
    phase: "Arrives in Phase 5.",
  },
  {
    path: "/testing",
    title: "Testing",
    purpose: "Test plans and the tests that were actually run, with their results.",
    phase: "Arrives in Phase 5.",
  },
  {
    path: "/security",
    title: "Security",
    purpose: "Security findings by severity and the security agent's audit reports.",
    phase: "Arrives in Phase 5.",
  },
  {
    path: "/approvals",
    title: "Approvals",
    purpose: "Decisions waiting for you and the history of the decisions you made.",
    phase: "Arrives in Phase 5.",
  },
];

function renderPlaceholder(page) {
  return h(
    "section",
    {},
    h("h1", {}, page.title),
    h("p", { class: "lead" }, page.purpose),
    h(
      "div",
      { class: "card placeholder" },
      h("p", { class: "badge" }, "Placeholder"),
      h("p", { class: "phase" }, page.phase),
      h("p", {}, "This page has no content yet, so it shows no data."),
    ),
  );
}

export const placeholderRoutes = PAGES.map((page) => ({
  path: page.path,
  title: page.title,
  render: () => renderPlaceholder(page),
}));
