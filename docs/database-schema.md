# AgentDesk: database schema

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Baselined |
| Last updated | 2026-10-30 |
| Task ID | T-20261030-001-PLN-2 (maintained by planner-agent, OD-10) |
| Related documents | [srs.md](srs.md), [architecture.md](architecture.md), [implementation-plan.md](implementation-plan.md), [traceability-matrix.md](traceability-matrix.md) |

## Revision history

| Version | Date | Task ID | Change | Requirement IDs | Approved by |
|---|---|---|---|---|---|
| 0.1 | 2026-10-30 | T-20261030-001-ORC | Single up-front schema, presented in conversation | - | Accepted in principle by the project owner |
| 0.2 | 2026-10-30 | T-20261030-001-ORC | Split into phased migrations (R2); Phase 1 reduced to two tables; attribution is no longer stored (computed on read); tables added for agent reports and project connections; finding statuses aligned with the agents' findings register; database-enforced separation of proposed and executed tests; immutable approvals | R2 | Pending |
| 0.3 | 2026-10-30 | T-20261030-001-PLN | Status Draft (E4, OD-18). Removed the planned `owner_display_name` setting (E3, OD-5). `agent_reports.summary` limited to 1,024 characters for subagent final messages (OD-4). `test_runs`: source `junit_xml` renamed `test_runner_file`, new verification value `file_origin_unverified`, new `artifact_mtime` column, CHECKs pairing source and verification (E1). `approvals.subject_type` gains `file_change_review`, with pinning rules for fingerprints and deleted files (E2); subject index now includes the project. Phase 1 DDL unchanged. | E1-E4, OD-4, OD-5; FR-045, FR-053, FR-054, FR-059, FR-060 | Pending |
| 1.0 | 2026-10-30 | T-20261030-001-PLN-2 | Baseline. No DDL change. Phase 1 DDL approved for implementation; Phases 3-5 DDL stays the planned design and is finalized at each phase start (TASK-036, TASK-051, TASK-066). A-7 and the 2-second tolerance confirmed (DEC-019). | All requirements; FR-054, FR-059, FR-060 | The owner, 2026-10-30 (blanket authorization, OA); DEC-019 under the owner's delegated authority |

## 1. Conventions

| Topic | Rule |
|---|---|
| Engine | SQLite 3.53 (bundled with Python 3.15.2), file `data/agentdesk.db` |
| Table type | `STRICT` tables (SQLite enforces column types) |
| Primary keys | `TEXT`: a short prefix plus 32 hex characters from a random UUID, for example `evt_3f2a...`. Exception: `sessions.id` is Claude Code's own `session_id`. |
| Timestamps | `TEXT`, ISO 8601 UTC with milliseconds, for example `2026-10-30T12:07:19.123Z`. Shown in local time in the UI. |
| Booleans | `INTEGER` with `CHECK (x IN (0,1))` |
| Fixed value sets | `TEXT` with a `CHECK (x IN (...))` constraint |
| JSON | `TEXT` with `CHECK (json_valid(x))` and a size limit |
| Paths | Project-relative with forward slashes. Absolute only for project roots and for paths outside a project. |
| Foreign keys | `PRAGMA foreign_keys=ON`. No cascading deletes of audit data. Projects are archived, not deleted. |
| Facts, not conclusions | Evidence classification (OBSERVED, UNATTRIBUTED, ...) is computed when viewed, never stored |
| Content | No file contents, prompts, tool output or secrets. Free text is redacted and length-limited. |
| Migrations | `migrations/NNNN_<name>.sql`, applied in order at startup, each in its own transaction. Checksums of applied files are stored; an applied file must never be edited. |

## 2. Migrations by phase

| Migration | Phase | Tables | Total tables after |
|---|---|---|---|
| (runner bootstrap) | 1 | `schema_migrations` | 1 |
| `0001_foundation.sql` | 1 | `app_settings` | 2 |
| `0002_projects_activity.sql` | 3 | `projects`, `activity_events` | 4 |
| `0003_git_tracking.sql` | 3 | `git_checkpoints`, `file_changes` | 6 |
| `0004_agent_reports.sql` | 3 | `agent_reports`, `report_items` | 8 |
| `0005_claude_code.sql` | 4 | `agents` (4 core rows seeded), `sessions`, `tasks`, `project_connections` | 12 |
| `0006_documents.sql` | 5 | `documents`, `requirements` | 14 |
| `0007_testing.sql` | 5 | `test_runs`, `test_cases` | 16 |
| `0008_security.sql` | 5 | `security_findings` | 17 |
| `0009_approvals.sql` | 5 | `approvals` (with immutability triggers; also holds file-change reviews) | 18 |

