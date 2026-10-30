# AgentDesk: architecture

| Field | Value |
|---|---|
| Version | 0.3 |
| Status | Draft |
| Last updated | 2026-10-30 |
| Task ID | T-20261030-001-PLN (maintained by planner-agent, OD-10) |
| Related documents | [srs.md](srs.md), [database-schema.md](database-schema.md), [implementation-plan.md](implementation-plan.md), [traceability-matrix.md](traceability-matrix.md) |

## Revision history

| Version | Date | Task ID | Change | Requirement IDs | Approved by |
|---|---|---|---|---|---|
| 0.1 | 2026-10-30 | T-20261030-001-ORC | Initial proposal, presented in conversation | - | Accepted in principle by the project owner |
| 0.2 | 2026-10-30 | T-20261030-001-ORC | Owner refinements R1-R12: phased schema, Project Connection Wizard, five-category evidence model, manual report ingestion, read-only boundary, interactive detail views. Added ingestion of the agents' change-tracking files (the agent definitions gained a shared tracking protocol on 2026-10-30). | R1-R12 | Pending |
| 0.3 | 2026-10-30 | T-20261030-001-PLN | Status Draft (E4, OD-18); links to the new SRS. Findings resolved: test-runner files and their verification rule (E1), file-change reviews (E2), no stored owner name (E3), refusal of home, user-profile and drive-root folders (E6, OD-17), checkpoint rate limit (E7, new §6.6). Owner decisions applied: final-message excerpt 1 KB (OD-4), typed name only (OD-5), no Markdown renderer, documents as escaped plain text (OD-6), no automatic stage/commit/discard (OD-12), global Claude settings read only in the Phase 4 wizard check (OD-13), strictly read-only security review and its limitation (OD-16 as corrected by OC-1, new §11.1). Proportionality principle P10 (FU-1, FU-2). Decision register rewritten with status and source; DEC-013 to DEC-017 added as Proposed. | E1-E4, E6, E7; OD-3 to OD-8, OD-12, OD-13, OD-16, OD-17; OC-1; FR-022, FR-039, FR-045, FR-046, FR-049, FR-053, FR-054, FR-059, FR-060, NFR-016, CON-010, CON-012 | Pending |

---

## 1. Purpose

AgentDesk is a local dashboard that lets a human project owner see, with evidence, what four
Claude Code specialist agents (planner, developer, testing, security audit) are doing and have done
across one or more software projects: activity, file changes, reasons, tests, security findings,
pending decisions and release readiness.

It is a monitoring and accountability tool. It is not a chatbot, it does not run agents, and it never
acts on a monitored project on its own.

It is a personal tool for one owner on one Windows PC (FU-1). It aims for practical usefulness, reliability,
basic security and easy maintenance, not enterprise features. Requirement IDs (FR-, NFR-, CON-) are defined
in [srs.md](srs.md); [traceability-matrix.md](traceability-matrix.md) links each one to this design.

## 2. Principles

These rules override everything else in this document.

| ID | Principle |
|---|---|
| P1 | **Evidence over claims.** Every record shows where it came from and how strong the evidence is (section 5). |
| P2 | **No attribution by timing.** A file is never attributed to an agent only because it changed while the agent or session was running. |
| P3 | **Read-only toward monitored projects.** The single exception is the Project Connection Wizard writing Claude Code hook settings after the owner previews and confirms the exact change (section 7). Any other write requires a separately authorized future feature. |
| P4 | **Never acts on the owner's behalf.** AgentDesk never approves, stages, commits, pushes, deploys or discards anything, and never modifies global Claude Code settings or agent definitions (R9, OD-12). |
| P5 | **Never blocks Claude Code.** Hooks always exit 0, print nothing, and fall back to a local buffer when AgentDesk is down. |
| P6 | **Local-first.** Bound to localhost, SQLite on disk, no cloud services, no API keys, no Docker. |
| P7 | **Lightweight.** No frontend framework, no build step, no chart or diagram libraries and no Markdown renderer (documents are shown as escaped plain text, DEC-010), two runtime Python dependencies. |
| P8 | **No secrets, no source code in the database.** Content is redacted or dropped at capture time; diffs and reports are read live from the project when viewed. |
| P9 | **Honest screens.** Empty states instead of invented numbers. Sample data exists only in Phase 2 preview mode, always under a visible banner, and is removed in Phase 3. If information is unavailable, the screen says so. |
| P10 | **Proportionate.** A personal tool (FU-1, FU-2): no login system, analytics, separate background services or enterprise features. The basic security protections in section 11 are never weakened to save effort. |

## 3. System context and boundaries

```
 +-------------------------- Monitored project (any folder the owner registers) --------------------------+
 |  source files   .git/   docs/agent-activity/...   docs/testing/...   docs/security/...   .claude/       |
 +-------^-------------^----------------^------------------------------------------------------^----------+
         | read-only   | read-only      | read-only (tracking files, docs, test-runner files)  | write ONLY via
         | (diff view) | (git CLI)      |                                                      | wizard, after
         |             |                |                                                      | preview+confirm
 +-------+-------------+----------------+------------------------------------------------------+----------+
 |                                AgentDesk server (FastAPI, 127.0.0.1:8765)                              |
 |  ingestion | git checkpoints | evidence | tracking parser | reports | connection wizard | approvals     |
 |                                SQLite: data/agentdesk.db (+ backups, logs, spool)                      |
 +------^---------------------------------------^---------------------------------------------^---------+
        | POST sanitized events                 | JSON REST (same-origin only)                | read-only:
        |                                       |                                             | ~/.claude settings
 +------+--------------------------+     +------+---------------------------+                 | flags, agent names
 | hooks/agentdesk_hook.py         |     | Browser dashboard                |                 | (Phase 4 wizard check only)
 | run by Claude Code on events    |     | static HTML/CSS/vanilla JS       |                 |
 +---------------------------------+     +----------------------------------+                 |
```

### 3.1 What AgentDesk may touch

| Location | Access | When |
|---|---|---|
| AgentDesk's own `data/` folder | Read and write | Always: database, backups, logs, event spool, ingest token, connection backups |
| Monitored project files | Read only | Diff viewing, untracked-file fingerprints, tracking files, documents, test-runner file import, settings inspection |
| Monitored project `.git/` | Read only, through the `git` CLI with hardened flags | Checkpoints, diffs, history. Never writes the index, objects or refs |
| Monitored project `.claude/settings.local.json` (or `.claude/settings.json` if the owner chooses) | Write | Only in the wizard's install or disconnect step, after the owner previews the exact change and confirms it |
| `~/.claude/settings.json`, `~/.claude/agents/*.md`, project `.claude/agents/*.md` | Read only, specific fields | Only in the Phase 4 wizard's configuration check (section 7, step 3; OD-13, DEC-017): `disableAllHooks`, number of existing hooks, agent names from frontmatter. No other phase or feature reads these files. |
| Any other location | None | |

