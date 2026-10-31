# DEC-025: Phase 1 triage dispositions: SEC-010 accepted under DEC-018; migrations without transaction control; stricter CSRF and header hardening

| Field | Value |
|---|---|
| Type | Design decision (triage dispositions; no requirement text changed) |
| Status | Proposed |
| Task ID | T-20261030-002-PLN |
| Date | 2026-10-31 |
| Requirements / findings affected | CON-004, FR-012, NFR-003, NFR-004; findings SEC-010, SEC-006, SEC-007, SEC-008 (T-20261030-002-SEC), O-7 (T-20261030-002-TST) |
| Approved by and when | Not yet approved. These are routine technical dispositions; under DEC-020 the orchestrator may record them under the owner's delegated authority (OA). No item weakens a security requirement, accepts a Critical or High risk or adds a dependency |

## Context

Triage of the first Phase 1 cycle (cycle step 7) needs three choices recorded. The first is how SEC-010 is handled
without a new dependency. The second is how FR-012's "each migration in its own transaction" is enforced (TST
observation O-7). The third is that the Phase 1 security hardening goes beyond the minimum lists in NFR-003 and
NFR-004 without changing their text.

## Decision

### 1. SEC-010 (Info): accepted with justification; severity unchanged

- **No hashes in `requirements.lock.txt`.** DEC-018 chose exact pins without hashes and rejected option C (hashes,
  pip-tools) for upkeep and tooling reasons. The lock file is reproducible: a fresh `.venv` matches `pip freeze`
  (T-20261030-002-DEV, V1a).
- **Development sub-dependencies are not locked.** DEC-018 records this limitation: they never ship with AgentDesk.
  CON-004's acceptance text requires `requirements-dev.txt` to add exactly pytest and httpx.
- **No local vulnerability scanner.** A scanner would be a new direct development dependency (CON-004, owner
  decision), and the owner asked for no new dependencies.
- **Residual risk:** a tampered package would not be detected at install time, and advisories published after the
  auditor's knowledge are not assessed. This is recorded in architecture.md §15 item 21.
- **Compensating practice:**
  - every security audit reviews the pinned versions against the advisories it knows;
  - the final audit (TASK-088) states the residual;
  - the owner may revisit hashes or a scanner at final acceptance (TASK-092).
- **Proposed register status:** "Risk accepted", citing DEC-018 and this record. DEC-018 was decided under the
  owner's delegated authority. If the orchestrator judges that the register's "user decision" rule needs the
  owner personally, SEC-010 stays "Open" (Info). Either way it does not block the Phase 1 gate. SEC confirms the
  justification in its recheck (plan §1.6).

### 2. Migration files must not contain transaction-control statements (O-7)

- **Rule.** The migration runner refuses a migration file that contains a transaction-control statement as a
  statement of its own: `BEGIN`, `COMMIT`, `END`, `ROLLBACK`, `SAVEPOINT` or `RELEASE`. It names the file and
  applies nothing.
- **Allowed.** `CREATE TRIGGER ... BEGIN ... END;` bodies, which later migrations need (for example the approval
  triggers in `0009`).
- **Reason.** FR-012 promises that each migration runs in its own transaction and that a failing one is rolled
  back. A `COMMIT` inside a file would commit part of it outside the runner's transaction, and nothing could roll
  that part back.
- **Implemented by:** TASK-095.

### 3. Hardening beyond NFR-003 and NFR-004 without changing their text

- **SEC-008.** The Origin, CSRF-token and JSON checks apply to every HTTP method except GET, HEAD and OPTIONS,
  instead of only POST, PUT, PATCH and DELETE.
- **SEC-006.** WebSocket connections are refused, because no WebSocket route exists.
- **SEC-007.** `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy` and `Permissions-Policy` are added.
- **Why the text stays.** All three are stricter than the requirement text, so NFR-003 and NFR-004 stay as written
  and these become design elements in architecture.md §11.
- **CSP unchanged.** The CSP string stays exactly as NFR-004 states. Adding `require-trusted-types-for 'script'`
  would change NFR-004's text and is not adopted.
- **Implemented by:** TASK-094.

## Alternatives considered

- **SEC-010: add hashes by hand with `pip download` and `pip hash`.** Not chosen: more upkeep for every dependency
  change, and DEC-018 already rejected it.
- **SEC-010: install pip-audit.** Not chosen: a new dependency (owner decision), and the owner asked for none.
- **O-7: enforce nothing and rely on review.** Not chosen: Phases 3 to 5 add five migrations, and the check costs
  a few lines.
- **O-7: detect `COMMIT` with a plain text search.** Not chosen: it would also match comments, strings and trigger
  bodies.
- **SEC-008: keep the denylist.** Not chosen: a future route with another method would skip the checks.

## Impact

- **Architecture 1.1:** §11 rows "Cross-site requests" and "Browser hardening" updated; §15 item 21 added.
- **Plan 1.1:** TASK-094 and TASK-095.
- **Tests:**
  - TASK-094 tests (e) to (g);
  - TASK-095 tests (c) and (d).
- **Security:** the SEC-010 disposition is checked in the SEC repeat pass (T-20261030-002-SEC-2).
- **No change to SRS requirement text.**

## Follow-up tasks

TASK-094, TASK-095; SEC recheck in T-20261030-002-SEC-2; TASK-088 states the SEC-010 residual.