Every table named in the original brief (projects, sessions, agents, tasks, activity_events, file_changes,
documents, requirements, test_runs, test_cases, security_findings, approvals) is present by the end of Phase 5.

**Only the Phase 1 DDL below is ready for implementation** (approved by the owner on 2026-10-30, OA). Later
migrations are the planned design. Each is finalized, and this document updated with a new MINOR version, when
its phase starts (TASK-036 for `0002`-`0004`, TASK-051 for `0005`, TASK-066 for `0006`-`0009`). Once a migration
file has been applied anywhere, it is never edited; corrections go into a new migration.

## 3. Phase 1 (ready for implementation)

### Runner bootstrap

Created by the migration runner itself before any migration file runs, because the runner needs it to know what has been applied.

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,           -- 1 for 0001_foundation.sql
    name        TEXT    NOT NULL,              -- 'foundation'
    checksum    TEXT    NOT NULL,              -- SHA-256 of the migration file
    applied_at  TEXT    NOT NULL
) STRICT;
```

### `0001_foundation.sql`

```sql
CREATE TABLE app_settings (
    key         TEXT PRIMARY KEY CHECK (length(key) BETWEEN 1 AND 64),
    value       TEXT NOT NULL    CHECK (length(value) <= 4096),
    updated_at  TEXT NOT NULL
) STRICT;
```

Keys written in Phase 1: `instance_id` (random, created at first start) and `created_at`.

No owner profile is stored, in any phase (E3, DEC-009). The owner types their name for each decision; the
browser may remember the last typed value in its own local storage, never in this database.

## 4. Phase 3 (planned)

### `0002_projects_activity.sql`

```sql
CREATE TABLE projects (
    id           TEXT PRIMARY KEY,                       -- prj_...
    name         TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 200),
    root_path    TEXT NOT NULL,                          -- absolute, resolved, as displayed
    root_key     TEXT NOT NULL UNIQUE,                   -- lower-case, forward slashes: Windows-safe matching
    is_git_repo  INTEGER NOT NULL CHECK (is_git_repo IN (0,1)),
    status       TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
) STRICT;

CREATE TABLE activity_events (
    id                 TEXT PRIMARY KEY,                 -- evt_...
    event_uuid         TEXT NOT NULL UNIQUE,             -- set by the producer: spool replay is idempotent
    project_id         TEXT REFERENCES projects(id),     -- NULL: could not be matched to a project
    session_id         TEXT,                             -- Claude session id. No FK: events may arrive before
    agent_instance_id  TEXT,                             --   their session row (async hooks)
    agent_type         TEXT,                             -- e.g. 'developer-agent'; NULL = main session / unknown
    task_key           TEXT,                             -- 'T-YYYYMMDD-NNN-ROLE' when known
    event_type         TEXT NOT NULL,                    -- normalized: tool_started, tool_succeeded, project_registered, ...
    hook_event_name    TEXT,                             -- raw Claude Code event name
    tool_name          TEXT,
    tool_use_id        TEXT,
    file_path          TEXT,
    summary            TEXT NOT NULL CHECK (length(summary) <= 500),
    details_json       TEXT NOT NULL DEFAULT '{}'
                       CHECK (json_valid(details_json) AND length(details_json) <= 4096),
    source             TEXT NOT NULL CHECK (source IN
                       ('claude_code_hook','git','tracking_file','manual_report','agentdesk','api','selftest')),
    verification       TEXT NOT NULL CHECK (verification IN
                       ('observed','verified','agent_reported','human','system')),
    occurred_at        TEXT NOT NULL,
    received_at        TEXT NOT NULL
) STRICT;