### 3.2 What AgentDesk never does

- Approve anything by itself, stage files, create commits, push, pull, fetch, merge, stash, reset, checkout,
  clean, discard changes or deploy (OD-12).
- Edit, add or delete files in a monitored project, other than the wizard exception above.
- Register a drive root, `C:\Users`, a user-profile root (such as the home folder), a Windows or program
  folder, or its own data folder as a monitored project (section 7, step 1).
- Record the Windows account name. Approvals and confirmations use the name the owner types (DEC-009).
- Edit `.gitignore`, CLAUDE.md, agent definitions or any global Claude Code configuration.
- Execute commands that arrive in events or reports. The only programs it runs are `git` (fixed read-only
  subcommands), `claude --version`, and its own hook script during the wizard self-test.
- Store file contents, edit strings, tool output, prompt text or transcripts.

## 4. Components

### 4.1 Server (Python, FastAPI)

| Module | Responsibility | Phase |
|---|---|---|
| `app/core/` | Configuration, logging setup, security middleware (Host allowlist, CSRF token, security headers), time utilities; later redaction | 1 (redaction 3) |
| `app/database/` | SQLite connection settings, migration runner, backup and restore | 1 |
| `app/api/` | REST routers, one file per area, all under `/api/v1` | 1+ |
| `app/models/` | Pydantic request and response schemas (input validation) | 1+ |
| `app/services/` | Business logic: projects, checkpoints, evidence classification, reports, ingestion, connection, readiness | 3+ |
| `app/integrations/git/` | Safe read-only `git` runner and output parsers | 3 |
| `app/integrations/tracking/` | Parsers for the agents' change-tracking Markdown files | 3 (change reports, log), 5 (tests, audits, register, decisions) |
| `app/integrations/claude_code/` | Hook payload normalizer, settings inspector, settings merge planner | 4 |

### 4.2 Hook script

`hooks/agentdesk_hook.py`: standard-library Python only, run by Claude Code for the registered
events (section 6). It sanitizes the event locally, posts it to the server with a short timeout,
and appends it to a local spool file if the server is unavailable.

### 4.3 Browser dashboard

One static `index.html`, one stylesheet and plain JavaScript ES modules (a small hash router, an
API wrapper, a DOM helper and one module per page). No framework and no build step. All data is
inserted with `textContent` or created elements, never as raw HTML.

### 4.4 Windows scripts

`scripts/setup.bat` (one-time virtual environment and dependency install), `scripts/start.bat`
(start the server and open the browser), `scripts/backup_db.py`, `scripts/restore_db.py`.

## 5. Data sources and evidence model

### 5.1 Sources

| Source | What it provides | Evidence level |
|---|---|---|
| Claude Code hooks | Sessions, subagent runs, tool calls (tool, file path, outcome) | **Observed**: the call happened |
| Git (read-only) | Which files differ, change type, line counts, content fingerprints | **Verified**: the change exists |
| Agent change-tracking files | Reports, claimed file changes, tests, findings, statuses | **Agent-reported**: a claim |
| Manual report paste | Reports from agents that cannot write files | **Agent-reported**, submitted by a named person |
| Subagent final message (SubagentStop) | Redacted excerpt of at most 1 KB (1,024 characters), task ID and report path (DEC-008) | **Agent-reported** |
| Test-runner file in the project (for example JUnit XML) | Executed test results | **Verified** only if a matching observed test command produced it (section 10.3); otherwise *test-runner file, origin not verified* |
| Owner actions in AgentDesk | Decisions, approvals, file-change reviews, wizard confirmations | **Human** |
| AgentDesk itself | Registrations, checkpoints, self-tests | **System** |

### 5.2 The five categories for file changes

Every file-change view shows one or more of these badges, always as icon plus text.

| Badge | Meaning | What it does not mean |
|---|---|---|
| **OBSERVED** | A Claude Code hook reported a successful file tool call (Write, Edit, MultiEdit, NotebookEdit) on this path, by a named agent or by the main session. | That this agent wrote the file's final content. Someone may have edited it afterwards. |
| **GIT-VERIFIED** | Git shows the file differs from the last commit or from the selected baseline. | Who made the change. |
| **AGENT-REPORTED** | An agent's report (tracking file, pasted report or final message) says it changed this file. | That the change happened. AgentDesk cross-checks it against Git. |
| **UNATTRIBUTED** | Git-verified change with no observed tool call and no agent report naming this file. | That nobody is responsible. It means there is no evidence either way. |
| **PRE-EXISTING** | The file's current content already existed at the start of the selected window (project connection or session start). | That the content is safe or approved. |

These are the five *evidence labels* defined in [srs.md](srs.md) §2.1 (FR-029). An owner's review of a change
(section 10.3, file-change reviews) is shown next to the labels and never changes them.

### 5.3 Classification rules

Classification is computed when a page is viewed, from stored facts. It is never saved as a
conclusion, so new evidence (for example a report that arrives later) is reflected immediately.

Two independent axes are shown:

- **Git axis**: Git-verified change / no change in Git / not a Git repository.
- **Source axis**: Observed / Agent-reported / Unattributed / Pre-existing (Observed and Agent-reported can both apply).

| Rule | Statement |
|---|---|
| R-A | PRE-EXISTING when the file's fingerprint at the window's baseline checkpoint equals its current fingerprint. If the content changed after the baseline, the badge reads "Pre-existing, changed since" and the later change is classified by R-B to R-D. |
| R-B | OBSERVED when a successful file tool event for the same project and path exists after the baseline. The label is "Observed edit by &lt;agent or Main session&gt;", never "Changed by". |
| R-C | AGENT-REPORTED when any report names the path. |
| R-D | UNATTRIBUTED when the change is Git-verified and neither R-B nor R-C applies. |
| R-E | Time overlap never produces OBSERVED or any agent attribution. Views may show neutral context only, for example "first detected at checkpoint 14:05 (session 3f2a)". |
| R-F | Shell commands (Bash, PowerShell) never produce OBSERVED for files, because their file effects are unknown. |

**Discrepancy flags** (shown, never resolved automatically):

