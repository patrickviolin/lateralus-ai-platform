CREATE UNIQUE INDEX IF NOT EXISTS uq_memory_summaries_coverage
ON memory_summaries (thread_id, covers_through_message_id);
