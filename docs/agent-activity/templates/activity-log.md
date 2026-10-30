# Agent activity log

Project: <name>
Task IDs: `T-YYYYMMDD-NNN-ROLE`, ROLE = PLN | DEV | TST | SEC | ORC. All agents on one work item share `T-YYYYMMDD-NNN`.

## Summary

Maintained by the orchestrator only. One row per work item.

| Work item | Title | Requirements | PLN | DEV | TST | SEC | Validation | Open findings | Approval | Status |
|---|---|---|---|---|---|---|---|---|---|---|

## Log

Newest first. Append-only: add each entry directly below the marker line; never edit or delete an existing entry.

<!--
Entry format:

### T-YYYYMMDD-NNN-ROLE | <agent> | YYYY-MM-DDTHH:MM:SS+hhmm
- Task: <one line>
- Related tasks: <IDs or none>
- Requirements/issues: <IDs or none>
- Files: A <path>; M <path>; D <path> (or none)
- Validation: `<command>` -> <actual result> (or none)
- Remaining issues: <list or none>
- Status: Awaiting validation | Awaiting approval | Blocked
- Approval: Pending user approval
- Report: <relative path to report file>
-->

<!-- NEW LOG ENTRIES BELOW THIS LINE -->