CREATE INDEX ix_events_project_time ON activity_events(project_id, occurred_at);
CREATE INDEX ix_events_session      ON activity_events(session_id, occurred_at);
CREATE INDEX ix_events_agent        ON activity_events(agent_type, occurred_at);
CREATE INDEX ix_events_type         ON activity_events(event_type, occurred_at);
CREATE INDEX ix_events_file         ON activity_events(project_id, file_path);
CREATE INDEX ix_events_task         ON activity_events(task_key);
CREATE INDEX ix_events_tool_use     ON activity_events(tool_use_id);
```

### `0003_git_tracking.sql`

```sql
CREATE TABLE git_checkpoints (
    id             TEXT PRIMARY KEY,                     -- chk_...
    project_id     TEXT NOT NULL REFERENCES projects(id),
    session_id     TEXT,                                 -- set when a session event triggered it
    trigger        TEXT NOT NULL CHECK (trigger IN
                   ('project_registered','manual','session_start','subagent_stop','stop','session_end')),
    branch         TEXT,
    head_commit    TEXT,                                 -- NULL in a repository without commits
    changed_count  INTEGER NOT NULL,
    truncated      INTEGER NOT NULL DEFAULT 0 CHECK (truncated IN (0,1)),   -- over 5,000 changed files
    taken_at       TEXT NOT NULL
) STRICT;

CREATE INDEX ix_checkpoints_project_time ON git_checkpoints(project_id, taken_at);
CREATE INDEX ix_checkpoints_session      ON git_checkpoints(session_id);
-- Automatic checkpoints (stop, subagent_stop, session_end) are limited by the server to one per project per
-- 10 seconds, with one trailing checkpoint per window (architecture section 6.6, E7). The database does not
-- enforce this. 'project_registered', 'session_start' and 'manual' are always taken.

-- One row per changed file per checkpoint. Git facts only: no attribution, no content.
CREATE TABLE file_changes (
    id             TEXT PRIMARY KEY,                     -- fch_...
    checkpoint_id  TEXT NOT NULL REFERENCES git_checkpoints(id),
    project_id     TEXT NOT NULL REFERENCES projects(id),
    path           TEXT NOT NULL,
    old_path       TEXT,                                 -- staged renames only
    change_type    TEXT NOT NULL CHECK (change_type IN
                   ('added','modified','deleted','renamed','untracked','type_changed','conflicted')),
    staged         INTEGER NOT NULL CHECK (staged IN (0,1)),
    additions      INTEGER,                              -- NULL for binary or unknown
    deletions      INTEGER,
    is_binary      INTEGER NOT NULL CHECK (is_binary IN (0,1)),
    fingerprint    TEXT,                                 -- `git hash-object` of the working file (without -w,
                                                         -- so nothing is written to .git); NULL if deleted
    UNIQUE (checkpoint_id, path)
) STRICT;

CREATE INDEX ix_file_changes_project_path ON file_changes(project_id, path);
```

How the five categories are derived from these facts, at query time:
- **GIT-VERIFIED**: the path has a row in the latest checkpoint, or differs between the baseline and the latest checkpoint.
- **PRE-EXISTING**: the path's fingerprint in the window's baseline checkpoint equals the current fingerprint.
- **OBSERVED**: a matching `activity_events` row exists (`source='claude_code_hook'`, file tool, `event_type='tool_succeeded'`, same project and path, after the baseline).
- **AGENT-REPORTED**: a matching `report_items` row exists (`kind='file_change'`, same path, report in the same project).
- **UNATTRIBUTED**: Git-verified and neither of the previous two.

### `0004_agent_reports.sql`

```sql
CREATE TABLE agent_reports (
    id               TEXT PRIMARY KEY,                   -- rpt_...
    project_id       TEXT NOT NULL REFERENCES projects(id),
    source           TEXT NOT NULL CHECK (source IN ('tracking_file','manual_paste','subagent_final_message')),
    source_path      TEXT,                               -- tracking file, project-relative
    content_hash     TEXT NOT NULL,                      -- skip unchanged files; detect edits
    report_type      TEXT NOT NULL CHECK (report_type IN
                     ('change','test','audit','activity_log_entry','findings_register','decision','free_text')),
    task_key         TEXT,                               -- as written: 'T-20261030-002-DEV'
    work_item_key    TEXT,                               -- 'T-20261030-002'
    agent_name       TEXT,                               -- as written: 'developer-agent'
    session_id       TEXT,
    reported_at      TEXT,                               -- date/time as written (may be 'time unavailable')
    reported_status  TEXT,                               -- as written: 'Awaiting validation', ...
    approval_text    TEXT CHECK (length(approval_text) <= 500),   -- as written in the Approval field/section
    title            TEXT CHECK (length(title) <= 300),
    summary          TEXT CHECK (length(summary) <= 8192),       -- redacted excerpt; full text read live
    parse_status     TEXT NOT NULL CHECK (parse_status IN ('parsed','partial','unrecognized')),
    submitted_by     TEXT,                               -- name typed by the person, manual pastes only
    ingested_at      TEXT NOT NULL,
    superseded_by    TEXT REFERENCES agent_reports(id),  -- a changed tracking file creates a new row
    -- DEC-008 (OD-4): at most 1 KB of a subagent's final message is kept
    CHECK (source <> 'subagent_final_message' OR length(summary) <= 1024)
) STRICT;

