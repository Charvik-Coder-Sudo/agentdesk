# DEC-024: Local data privacy on a shared PC (SEC-005): owner-only secrets, folder warning, no account name

| Field | Value |
|---|---|
| Type | Requirement change (new requirement NFR-024) and design decision |
| Status | Proposed |
| Task ID | T-20261030-002-PLN |
| Date | 2026-10-31 |
| Requirements / findings affected | NFR-024 (new); NFR-011, NFR-012, NFR-020 (unchanged); DEC-009 (respected); CON-004 (no new dependency); NFR-017 (no program run); security finding SEC-005 (T-20261030-002-SEC) |
| Approved by and when | Not yet approved. It strengthens security, weakens nothing and adds no dependency, so under SRS §1.3 and DEC-020 the orchestrator may record its approval under the owner's delegated authority (OA). It must be approved before TASK-038 (Phase 3) starts |

## Context

SEC-005 (Low) found that `D:\agentdesk` and `data\` inherit `Authenticated Users: Modify` and `Users: Read`
from `D:\`. On a PC with more than one Windows account, another account could read AgentDesk's data. It could
also change the code or `.venv`, which then runs as the owner. The planned ingest token (`data/ingest_token`)
would be readable by every local user. Note: TASK-038 creates this token in **Phase 3**, not Phase 4.

The owner asked for no routine questions, no new dependencies and a lightweight tool. DEC-009 forbids reading or
storing the Windows account name.

## Decision

1. **New requirement NFR-024 (Phase 3, Must, Proposed).** Secret files in the data folder (from Phase 3 the
   ingest token) are created so that only the current Windows user, SYSTEM and Administrators can access them.
   The standard library is used, and the account name is never read. If this fails, no secret is created and a
   plain message explains it.
   - Possible methods (DEV chooses in TASK-038):
     - the Windows security API through `ctypes`, using the current user's SID from the process token (a SID,
       not a name);
     - a security descriptor applied when the file is created;
     - or `os.mkdir(path, 0o700)` for a containing folder, which Windows applies as owner-only access in the
       supported Python versions. This option changes the token path, which NFR-020 fixes as `data/ingest_token`,
       so it needs its own decision record.
   - Full text and acceptance criteria: SRS v1.1, NFR-024.
2. **Phase 1 hardening (TASK-096; no requirement change):**
   - **Read-only startup warning.** It is shown when the AgentDesk folder or the data folder grants write-type
     access to Everyone (S-1-1-0), Authenticated Users (S-1-5-11) or Users (S-1-5-32-545). Detection compares
     well-known SIDs through `ctypes` and never looks up names. A failing check logs one INFO line and startup
     continues.
   - **Owner-only new data folder.** A data folder that does not exist yet is created with `os.mkdir(path, 0o700)`.
   - **README section "Keep AgentDesk private on a shared PC".** It gives the owner's own commands to restrict the
     folder, how to check the result and how to undo it (`icacls ... /reset`).
3. **AgentDesk never changes the permissions of an existing folder.** That stays an owner step, documented in the
   README and later in the user manual (TASK-081). The owner does not need to be asked whether other accounts
   exist: the warning appears only when it is relevant, and the secret file is protected either way.

## Alternatives considered

- **Ask the owner whether other Windows accounts exist** (SEC's verdict condition 3). Rejected: a routine
  question, and the controls above are cheap whatever the answer.
- **Let AgentDesk or `setup.bat` restrict existing folder permissions automatically.** Rejected: removing
  inheritance can lock out other tools, and changing the permissions of the owner's folders is the owner's choice.
- **Run `icacls` from AgentDesk.** Rejected for three reasons:
  - NFR-017 limits the programs AgentDesk runs;
  - `icacls` output is localized;
  - its output contains account names (DEC-009).
- **`pywin32`.** Rejected: a new dependency (CON-004).

## Impact

- **SRS 1.1:** NFR-024 added (Proposed); counts in §7.
- **Architecture 1.1:** §11 gains a "Local data privacy" row; §15 gains item 20 (residual risk: permissions of
  existing folders).
- **Plan 1.1:**
  - TASK-096 (Phase 1);
  - TASK-038 and TASK-048 (Phase 3) amended;
  - the Phase 3 requirement list includes NFR-024;
  - TASK-036 confirms that the approval is recorded.
- **Traceability matrix 1.1:** new NFR-024 row; SEC-005 linked from NFR-011.
- **Tests:**
  - TASK-096 tests (a) to (f);
  - TASK-038 adds a test that checks the token file's access list by SID.
- **Security:** SEC-005 can be verified only after the Phase 3 part passes TASK-048. Until then the proposed
  register status is "In remediation".

## Follow-up tasks

TASK-096 (Phase 1), TASK-038 and TASK-048 (Phase 3); TASK-081 (the user manual mentions the folder step).