- *Reported, not found in Git*: an agent claims a change that Git does not show.
- *Observed, not in that agent's report*: a hook saw an agent edit a file that its report omits.
- *Git change not reported*: a change during a task window that no report mentions. This is a prompt to review, not an accusation.
- *Observed edit, no Git change*: the file was later reverted, or it is ignored by Git.

### 5.4 Verification vocabulary for other records

Events, tests, findings and approvals use: `observed`, `verified`, `agent_reported`, `human`, `system`.
Test runs add one value, `file_origin_unverified`, shown as *Test-runner file, origin not verified* (E1, section 10.3).
Test results and findings are never shown as verified because an agent says so.

## 6. Claude Code integration

Based on the official hook reference (code.claude.com/docs/en/hooks), checked 2026-10-30 against the
installed Claude Code 2.1.314. Phase 4 verifies every field below with real events before relying on it.

### 6.1 Registered events

| Event | Mode | Recorded |
|---|---|---|
| SessionStart | Synchronous, 5 s timeout | Session start, source, model. Always takes a baseline Git checkpoint (section 6.6). |
| SessionEnd | Synchronous, 5 s | End reason. Requests a checkpoint (rate-limited, section 6.6). |
| UserPromptSubmit | Async | Prompt boundary only (prompt id). Never the prompt text. |
| PreToolUse | Async | Tool started: tool name, file path for file tools, redacted command for shell tools, the Agent tool's short description and task ID |
| PostToolUse | Async | Tool succeeded, duration |
| PostToolUseFailure | Async | Tool failed; exit code if the error text starts with `Exit code N`; interrupt flag |
| SubagentStart | Synchronous, 5 s | Subagent run started: `agent_id`, `agent_type` |
| SubagentStop | Synchronous, 5 s | Run ended; task ID and report path extracted; redacted excerpt of at most 1 KB (1,024 characters, DEC-008). Requests a checkpoint and a tracking-file rescan (rate-limited, section 6.6). |
| Stop | Synchronous, 5 s | Turn ended. Requests a checkpoint (rate-limited, section 6.6). |
| StopFailure | Async | Turn ended by an API error |
| Notification | Async | Notification type and a redacted message of at most 200 characters (for example, waiting for permission) |
| TaskCreated, TaskCompleted | Async | Claude Code task id and subject (redacted, capped) |

Synchronous lifecycle hooks are rare and short. Running them synchronously keeps them from being killed
when a short `claude -p` run ends. High-frequency tool hooks are async so they never slow Claude down.

### 6.2 Hook script behaviour

1. Read the event JSON from stdin, up to 5 MB. A larger event is recorded as "oversized" without details.
2. Sanitize it locally (section 6.3) and add a unique `event_uuid` and the capture time.
3. POST it to `http://127.0.0.1:<port>/api/v1/ingest/claude-code` with the ingest token from
   `data/ingest_token` and a 1.5 s timeout. The address is fixed in the script and never comes from input.
4. If the server is unreachable or rejects the event, append the sanitized event to
   `data/spool/YYYYMMDD.jsonl` (capped at 50 MB in total; beyond that, events are counted and dropped).
5. Print nothing to stdout and always exit with code 0, including on internal errors.
   On some events Claude Code adds hook stdout to Claude's context, and exit code 2 blocks actions,
   so the script can do neither. Its own problems go to `data/logs/hook.log` (size-capped).

Configuration written by the wizard uses the exec form (`command` = absolute path of a Python
interpreter, `args` = absolute script path, project id and an `--agentdesk` marker), so no shell
parses the command.

### 6.3 What is kept and what is dropped

| Field | Stored |
|---|---|
| `session_id`, `agent_id`, `agent_type`, `prompt_id`, `tool_name`, `tool_use_id`, `hook_event_name`, `permission_mode`, `model`, `duration_ms`, `source`, `reason` | Yes |
| `cwd` | Yes (normalized), used to match the project |
| File tool `file_path` / `notebook_path` | Yes: project-relative inside the project, absolute (flagged "outside project") otherwise |
| `content`, `old_string`, `new_string`, edits | Never. Character counts only. |
| Shell `command` | Redacted, at most 200 characters |
| Shell `description`, Agent tool `description` | Redacted, at most 200 characters |
| Agent tool `prompt` | Never. Only a `Task ID: T-...` line is extracted by pattern. |
| WebFetch URL | Scheme, host and path only (query string removed) |
| Grep and Glob patterns | Redacted, at most 100 characters |
| MCP tool input | Tool name only |
| `tool_response` | Never |
| `prompt` (UserPromptSubmit) | Never |
| `last_assistant_message` (SubagentStop) | Redacted excerpt of at most 1,024 characters (about 1 KB), plus the extracted task ID and report path (DEC-008). The rest of the message is dropped. |
| `transcript_path`, `agent_transcript_path` | Path only. Transcripts are never read. |

Redaction replaces private-key blocks, cloud and GitHub token formats, `sk-` style keys, bearer tokens,
credentials in URLs and `password=`/`token=`/`secret=`/`api_key=` assignments with `[REDACTED]`.
Redaction is best effort, which is why content-bearing fields are dropped entirely rather than redacted.

### 6.4 Linking runs, tasks and reports

- When the orchestrator delegates, the Agent tool's prompt starts with `Task ID: T-YYYYMMDD-NNN-ROLE`
  (change-tracking protocol). The hook extracts only that ID and the short description.
- The Agent tool's PreToolUse and PostToolUse share a `tool_use_id`, giving the run's start, end and outcome.
- Events fired inside the subagent carry `agent_id` and `agent_type`. Linking that `agent_id` to the
  Agent tool call is **inferred** (same session, matching agent type, adjacent timing) unless the subagent's
  final message or report contains the same task ID. Inferred links are labelled as such.
- The subagent's final message contains its report path (protocol rule), which links the run to the
  tracking file.

### 6.5 Sessions, staleness and offline buffering

- A session is *active* from SessionStart until SessionEnd. With no events for 30 minutes it shows as
  *idle*. A session with no SessionEnd and no events for 12 hours becomes *stale*. AgentDesk shows
  "last event N ago" rather than claiming activity.
- A subagent run without SubagentStop, whose session has ended or gone stale, becomes *unknown (no stop event)*.
- The server replays the spool at startup and every 60 seconds. Replay is idempotent through `event_uuid`.

### 6.6 Automatic Git checkpoints (rate limit)

`Stop` fires at the end of every turn, so checkpoints need a limit (E7, FR-046).