CREATE INDEX ix_reports_project_task ON agent_reports(project_id, task_key);
CREATE INDEX ix_reports_work_item    ON agent_reports(project_id, work_item_key);
CREATE UNIQUE INDEX ux_reports_file_version
    ON agent_reports(project_id, source_path, content_hash) WHERE source_path IS NOT NULL;

CREATE TABLE report_items (
    id           TEXT PRIMARY KEY,                       -- rit_...
    report_id    TEXT NOT NULL REFERENCES agent_reports(id),
    kind         TEXT NOT NULL CHECK (kind IN ('file_change','validation','test_case','finding','note')),
    path         TEXT,                                   -- file_change path or finding location
    change_type  TEXT,                                   -- as written: A / M / D / R / reviewed
    reason       TEXT CHECK (length(reason) <= 1000),
    data_json    TEXT NOT NULL DEFAULT '{}'
                 CHECK (json_valid(data_json) AND length(data_json) <= 4096)
) STRICT;

CREATE INDEX ix_report_items_report ON report_items(report_id);
CREATE INDEX ix_report_items_path   ON report_items(path);
```

## 5. Phase 4 (planned)

### `0005_claude_code.sql`

```sql
CREATE TABLE agents (                                    -- the four core profiles and their Claude Code names
    id                 TEXT PRIMARY KEY,                 -- agt_planner, agt_developer, agt_testing, agt_security
    key                TEXT NOT NULL UNIQUE,             -- planner | developer | testing | security
    display_name       TEXT NOT NULL,
    claude_agent_type  TEXT NOT NULL UNIQUE,             -- name in hook events, e.g. 'planner-agent'
    responsibilities   TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(responsibilities)),
    created_at         TEXT NOT NULL
) STRICT;
-- Seeded with planner-agent, developer-agent, testing-agent, security-audit-agent.
-- Other agent types seen in events (Explore, general-purpose, ...) are listed from activity_events,
-- not stored here. A profile is never shown as active just because it exists.

CREATE TABLE sessions (
    id               TEXT PRIMARY KEY,                   -- Claude Code session_id
    project_id       TEXT REFERENCES projects(id),
    status           TEXT NOT NULL CHECK (status IN ('active','ended','stale')),
    start_source     TEXT,                               -- startup | resume | clear | compact | fork
    model            TEXT,
    permission_mode  TEXT,
    started_at       TEXT,                               -- NULL if first seen mid-session
    ended_at         TEXT,
    end_reason       TEXT,
    last_event_at    TEXT NOT NULL
) STRICT;

CREATE INDEX ix_sessions_project_status ON sessions(project_id, status, last_event_at);

CREATE TABLE tasks (
    id                 TEXT PRIMARY KEY,                 -- tsk_...
    project_id         TEXT REFERENCES projects(id),
    session_id         TEXT,
    kind               TEXT NOT NULL CHECK (kind IN ('subagent_run','claude_task')),
    task_key           TEXT,                             -- from 'Task ID:' line of the delegation prompt
    agent_type         TEXT,
    agent_instance_id  TEXT,
    external_id        TEXT,                             -- Claude Code task_id (TaskCreated)
    title              TEXT CHECK (length(title) <= 300),
    title_source       TEXT CHECK (title_source IN ('agent_tool_description','task_subject')),
    status             TEXT NOT NULL CHECK (status IN ('running','completed','failed','unknown')),
    link_confidence    TEXT NOT NULL DEFAULT 'direct' CHECK (link_confidence IN ('direct','inferred')),
    started_at         TEXT,
    ended_at           TEXT,
    final_report_id    TEXT REFERENCES agent_reports(id)
) STRICT;

