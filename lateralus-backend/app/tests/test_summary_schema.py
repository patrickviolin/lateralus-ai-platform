from app.domain.schemas import MemorySummaries


def test_summary_entity_matches_database_migration():
    assert MemorySummaries.__tablename__ == "memory_summaries"
    assert {column.name for column in MemorySummaries.__table__.primary_key.columns} == {
        "thread_id",
        "revision",
    }
    assert "uq_memory_summaries_coverage" in {
        index.name for index in MemorySummaries.__table__.indexes
    }
