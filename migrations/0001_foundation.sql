-- 0001_foundation: application settings (database-schema.md section 3).
-- Phase 1 stores two keys here: instance_id and created_at.
-- Never edit this file after it has been applied: AgentDesk checks its checksum at every start.

CREATE TABLE app_settings (
    key         TEXT PRIMARY KEY CHECK (length(key) BETWEEN 1 AND 64),
    value       TEXT NOT NULL    CHECK (length(value) <= 4096),
    updated_at  TEXT NOT NULL
) STRICT;