CREATE INDEX ix_tasks_project_status ON tasks(project_id, status);
CREATE INDEX ix_tasks_session        ON tasks(session_id);
CREATE INDEX ix_tasks_key            ON tasks(task_key);

CREATE TABLE project_connections (                       -- one row per install; history kept
    id                TEXT PRIMARY KEY,                  -- con_...
    project_id        TEXT NOT NULL REFERENCES projects(id),
    settings_file     TEXT NOT NULL CHECK (settings_file IN ('local','shared')),
    status            TEXT NOT NULL CHECK (status IN ('installed','removed')),
    created_file      INTEGER NOT NULL CHECK (created_file IN (0,1)),  -- AgentDesk created the file
    hook_script_path  TEXT NOT NULL,
    python_path       TEXT NOT NULL,
    events_json       TEXT NOT NULL CHECK (json_valid(events_json)),
    backup_path       TEXT,                              -- inside AgentDesk data/connection-backups/
    approved_by       TEXT NOT NULL,                     -- name typed at confirmation
    installed_at      TEXT NOT NULL,
    removed_by        TEXT,
    removed_at        TEXT,
    last_selftest_at  TEXT,
    last_selftest_ok  INTEGER CHECK (last_selftest_ok IN (0,1))
) STRICT;

CREATE INDEX ix_connections_project ON project_connections(project_id, status);
```

## 6. Phase 5 (planned)

### `0006_documents.sql`

```sql
CREATE TABLE documents (
    id                TEXT PRIMARY KEY,                  -- doc_...
    project_id        TEXT NOT NULL REFERENCES projects(id),
    path              TEXT NOT NULL,
    doc_type          TEXT NOT NULL CHECK (doc_type IN
                      ('srs','sdd','architecture','uml','data_flow','specification','traceability','decision','other')),
    title             TEXT,
    declared_version  TEXT,                              -- 'Version' as written in the document
    declared_status   TEXT,                              -- 'Status' as written (Draft, Baselined, ...)
    content_hash      TEXT NOT NULL,                     -- current version; approvals pin a hash
    last_seen_at      TEXT NOT NULL,
    UNIQUE (project_id, path)
) STRICT;

CREATE TABLE requirements (                              -- index of IDs found in the SRS
    id                TEXT PRIMARY KEY,                  -- req_...
    project_id        TEXT NOT NULL REFERENCES projects(id),
    req_key           TEXT NOT NULL,                     -- FR-001, NFR-002, CON-003
    req_type          TEXT NOT NULL CHECK (req_type IN ('FR','NFR','CON')),
    title             TEXT,
    priority          TEXT,                              -- as written (Must / Should / Could)
    declared_status   TEXT,                              -- as written in the SRS
    document_id       TEXT REFERENCES documents(id),
    last_seen_at      TEXT NOT NULL,
    UNIQUE (project_id, req_key)
) STRICT;
```

The traceability matrix is displayed from the planner's own document, so no link table is needed in version 1.
Document content is never stored: it is read live and shown as escaped plain text (DEC-010).

### `0007_testing.sql`

```sql
CREATE TABLE test_runs (
    id             TEXT PRIMARY KEY,                     -- trn_...
    project_id     TEXT NOT NULL REFERENCES projects(id),
    source         TEXT NOT NULL CHECK (source IN ('test_runner_file','hook_observed','agent_reported')),
    verification   TEXT NOT NULL CHECK (verification IN
                   ('verified','observed','agent_reported','file_origin_unverified')),
    report_id      TEXT REFERENCES agent_reports(id),    -- agent_reported
    event_id       TEXT REFERENCES activity_events(id),  -- hook_observed: the command; test_runner_file:
                                                         --   the observed command that verified the file
    artifact_path  TEXT,                                 -- test_runner_file, project-relative
    artifact_hash  TEXT,
    artifact_mtime TEXT,                                 -- file's last-modified time when imported
    session_id     TEXT,
    task_key       TEXT,
    agent_type     TEXT,
    command        TEXT CHECK (length(command) <= 200),  -- redacted
    exit_code      INTEGER,
    total          INTEGER,
    passed         INTEGER,
    failed         INTEGER,
    skipped        INTEGER,
    errors         INTEGER,
    started_at     TEXT,
    finished_at    TEXT,
    recorded_at    TEXT NOT NULL,
    -- E1: each source has its own possible labels
    CHECK ((source = 'hook_observed'    AND verification = 'observed') OR
           (source = 'agent_reported'   AND verification = 'agent_reported') OR
           (source = 'test_runner_file' AND verification IN ('verified','file_origin_unverified'))),
    -- a verified test-runner file must name the observed command that produced it
    CHECK (verification <> 'verified' OR event_id IS NOT NULL)
) STRICT;