| Trigger | Rule |
|---|---|
| Project registration, SessionStart (baselines), manual "Refresh from Git" | Always taken at once, even inside a rate-limit window |
| Stop, SubagentStop, SessionEnd (automatic) | At most one automatic checkpoint per project per 10 seconds |

- If an automatic request arrives less than 10 seconds after the project's last checkpoint, it is not taken at
  once. One *trailing* checkpoint is scheduled for the end of the 10-second window, and every further request
  inside the window is merged into it.
- Tracking-file rescans requested by the same events follow the same rule and run with that checkpoint.
- This is a simple timer inside the server process (like the spool replay). There is no separate worker or queue.
- If the server stops before a trailing checkpoint runs, it is lost. Nothing is missed in the long run, because
  each checkpoint records the current Git state; the next checkpoint shows the same changes.

## 7. Project Connection Wizard

Route `#/projects/connect`. Steps 1-2 arrive in Phase 3 (needed for Git tracking). Steps 3-5 arrive in Phase 4.

### Step 1. Choose a folder

- Paste a path, or use the built-in folder browser. Browsers do not reveal real folder paths to web
  pages, so the server lists drives and **folder names only**: never file names or contents. Hidden
  and system folders are skipped.
- Validation: the folder exists; it is not a refused folder (below); it is not already registered (if it is,
  the wizard links to that project). Junctions and symlinks are resolved, the final path is shown, and all
  checks run on that final path (letter case and trailing slashes ignored).
