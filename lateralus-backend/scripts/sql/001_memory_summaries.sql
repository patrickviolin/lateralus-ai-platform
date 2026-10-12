CREATE TABLE IF NOT EXISTS memory_summaries (
    thread_id TEXT NOT NULL,
    revision INTEGER NOT NULL,
    content TEXT NOT NULL,
    covers_through_message_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    tombstoned_at TIMESTAMPTZ,
    tombstone_reason TEXT,
    model TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    audience TEXT NOT NULL,
    kind TEXT NOT NULL,
    memory_agent TEXT NOT NULL,
    memory_agent_version TEXT NOT NULL,
    PRIMARY KEY (thread_id, revision)
);