CREATE INDEX ix_test_runs_project_time ON test_runs(project_id, recorded_at);

CREATE TABLE test_cases (
    id                TEXT PRIMARY KEY,                  -- tcs_...
    project_id        TEXT NOT NULL REFERENCES projects(id),
    test_run_id       TEXT REFERENCES test_runs(id),     -- NULL = proposed, not executed
    report_id         TEXT REFERENCES agent_reports(id),
    name              TEXT NOT NULL CHECK (length(name) <= 500),
    suite             TEXT,
    category          TEXT CHECK (category IN ('unit','integration','regression','edge','boundary','other')),
    requirement_keys  TEXT,                              -- FR-/NFR- IDs as written, comma-separated
    status            TEXT NOT NULL CHECK (status IN ('proposed','passed','failed','skipped','error')),
    duration_ms       INTEGER,
    failure_message   TEXT CHECK (length(failure_message) <= 2000),   -- redacted
    CHECK ((status = 'proposed') = (test_run_id IS NULL))  -- proposed tests can never look executed
) STRICT;

CREATE INDEX ix_test_cases_run            ON test_cases(test_run_id);
CREATE INDEX ix_test_cases_project_status ON test_cases(project_id, status);
```

Test-runner files (E1, FR-053, FR-054; Could priority):
- The label is decided when the file is imported, by the rule in architecture section 10.3: `verified` only if a
  hook observed a test-runner command complete in the same project and `artifact_mtime` lies inside that
  command's run window (2-second tolerance, DEC-019). Otherwise `file_origin_unverified`.
- A rescan re-checks rows still marked `file_origin_unverified` (an observed event may arrive late). A changed
  file (new `artifact_hash`) is imported as a new row.
- Release readiness counts only runs with `verification IN ('verified','observed')`.

### `0008_security.sql`

```sql
CREATE TABLE security_findings (                         -- index of the agents' findings register and audit reports
    id                     TEXT PRIMARY KEY,             -- fnd_...
    project_id             TEXT NOT NULL REFERENCES projects(id),
    finding_key            TEXT NOT NULL,                -- SEC-001
    title                  TEXT NOT NULL CHECK (length(title) <= 300),
    severity               TEXT NOT NULL CHECK (severity IN
                           ('critical','high','medium','low','informational')),
    location               TEXT,                         -- file:line as written
    description            TEXT CHECK (length(description) <= 4000),
    remediation            TEXT CHECK (length(remediation) <= 4000),
    references_text        TEXT CHECK (length(references_text) <= 500),   -- CWE / OWASP as written
    remediation_status     TEXT NOT NULL CHECK (remediation_status IN
                           ('open','in_remediation','fixed_pending_verification',
                            'verified','risk_accepted','false_positive')),
    found_in_task          TEXT,
    fixed_in_task          TEXT,
    verified_by            TEXT,
    verification_evidence  TEXT CHECK (length(verification_evidence) <= 2000),
    source_report_id       TEXT REFERENCES agent_reports(id),
    first_seen_at          TEXT NOT NULL,
    last_updated_at        TEXT NOT NULL,
    UNIQUE (project_id, finding_key)
) STRICT;

