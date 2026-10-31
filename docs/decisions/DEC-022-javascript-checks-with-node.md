# DEC-022: JavaScript checks with the installed Node.js, no npm packages

| Field | Value |
|---|---|
| Type | Design decision (development checks) |
| Status | Approved (original decision); Amendment 1 Proposed (see below) |
| Task ID | T-20261030-001-PLN-2 (decided by the orchestrator and relayed in this delegation); Amendment 1: T-20261030-002-PLN |
| Date | 2026-10-30; Amendment 1: 2026-10-31 |
| Requirements / findings affected | CON-004 (unaffected), CON-011, CON-019, NFR-005; Amendment 1: T-20261030-002-DEV Defect 2 (plain `node --check` gives false passes) |
| Approved by and when | Original: the orchestrator, 2026-10-30, under the owner's delegated authority (OA: "Resolve minor ambiguities using the simplest maintainable solution consistent with the approved architecture."). Amendment 1: pending. Like the original, it is a technical correction that the orchestrator may record under the same delegated authority |

## Revision history

| Revision | Date | Task ID | Change | Approved by |
|---|---|---|---|---|
| Original | 2026-10-30 | T-20261030-001-PLN-2 | Decision recorded | The orchestrator, under the owner's delegated authority (OA) |
| Amendment 1 | 2026-10-31 | T-20261030-002-PLN | The syntax check uses module mode with the file on standard input, plus a negative control in every run; plain `node --check <file>` is no longer evidence | Pending user approval (to be recorded by the orchestrator under OA) |

## Context

The frontend is plain JavaScript with no build step and no JavaScript test framework. Syntax errors in a module
would otherwise only show up in the browser.

## Decision

Use the Node.js 24 already installed on the owner's PC, with no npm packages: `node --check` on every JS file
under `app/static/js/`, and optionally `node --test` for pure functions such as route parsing and formatting. The
checks run from the pytest suite. If Node is missing, the check is skipped with a visible reason, and a skipped
check never counts as evidence (CON-019). TST confirms once that a deliberately broken file fails the check.

This adds no dependency to AgentDesk: Node is a development check only and is not needed to run AgentDesk.

## Alternatives considered

No JavaScript checks (errors found late); a JavaScript test framework through npm (new dependencies).

## Impact

Plan §1.3; architecture §14. Tasks TASK-024, TASK-031 and later developer test tasks.

## Follow-up tasks

None (original). See Amendment 1.

## Amendment 1 (Proposed, 2026-10-31, T-20261030-002-PLN)

**Reason.** On Node.js 24.18.0, `node --check file.js` exited with code 0 for `.js` files that use
`import`/`export` and contain a syntax error. A deliberately broken file and a broken `app/static/js/router.js`
both "passed". The form `node --input-type=module --check < file.js` failed on both broken files and passes on all
seven current modules; the negative control `export function x( {` gave exit code 1 (T-20261030-002-DEV, Defect 2,
validation rows V3 and V3a). T-20261030-002-TST confirmed the module-mode form with the negative control
`export const x = ;` inside pytest (row M8). The plain form therefore produced false evidence, which CON-019 forbids.

**Old text (Decision, first sentences):** "Use the Node.js 24 already installed on the owner's PC, with no npm
packages: `node --check` on every JS file under `app/static/js/` ... TST confirms once that a deliberately broken
file fails the check."

**New text:** "Use the Node.js 24 already installed on the owner's PC, with no npm packages. Every JS file under
`app/static/js/` is syntax-checked as an ES module, with the file's content on standard input:
`node --input-type=module --check < <file>` (from pytest: run `node --input-type=module --check` with the file
opened as standard input). Every run of the check includes a negative control: a deliberately broken module source
(for example `export const x = ;`) given to the same command in the same run must exit non-zero; if it does not,
the check fails instead of passing. Plain `node --check <file>` is not used as evidence. `node --test` may still be
used for pure functions such as route parsing and formatting."

**Unchanged:** the checks run from the pytest suite. If Node is missing, the check is skipped with a visible reason,
and a skipped check never counts as evidence (CON-019). Node is not a dependency of AgentDesk (CON-004).

**Impact:**
- implementation-plan.md v1.1: §1.3 and TASK-024 updated; the corrective-pass definition of done (§3.3) uses
  this form.
- architecture.md §14 ("Development checks") and its §16 register row still say `node --check`. They defer to
  this record and are to be aligned in the next planner pass that may edit those sections. (T-20261030-002-PLN was
  limited to the security model in architecture.md.)
- TST's existing test `test_tst_javascript_syntax_check_with_negative_control` already follows the new text.
- No requirement text changes. The SRS does not mention the command.