- **Refused folders** (E6, OD-17, FR-022). AgentDesk never registers:
  - a drive root (`C:\`, `D:\`, ...);
  - `C:\Users` itself, or any user-profile root: any folder directly inside it (for example `C:\Users\Charvik`)
    and the current `%USERPROFILE%`;
  - the Windows and program folders, or anything inside them: `%SystemRoot%` (normally `C:\Windows`),
    `%ProgramFiles%`, `%ProgramFiles(x86)%`, `%ProgramData%`;
  - AgentDesk's own data folder, or anything inside it.

  Folders *inside* a user profile are allowed, for example `C:\Users\Charvik\projects\app`. The wizard
  explains each refusal in one sentence.
- **Git root rule**. If the folder is inside a Git repository, the wizard shows the repository root. It offers
  to use the root instead of the chosen folder only if the root itself passes the refused-folder checks.
  If the Git root is a refused folder (for example the home folder `C:\Users\Charvik`, which is a Git
  repository on this PC), AgentDesk does not use that repository: the folder is registered as
  "Not a Git repository" with the explanation "The enclosing Git repository is at <root>, a location AgentDesk
  never monitors. Run `git init` in this folder if you want Git tracking." No Git command is ever run for that
  project. The check is repeated on every "Refresh from Git".

### Step 2. Git status (read-only)

- Shows: repository root, branch, last commit (short hash and subject), number of uncommitted changes by type, untracked files.
- Explains: "These N uncommitted changes will be labelled PRE-EXISTING."
- Not a Git repository (including the refused-Git-root case above): the owner may continue. Git-verified
  changes are then unavailable, and the screens say so.
- **Register project** saves the project in AgentDesk's database and takes the baseline checkpoint.
  Nothing is written to the project.

### Step 3. Claude Code configuration check (read-only)

| Check | Possible results |
|---|---|
| Claude Code CLI | Found with version / not found (hooks can still be installed) / older than the tested version (warning) |
| `.claude/settings.json` | Absent / valid, with existing hooks counted per event / AgentDesk entries present / invalid JSON (install into this file is blocked) |
| `.claude/settings.local.json` | Same checks, plus whether Git ignores it (warning if not: it would contain machine-specific paths) |
| `disableAllHooks` | Set in project, local or user settings: warning that hooks will not run |
| User-level hooks | Count only, for information: they keep running alongside AgentDesk's hooks |
| Agent definitions | Which of `planner-agent`, `developer-agent`, `testing-agent`, `security-audit-agent` exist (project or user level), names only |
| Change-tracking files | Whether `docs/agent-activity/activity-log.md` and the report folders exist (agent-reported records available) |
| Workspace trust, managed policies | Cannot be checked from outside Claude Code: shown as reminders |

This step is the only place where AgentDesk reads user-level Claude Code files (`~/.claude/settings.json`,
`~/.claude/agents/*.md`). It reads them read-only and only for `disableAllHooks`, the number of hooks and agent
names (OD-13, DEC-017, FR-039). It never writes them.

### Step 4. Hook installation (optional)

Skipping leaves the project registered with Git tracking only ("Not connected").

1. **Target file**: `.claude/settings.local.json` (recommended: personal, normally not committed) or
   `.claude/settings.json` (shared with everyone who clones the project; shown with a warning).
2. **Preview**: the list of hook entries to add and a before/after diff of the whole file. The preview
   records a SHA-256 hash of the file as it was read.
3. **Confirm**: the owner ticks "I approve writing this change to &lt;full path&gt;", types their name, and selects Install.
   The browser may remember the last typed name on this PC (local storage). AgentDesk stores no owner profile
   and never reads the Windows account name (DEC-009, E3).
4. **Apply**:
   - Re-read the file. If its hash differs from the preview, abort and show a new preview.
   - Copy the original, byte for byte, to `data/connection-backups/<project>/<timestamp>-<file>` inside AgentDesk.
   - Write to a temporary file in the same folder, then atomically replace the original.
   - Re-read and validate the result.
   - Record the connection, the approver and the time.
5. **Merge rules**:
   - Never remove, reorder or modify existing entries or other settings.
   - Append one matcher group per event, identified by the AgentDesk script path and the `--agentdesk` marker.
   - Re-installing replaces only AgentDesk's own groups, so the operation is idempotent.
   - Refuse to proceed if the file is not valid JSON, contains comments, or has a `hooks` value that is not an object.
   - The output uses 2-space indentation, keeps the file's original line endings, and keeps all content.
6. **Advice shown**: close running Claude Code sessions in that project first. Claude Code itself may write
   to `settings.local.json` (for example when the owner chooses "always allow"), and new hooks load in new sessions.

### Step 5. Connection health

- **Configuration check**: AgentDesk's entries are present and valid; the Python and script paths exist.
- **Self-test**: AgentDesk runs its own hook script once with a synthetic event (a fixed command with no
  input from the browser) and waits up to 5 seconds for it to arrive. Self-test events are labelled
  SELF-TEST and excluded from all statistics.
- **First real event**: "Start a new Claude Code session in this folder." The step turns green when a real SessionStart arrives.

| Health state | Meaning |
|---|---|
| Not connected | Registered; no AgentDesk hooks |
| Awaiting first event | Hooks installed, self-test passed, no real event yet |
| Connected | Real events received; shows "last event N ago". A quiet project is not an error. |
| Attention needed | AgentDesk entries missing or changed; script or Python path missing; `disableAllHooks` set; events rejected (token mismatch); spooled events waiting for replay |
| Not a Git repository | Information: file changes cannot be Git-verified |

**Disconnect**: a preview that removes only AgentDesk's entries, then confirmation, backup and atomic write.
If AgentDesk created the settings file and nothing else would remain in it, the preview proposes deleting
that file. That is the only file AgentDesk can ever delete: one it created, and only after confirmation.
The README documents manual removal (delete the hook entries whose `args` contain `agentdesk_hook.py`).

## 8. Change-tracking file ingestion

The four agents keep tracking records in each project (the shared "Change tracking" protocol in their
definitions). AgentDesk reads these files and **never writes to them**.

| Path (relative to the project root) | Parsed into | Phase |
|---|---|---|
| `docs/agent-activity/activity-log.md` | Summary table rows (work items, statuses as recorded by the orchestrator) and log entries (timeline, agent-reported) | 3 |
| `docs/agent-activity/change-reports/T-*.md` | Planner and developer reports: header fields, Files changed table, Validation table | 3 |
| `docs/testing/test-reports/T-*.md` | Executed table (command, exit code, counts), per-test results, Proposed table | 5 |
| `docs/security/audit-reports/T-*.md` | Findings, re-checked findings, deployment-readiness verdict | 5 |
| `docs/security/findings-register.md` | Current status of each finding | 5 |
| `docs/decisions/DEC-*.md` | Decision records: type, status, approved by | 5 |
| `CHANGELOG.md` | Unreleased entries with task IDs (display only) | 5 |

Rules:
- The parsers follow the protocol's templates and are tolerant: a file that does not match is kept as
  "fields not recognized" and still viewable. Nothing is guessed.
- A content hash prevents re-parsing unchanged files. When a file changes, a new version is recorded and the old one is kept.
- Rescans happen at project registration, on SubagentStop, Stop and SessionEnd (Phase 4, rate-limited together
  with checkpoints, section 6.6), and on the "Rescan" button.
- The database keeps parsed fields and a short redacted summary. The full report is read live from the file when viewed.
- Status values are displayed exactly as written by the agents, for example `Awaiting validation`, `Pending user approval`, `Fixed - pending verification`.
- Version 1 uses the protocol's default paths. A project whose CLAUDE.md overrides them shows "tracking files not found" (known limitation).

## 9. Manual activity-report ingestion

For agents that cannot write files, projects without tracking files, or reports produced elsewhere.

- **Reports > Add report** (`#/reports/new`): project, agent (core profile or free text), optional session
  and task ID, and a paste box.
- **Accepted formats**, detected automatically:
  1. a report in the change-tracking template format (Markdown), parsed with the same parser as section 8;
  2. a fenced `agentdesk-report` JSON block (below);
  3. plain text, stored as a narrative report with no structured items.
- **Preview** shows exactly what will be recorded (fields, file claims, tests, findings) before **Save**.
- Saved reports are labelled *AGENT-REPORTED, submitted manually by &lt;name&gt; on &lt;date&gt;*. File claims are cross-checked against Git like any other report.
- Limits: 64 KB per report, redaction applied, all text displayed escaped (never as HTML).
- The page offers a copyable instruction snippet the owner can add to a prompt, asking any agent to end
  its answer with an `agentdesk-report` block. AgentDesk never edits agent definitions.

```json
{
  "schema": "agentdesk-report/v1",
  "task_id": "T-20261030-002-SEC",
  "agent": "security-audit-agent",
  "summary": "Audited authentication module.",
  "status": "Awaiting approval",
  "files": [{ "path": "app/auth.py", "change": "reviewed", "reason": "Scope of audit" }],
  "tests": [{ "name": "test_login_rejects_bad_token", "status": "passed", "command": "pytest tests/test_auth.py" }],
  "findings": [{ "id": "SEC-001", "title": "Session token not rotated", "severity": "medium",
                 "location": "app/auth.py:88", "remediation": "Rotate on login" }]
}
```

## 10. Dashboard

### 10.1 Navigation and routes

All pages are deep-linkable. Filters are kept in the URL, so links can be shared and Back and Forward work.
In Phase 1, every page except Settings is a placeholder that names the phase shown in the last column (FR-006).

| Route | Page | Detail views and interactions | Real data from |
|---|---|---|---|
| `#/overview` | Overview | Every tile opens the matching filtered list; every panel row opens its item | Phase 3-5 (preview in Phase 2) |
| `#/projects` | Projects | Health badge per project; "Connect a project" | 3 |
| `#/projects/connect` | Connection Wizard | Steps 1-2 (Phase 3), 3-5 (Phase 4) | 3, 4 |
| `#/projects/:id` | Project detail | Git status, checkpoints, connection health, configuration check, sessions, Rescan, Refresh from Git, Disconnect | 3, 4 |
| `#/agents`, `#/agents/:key` | Agents | Profile, status, current task, runs, reports, observed file edits, other observed agent types | 4 (preview in 2) |
| `#/activity` | Activity timeline | Filters: project, agent, event type, source/evidence, date range, status | 3 (preview in 2) |
| `#/activity/:eventId` | Event detail | Sanitized fields; links to session, task, agent, file | 3 |
| `#/sessions/:id` | Session detail | Timeline, subagent runs, files observed, checkpoints | 4 |
| `#/tasks/:key` | Work item / task detail | Agent tasks for a `T-...` ID; reports; files (reported vs Git vs observed); tests; findings; approvals | 3, 4 |
| `#/files` | File changes | List with evidence badges; filters: project, window (since connection / a session), badge, change type | 3 |
| `#/files/:projectId/:path` | File detail | Diff viewer (unified or split), evidence panel, checkpoint history, discrepancy flags; "Mark as reviewed" (Phase 5, section 10.3) | 3 |
| `#/reports`, `#/reports/new`, `#/reports/:id` | Agent reports | List, paste form, report detail with Git cross-check results | 3 |
| `#/documents`, `#/documents/:id` | Documentation | Grouped by type; document shown as escaped plain text; version and status as declared in the document; Git history; approval state | 5 |
| `#/testing`, `#/testing/runs/:id` | Testing | Executed and Proposed tabs; run detail with source badge | 5 |
| `#/security`, `#/security/findings/:id` | Security | Severity counts, findings register, finding detail, audit reports and verdicts | 5 |
| `#/approvals`, `#/approvals/:id` | Approvals | Pending queue, decision form, immutable history | 5 |
| `#/settings` | Settings and system | Version; Python and SQLite versions; schema version and applied migrations; database size; data folder; integrity result; backup list; "Create backup now". No stored owner profile (E3). | 1 |

### 10.2 Interaction conventions

- Every ID (event, session, task, agent, file, report, finding) is a link to its detail view.
- Lists open full-page detail views with breadcrumbs. Pages are deep-linkable and usable on mobile. Dialogs are used only for confirmations.
- "Load more" pagination, newest first.
- Auto-refresh every 5 seconds only while the tab is visible, with a pause control.
- Keyboard: every control is reachable; Enter opens a focused row; Esc closes dialogs; focus moves to the page heading after navigation; a skip link is provided.
- Themes: light, dark, and follow-system (default). Contrast meets WCAG AA. Status is never shown by colour alone.
- No charts in version 1. Counts, short lists and plain tables only.

### 10.3 Phase 5 specifics

- **Documentation** (FR-049, DEC-010):
  - Documents are shown as **escaped plain text** in a monospace, wrapped view. Nothing is interpreted:
    Markdown symbols, HTML tags and links appear exactly as written, and links are not clickable. Mermaid
    diagrams therefore appear as their source text, and the traceability matrix as its Markdown table.
  - A metadata panel shows the document type, the version and status declared in the document, the file's
    Git history (read-only `git log` for that path) and its approval state from the Approval Centre.
  - Requirement IDs (FR-, NFR-, CON-) can be indexed from the SRS with their status as written (FR-050, Could).
  - Version 1 has no Markdown renderer. Adding one would need a separate owner decision and its own security tests.
- **Testing**:
  - Sources and labels:
    - agent test reports: *agent-reported*;
    - shell commands that match known test runners (for example `pytest`, `npm test`), with their exit
      status, seen by hooks: *observed*;
    - test-runner files (for example JUnit XML) chosen by the owner from inside the project (FR-053, Could
      priority): *verified* or *test-runner file, origin not verified* (rule below).
  - **Test-runner file rule (E1, FR-054).** A test-runner file is labelled `verified` only when both are true:
    1. a hook observed a test-runner shell command complete (PostToolUse or PostToolUseFailure) in the same project;
    2. the file's last-modified time falls inside that command's run window (from its PreToolUse event to its
       completion event), with a tolerance of 2 seconds either side.

    Otherwise it is labelled `file_origin_unverified`, shown as *Test-runner file, origin not verified*. The
    matching command is linked from the run. Reason: any agent with write access could write a fake result
    file; a matching observed command makes that much less likely, though not impossible (section 15).
  - Proposed tests are listed separately and never counted as executed (also enforced by the database).
  - A reported executed command is compared with observed commands in the same session: "observed run matches" or "no matching observed run".
  - Only `verified` and `observed` runs count for release readiness. Agent-reported runs and unverified
    test-runner files are shown, but they do not clear the "no executed tests" blocker.
- **Security**:
  - Severities: Critical, High, Medium, Low, Informational.
  - Statuses come from the findings register exactly as written: Open, In remediation, Fixed - pending verification, Verified, Risk accepted, False positive.
  - The latest audit verdict is shown as agent-reported.
  - Permanent notice: "AgentDesk never declares a project secure. No findings means none were recorded within the audited scope."
- **Approvals**:
  - AgentDesk creates *review requests* from facts: reports marked `Pending user approval`, new document
    versions, dependency manifest changes seen in Git (for example `requirements*.txt`, `pyproject.toml`,
    `package.json`, lock files), findings in `Fixed - pending verification`, and a manually requested release review.
  - Only a person decides. Each decision records the person's typed name (never the Windows account name,
    DEC-009), the time, and the exact version (content hash or commit) it applies to.
  - Decided approvals cannot be edited or deleted (database triggers). Changing a decision creates a new record.
  - An approval whose subject has changed since shows "approved version is outdated".
  - Approvals that the orchestrator recorded in project files are shown separately as "recorded in project files", and mismatches are flagged.
  - AgentDesk does not write decisions into project files. A "Copy decision" button produces a one-line statement the owner can give to Claude Code.
- **File-change reviews** (E2, FR-059; arrives with the Approval Centre in Phase 5):
  - In the File Change Explorer the owner can mark a Git-verified change as *Reviewed*: **accepted**, or
    **changes requested**, with their typed name, the time and an optional note.
  - The review is stored as an approval record (`subject_type = 'file_change_review'`) pinned to the project,
    the path and the file's content fingerprint. For a deleted file there is no content, so the pin is a
    deletion marker plus the HEAD commit (`deleted@<commit>`).
  - A review never changes the evidence label. An UNATTRIBUTED change stays UNATTRIBUTED and shows
    "Reviewed by &lt;name&gt; on &lt;date&gt; for this version".
  - If the file's content changes later (different fingerprint), the review shows as outdated.
- **Release readiness** (Overview):
  - Blockers mirror the tracking protocol's completion rules:
    - open Critical or High findings without a recorded risk acceptance;
    - no `verified` or `observed` test run, or a failed latest such run;
    - pending approvals;
    - Git-verified UNATTRIBUTED changes without an *accepted* review of their current version (a "changes
      requested" review keeps the blocker: SRS assumption A-7, question Q12);
    - a missing audit or a NOT READY verdict.
  - Possible states: "Not ready (N blockers)", "No blockers found, awaiting human release approval",
    "Release approved by &lt;name&gt; on &lt;date&gt; for commit &lt;hash&gt;". Never "secure", never ready on its own.

## 11. Security and privacy

| Area | Control |
|---|---|
| Network | Binds to 127.0.0.1 by default. Non-loopback host settings are refused at startup. |
| DNS rebinding | Host header allowlist (`127.0.0.1:<port>`, `localhost:<port>`, `[::1]:<port>`), otherwise 400 |
| Cross-site requests | No CORS headers. State-changing requests need `Content-Type: application/json`, a same-origin or absent `Origin`, and a per-start CSRF token in `X-AgentDesk-CSRF` |
| Hook ingestion | Requires the ingest token from `data/ingest_token` (random, created at first start); payloads validated and re-sanitized server-side |
| Browser hardening | Content-Security-Policy `default-src 'self'` with no inline scripts; `X-Content-Type-Options: nosniff`; `Referrer-Policy: no-referrer`; framing denied; `Cache-Control: no-store` on the API |
| Project folders | Drive roots, `C:\Users`, user-profile roots (including the home folder), Windows and program folders and AgentDesk's data folder are refused as projects; an enclosing Git repository rooted at such a location is never used (section 7, FR-022) |
| File access | Every project path must resolve inside a registered project root after resolving `..`, symlinks and junctions; size caps; binary detection |
| Sensitive files | The diff and file viewers refuse `.env*`, `*.pem`, `*.key`, `*.pfx`, `*.p12`, `id_rsa*`, `id_ed25519*`, `credentials*`, `secrets.*`, and any file inside AgentDesk's own data folder (for example `ingest_token`), which matters when AgentDesk monitors its own repository |
| Identity | Approvals and confirmations record the name the owner types; AgentDesk stores no owner profile and never reads the Windows account name (DEC-009) |
| Git | Fixed allowlist of read-only subcommands with argument lists (no shell), `GIT_OPTIONAL_LOCKS=0`, `-c core.fsmonitor=false`, `--no-ext-diff`, `--no-textconv`, timeouts. Prevents repository config from running programs and avoids touching the index lock. |
| Commands | No command from an event, report or browser input is ever executed |
| Wizard writes | Server builds hook entries itself; target restricted to two file names inside a registered project; preview hash binding; backup; atomic write; audit record |
| Folder browser | Read-only, folder names only, CSRF-protected |
| Data at rest | No secrets, file contents or prompts stored; redaction on all free text; reports and diffs read live |
| Errors | JSON errors without stack traces; details in `data/logs/` |

### 11.1 Development process: strictly read-only security review and its limitation

This concerns how AgentDesk is *built*, not the running product (OD-16 as corrected by the owner, OC-1;
DEC-016; CON-012).

- For AgentDesk work, `security-audit-agent` must not modify anything: no application code, no documentation
  (including its own audit report, `docs/security/findings-register.md` and the activity log), no
  configuration, no global agent definitions and no project settings.
- It returns its full audit report in its final answer. The orchestrator then:
  - saves that report verbatim to `docs/security/audit-reports/<TaskID>.md`;
  - updates the findings register;
  - adds the log entry;

  each labelled "recorded by orchestrator from security-audit-agent's returned report".
- The orchestrator records `git status` before and after each security task. Any difference counts as a
  discrepancy and is reported to the owner.
- **Limitation.** The agent's global definition still includes the Write and Edit tools, and it is not changed.
  The read-only boundary therefore rests on instructions and is checked by Git after the fact. It is not
  prevented. Changes Git cannot see (for example in ignored files or outside the repository) would not be
  detected by this check.

## 12. Reliability and operations

- **SQLite**: WAL mode, `foreign_keys=ON`, `busy_timeout=5000`, one connection per request, explicit transactions.
- **Migrations**: numbered SQL files, applied in order at startup, each in its own transaction. Applied files
  are checksummed; an edited applied migration stops startup with a clear message. Backup before any migration.
- **Backups**: SQLite online backup API to `data/backups/`: at startup (if the last backup is over 24 hours old),
  before migrations, and on demand (Settings or `scripts/backup_db.py`). Each backup is integrity-checked; the newest 10 are kept.
- **Recovery**: `PRAGMA quick_check` at startup. A damaged database is never deleted or overwritten:
  AgentDesk refuses to start and explains how to restore with `scripts/restore_db.py`, which keeps the damaged file as `pre-restore-<time>.db`.
- **Logs**: `data/logs/agentdesk.log` (rotating, 1 MB x 5) and `data/logs/hook.log` (capped). No request bodies or secrets.
- **Retention**: nothing is deleted automatically in version 1. Settings shows the database size.

## 13. Project structure

```
agentdesk/
  app/
    __init__.py  __main__.py  main.py
    api/                 REST routers (one file per area)
    core/                config, log_setup, security, timeutil (+ redaction in Phase 3)
    models/              Pydantic schemas
    services/            business logic                                   (Phase 3+)
    integrations/
      git/               read-only git runner and parsers                 (Phase 3)
      tracking/          change-tracking Markdown parsers                 (Phase 3, 5)
      claude_code/       hook payload normalizer, settings inspector/merger (Phase 4)
    database/            connection, migrations runner, backup
    static/              index.html, favicon.svg, css/app.css, js/ (app, router, api, dom, theme, pages/)
  hooks/agentdesk_hook.py                                                  (Phase 4)
  migrations/            0001_foundation.sql, ...
  tests/
  docs/                  architecture, schema, plan, agent-activity/, decisions/, testing/, security/
  scripts/               setup.bat, start.bat, backup_db.py, restore_db.py
  data/                  gitignored: agentdesk.db, backups/, logs/, spool/, connection-backups/, ingest_token
  <dependency files: format open, Q10>  pytest.ini  README.md  CHANGELOG.md  .gitignore
```

Changes from the original brief's suggested structure:
- No `app/templates/`: a single static page needs no server-side templating, which avoids a Jinja2 dependency.
- An added `app/integrations/tracking/` for the agents' tracking files.
- Packages are created when they first receive code (no empty placeholders).

## 14. Dependencies

| Kind | Packages |
|---|---|
| Runtime | `fastapi==0.162.0`, `uvicorn==0.54.0` (Windows wheels for Python 3.15 confirmed by a pip dry run) |
| Development | `pytest==9.2.0`, `httpx==0.28.1` |
| Frontend | None |
| External programs | Python 3.12 or newer (developed on 3.15.2), Git (2.53 installed), Claude Code for hooks (2.1.314 installed) |

The hook script uses only the Python standard library. SQLite 3.53.4 (bundled with Python 3.15.2) supports the `STRICT` tables and JSON functions used by the schema.

**Open question Q10 (OD-14).** How the pinned versions are written down (the dependency file format, and
whether a lock file is used) is not decided. The orchestrator explains the simplest reproducible approach and
its maintenance cost; the owner chooses before Phase 1 installs anything (TASK-002, TASK-003). The package
versions above are fixed either way.

## 15. Known limitations

1. **Agent identity exists only inside subagents.** Work done directly by the main conversation shows as "Main session", even if it was told to act as one of the four roles (unless the session was started with `claude --agent <name>`).
2. **Shell commands hide their file effects.** Changes made by `npm install`, formatters, generators or `sed` can only be Unattributed.
3. **Parallel work** (several subagents, several sessions, the owner's editor) shares one working tree. Only explicit file tool events link a file to an agent.
4. **Diffs are cumulative.** If several parties edit one file, Git cannot split the diff by author, and AgentDesk does not store snapshots to do so.
5. **Renames** are detected only for staged files. AgentDesk never stages, so unstaged renames appear as a deletion plus a new file.
6. **Missed events.** A killed terminal or crash sends no SessionEnd or SubagentStop. Sessions and runs become stale or unknown instead of appearing active. Async hooks can arrive slightly out of order. The spool covers server downtime, not a killed hook process.
7. **Run-to-subagent links** are inferred unless both carry the same task ID.
8. **Coverage.** Hooks run only in sessions started after installation, in folders the owner has trusted in Claude Code. MCP tools that write files may not expose paths in a known form. Other editors and AI tools appear only through Git.
9. **"Why" a change was made** comes only from real sources (task description, reports, commit messages). Otherwise it stays empty.
10. **Approvals are records, not enforcement.** AgentDesk does not stop Claude Code from acting.
11. **Tracking files are claims.** Anyone can edit them. AgentDesk parses the protocol's templates and default paths only.
12. **Redaction is best effort.** Content-bearing fields are therefore dropped, not redacted.
13. **Folder selection** uses a server-side folder browser, because browsers do not expose real paths.
14. **Settings-file race.** Claude Code may write `settings.local.json` while the wizard installs. The preview-hash check and the advice to close sessions reduce, but cannot fully remove, this risk.
15. **Home and drive-root folders are refused** (OD-17, E6). On this PC the home folder `C:\Users\Charvik` is a
    Git repository with no commits. A project folder inside the home folder that is not its own Git repository
    is therefore registered as "Not a Git repository": AgentDesk will not use the home repository, and Git-verified
    changes are unavailable until the owner runs `git init` in the project folder. AgentDesk never modifies the
    home repository.
16. **Test-runner file verification is strong evidence, not proof.** It relies on an observed test command and the
    file's modification time. An agent that runs a real test command could still alter the result file inside
    that command's run window, and file times can be changed. Unverified files are never counted (section 10.3).
17. **Read-only security review is an instruction, not a permission** (section 11.1). `security-audit-agent` keeps
    the Write and Edit tools in its global definition. Unexpected changes are detected afterwards by the
    orchestrator's `git status` comparison, not prevented, and changes Git cannot see are not detected.
18. **Rate-limited checkpoints** (section 6.6). Within a 10-second window, intermediate states are merged into one
    trailing checkpoint, so a file changed and changed back inside the window may not appear.
19. **File-change reviews apply to one version.** Any later edit to the file makes the review outdated, even a
    harmless one; the owner then reviews again.

## 16. Decision register

All decisions below are **Proposed**: the owner has approved none of them yet (OD-15, OD-18). DEC-001 to DEC-012
are the recommended options from the 2026-10-30 proposal, adjusted by refinements R1-R12; for DEC-007 to
DEC-012 the owner has already stated a preference (OD-3 to OD-8). DEC-013 to DEC-017 record the owner's process
choices. No decision file exists yet: `docs/decisions/DEC-###-<slug>.md` files are created only after the owner
explicitly approves the decision.

| ID | Decision | Status | Source |
|---|---|---|---|
| DEC-001 | Stack: FastAPI + Python `sqlite3` with plain SQL (no ORM) + vanilla JS ES modules without a build step | Proposed | Brief §2, R1 |
| DEC-002 | Hook transport: standard-library Python command hook; async for tool events, synchronous (5 s) for lifecycle events; offline spool | Proposed | Brief §5 |
| DEC-003 | Hook settings go to `.claude/settings.local.json` by default; `.claude/settings.json` only by explicit choice in the wizard | Proposed | Brief §5, R3 |
| DEC-004 | Evidence model: five labels, two axes, classification computed on read, no attribution by timing (section 5) | Proposed | R5, R6, FU-6 |
| DEC-005 | Diffs and reports are read live from the project; the database stores facts, fingerprints and redacted summaries only | Proposed | Brief §7 |
| DEC-006 | Read-only boundary toward monitored projects; the wizard's previewed and confirmed settings write is the only exception | Proposed | R8 |
| DEC-007 | Shell commands stored after secret redaction, truncated to 200 characters | Proposed; owner preference recorded (OD-3) | OD-3 |
| DEC-008 | At most 1 KB (1,024 characters) of a subagent's final message is stored, redacted, with its task ID and report path, labelled agent-reported | Proposed; owner preference recorded (OD-4) | OD-4 |
| DEC-009 | Approvals and confirmations record the name the owner types; no stored owner profile; the Windows account name is never recorded | Proposed; owner preference recorded (OD-5) | OD-5, E3 |
| DEC-010 | No chart or diagram libraries and no custom Markdown renderer in version 1; documents are shown as escaped plain text with metadata. A renderer would need a separate future decision with security tests | Proposed; owner preference recorded (OD-6) | OD-6 |
| DEC-011 | Schema grows by phase: each feature's tables arrive in its own migration | Proposed; owner preference recorded (OD-7) | OD-7, R2 |
| DEC-012 | Hook installation through the dashboard wizard with an explicit preview and confirmation (and backup), replacing the earlier command-line-only proposal | Proposed; owner preference recorded (OD-8) | OD-8, R3 |
| DEC-013 | Option B workflow: the Planner maintains requirements, traceability, design documents and task planning; the Developer implements the approved phase and writes the initial tests; the Testing Agent independently reviews, adds edge cases and executes; the Security Audit Agent reviews read-only; the owner approves each phase | Proposed | OD-1, OD-10, OD-11 |
| DEC-014 | GUI verification through a manual browser checklist run by the owner; no Chrome extension or browser automation | Proposed | OD-2 |
| DEC-015 | No automatic stage, commit, push, deploy or discard, by AgentDesk or by any agent; the owner commits | Proposed | OD-12 |
| DEC-016 | `security-audit-agent` is strictly read-only for AgentDesk work and modifies no file; it returns its full report, which the orchestrator records verbatim (audit report, findings register, log entry, each labelled as recorded by the orchestrator); `git status` is compared before and after each security task. Limitation: its global definition keeps Write and Edit and is not changed, so the boundary rests on instructions and is checked by Git afterwards, not prevented (section 11.1) | Proposed | OD-16, OC-1 |
| DEC-017 | Global Claude Code settings and agent names are read only when a later feature requires it, strictly read-only: only in the Phase 4 wizard configuration check, limited to `disableAllHooks`, hook counts and agent names | Proposed | OD-13 |
