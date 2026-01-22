# Redis TTL Migration - Archive

This directory contains the archived APScheduler-based timer cleanup implementation.

## Files

- `timer_cleanup_apscheduler.py`: Original polling-based timer cleanup (1-minute intervals)

## Migration

**Date**: 2026-01-07
**From**: APScheduler (polling every 1 minute)
**To**: Redis TTL (event-driven, second-level accuracy)

## Why Archived

The APScheduler approach is kept as a backup in case Redis TTL encounters issues.
To revert to APScheduler:

1. Restore `timer_cleanup_apscheduler.py` to parent directory
2. Update `__init__.py` to export `check_expired_timers`
3. Replace Redis listener in `main.py` with APScheduler code
4. Add `apscheduler==3.10.4` back to requirements.txt

## Advantages of Redis TTL

- ✅ Second-level accuracy (vs ±1 minute)
- ✅ No database polling
- ✅ Event-driven architecture
- ✅ Multi-server safe
- ✅ Lower resource usage
