"""Query counter utility for detecting N+1 query problems.

This module provides a context manager to count database queries
executed during a code block. Used for automated N+1 query detection tests.

Industry standard pattern for preventing query performance regression.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import event
from sqlalchemy.engine import Engine


class QueryCounter:
    """Context manager to count database queries.

    Usage:
        with QueryCounter() as counter:
            # Execute some code
            service.get_posts(limit=50)

        # Check query count
        assert counter.count <= 5, f"Too many queries: {counter.count}"

    Attributes:
        count: Number of queries executed
        queries: List of SQL statements (for debugging)
    """

    def __init__(self):
        """Initialize query counter."""
        self.count = 0
        self.queries = []
        self._listener = None

    def __enter__(self):
        """Start counting queries."""
        self.count = 0
        self.queries = []

        # Register SQLAlchemy event listener
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            self.count += 1
            # Store query for debugging (truncate long queries)
            query_preview = statement[:200] if len(statement) > 200 else statement
            self.queries.append(query_preview)

        self._listener = receive_before_cursor_execute
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop counting queries and clean up listener."""
        if self._listener:
            event.remove(Engine, "before_cursor_execute", self._listener)
        return False

    def get_summary(self) -> str:
        """Get a summary of queries executed.

        Returns:
            Human-readable summary string
        """
        summary = f"Total queries: {self.count}\n"
        if self.queries:
            summary += "Queries executed:\n"
            for i, query in enumerate(self.queries, 1):
                summary += f"  {i}. {query}\n"
        return summary


@contextmanager
def count_queries() -> Generator[QueryCounter, None, None]:
    """Convenience context manager for counting queries.

    Usage:
        with count_queries() as counter:
            service.get_posts(limit=50)

        assert counter.count <= 5

    Yields:
        QueryCounter instance
    """
    counter = QueryCounter()
    with counter:
        yield counter
