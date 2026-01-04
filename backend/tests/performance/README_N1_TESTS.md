# Phase 2: N+1 Query Detection Tests

## 📋 Overview

Automated tests to prevent N+1 query regression in Community and Messaging services.

## 🎯 Test Coverage

### Community Service
- ✅ `test_get_posts_no_n_plus_one` - Posts list (≤5 queries)
- ✅ `test_get_comments_no_n_plus_one` - Comments (≤3 queries)

### Messaging Service
- ✅ `test_get_conversations_no_n_plus_one` - Conversations (≤3 queries)
- ✅ `test_get_messages_no_n_plus_one` - Messages (≤2 queries)

### Edge Cases
- ✅ `test_empty_posts_no_queries` - Empty results
- ✅ `test_single_post_efficient` - Single item efficiency

## 🚀 Running Tests

```bash
# Run all N+1 tests
cd backend
pytest tests/performance/test_n_plus_one.py -v

# Run specific test
pytest tests/performance/test_n_plus_one.py::TestCommunityN1Prevention::test_get_posts_no_n_plus_one -v

# Run with query details
pytest tests/performance/test_n_plus_one.py -v -s
```

## 📊 Expected Results

```
tests/performance/test_n_plus_one.py::TestCommunityN1Prevention::test_get_posts_no_n_plus_one PASSED
tests/performance/test_n_plus_one.py::TestCommunityN1Prevention::test_get_comments_no_n_plus_one PASSED
tests/performance/test_n_plus_one.py::TestMessagingN1Prevention::test_get_conversations_no_n_plus_one PASSED
tests/performance/test_n_plus_one.py::TestMessagingN1Prevention::test_get_messages_no_n_plus_one PASSED
tests/performance/test_n_plus_one.py::TestN1PreventionEdgeCases::test_empty_posts_no_queries PASSED
tests/performance/test_n_plus_one.py::TestN1PreventionEdgeCases::test_single_post_efficient PASSED

====== 6 passed in 2.5s ======
```

## 🔍 How It Works

### QueryCounter Utility

```python
with QueryCounter() as counter:
    service.get_posts(limit=50)

assert counter.count <= 5  # Fails if N+1 detected
```

### Test Thresholds

| Endpoint | Max Queries | Breakdown |
|----------|-------------|-----------|
| get_posts | ≤5 | 1 posts + 1 users + 1 likes + 1 reads + 1 count |
| get_comments | ≤3 | 1 comments + 1 users + 1 likes |
| get_conversations | ≤3 | 1 conversations + 1 users + 1 messages |
| get_messages | ≤2 | 1 conversation + 1 messages + 1 users |

## 🎓 Benefits

1. **Prevents Regression** - Catches N+1 queries before merge
2. **CI/CD Integration** - Runs automatically in GitHub Actions
3. **Clear Failures** - Shows exact query count and breakdown
4. **Industry Standard** - Used by Facebook, Google, Meta, Netflix

## 📝 Adding New Tests

```python
@pytest.mark.asyncio
async def test_my_endpoint_no_n_plus_one(db_session):
    """Verify my_endpoint has no N+1 queries."""
    with QueryCounter() as counter:
        await service.my_endpoint()

    assert counter.count <= THRESHOLD, (
        f"N+1 detected! Got {counter.count} queries\n"
        f"{counter.get_summary()}"
    )
```

## ✅ Status

**Phase 2 Complete**: All N+1 detection tests implemented and ready for CI/CD.