CREATE INDEX ix_findings_project_severity ON security_findings(project_id, severity, remediation_status);
```

Status values map one-to-one to the register's wording (Open, In remediation, Fixed - pending verification,
Verified, Risk accepted, False positive). Every row is agent-reported. A risk acceptance decided in AgentDesk
is an approval record (below), not an edit of this table.

### `0009_approvals.sql`

```sql
CREATE TABLE approvals (
    id               TEXT PRIMARY KEY,                   -- apr_...
    project_id       TEXT NOT NULL REFERENCES projects(id),
    subject_type     TEXT NOT NULL CHECK (subject_type IN
                     ('document','requirement_change','feature','code_change','dependency_change',
                      'security_remediation','risk_acceptance','release','file_change_review')),
    subject_ref      TEXT NOT NULL,                      -- document id, task key, finding key, file path, ...
    subject_version  TEXT NOT NULL,                      -- exact content hash or commit being decided;
                                                         --   file reviews: fingerprint or 'deleted@<commit>'
    title            TEXT NOT NULL CHECK (length(title) <= 300),
    evidence_json    TEXT NOT NULL DEFAULT '{}'
                     CHECK (json_valid(evidence_json) AND length(evidence_json) <= 8192),  -- what was shown
    status           TEXT NOT NULL CHECK (status IN
                     ('pending','approved','rejected','changes_requested','withdrawn')),
    requested_by     TEXT NOT NULL,                      -- 'agentdesk' (review request) or a person's name
    requested_at     TEXT NOT NULL,
    decided_by       TEXT CHECK (decided_by IS NULL OR decided_by <> 'agentdesk'),   -- only a person decides;
                                                         --   the name the person typed (DEC-009)
    decided_at       TEXT,
    comment          TEXT CHECK (length(comment) <= 2000),
    CHECK (status IN ('pending','withdrawn') OR (decided_by IS NOT NULL AND decided_at IS NOT NULL)),
    -- E2: a file-change review is created already decided: accepted (stored as 'approved') or changes requested
    CHECK (subject_type <> 'file_change_review' OR status IN ('approved','changes_requested'))
) STRICT;

CREATE INDEX ix_approvals_project_status ON approvals(project_id, status, requested_at);
CREATE INDEX ix_approvals_subject        ON approvals(project_id, subject_type, subject_ref);

CREATE TRIGGER approvals_decided_are_immutable
BEFORE UPDATE ON approvals
WHEN OLD.status <> 'pending'
BEGIN
    SELECT RAISE(ABORT, 'Decided approvals are immutable; create a new approval instead.');
END;

CREATE TRIGGER approvals_cannot_be_deleted
BEFORE DELETE ON approvals
BEGIN
    SELECT RAISE(ABORT, 'Approvals cannot be deleted.');
END;
```

**File-change reviews** (E2, FR-059). How a review is pinned to one version of one change:

| Column | Value for `subject_type = 'file_change_review'` |
|---|---|
| `project_id` | The project |
| `subject_ref` | Project-relative path, forward slashes (the same form as `file_changes.path`) |
| `subject_version` | The file's current content fingerprint (`file_changes.fingerprint`, from `git hash-object` without `-w`). For a deleted file, which has no content: `deleted@<head_commit>` using `git_checkpoints.head_commit` of the latest checkpoint, or `deleted@no-commit` in a repository without commits |
| `status` | `approved` (shown as "Reviewed: accepted") or `changes_requested` |
| `requested_by`, `decided_by` | The name the owner typed |
| `comment` | The optional note |

- **Current or outdated**: the review applies while the file's latest fingerprint (or deletion marker) equals
  `subject_version`. When the content changes, the newest review for that path shows as outdated.
- **Labels unchanged**: evidence labels are computed as before; the review is shown beside them.
- **Release readiness**: an UNATTRIBUTED change is cleared only by an `approved` review whose `subject_version`
  matches the current version (SRS assumption A-7, DEC-019).
- Reviews are immutable like all decided approvals; a new review creates a new row.

## 7. Relationships (overview)

```
projects 1--* activity_events        projects 1--* git_checkpoints 1--* file_changes
projects 1--* agent_reports 1--* report_items                 agent_reports 0..1--* tasks (final report)
projects 1--* sessions (by id)       projects 1--* tasks       projects 1--* project_connections
projects 1--* documents 1--* requirements                     projects 1--* security_findings
projects 1--* test_runs 1--* test_cases (executed); test_cases with no run = proposed
projects 1--* approvals (subject_type + subject_ref + subject_version point at any subject;
                         file_change_review: path + fingerprint or deletion marker)
agents: profile lookup by claude_agent_type, matched to activity_events.agent_type / tasks.agent_type
```

`session_id`, `agent_type`, `agent_instance_id` and `task_key` are plain references, not foreign keys, because
hook events can arrive before (or without) the rows they refer to. The service layer resolves them.
