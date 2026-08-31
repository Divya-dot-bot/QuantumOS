"""
QuantumOS Storage - Database

SQLite persistence layer for QuantumOS jobs, executions,
and quantum resources.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from qos.storage.models import (
    ExecutionRecord,
    JobRecord,
    ResourceRecord,
)


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""


class Database:
    """
    SQLite database used by QuantumOS.

    The database is intentionally small and self-contained for
    the MVP. The interface can later be backed by PostgreSQL or
    another database without changing the rest of QuantumOS.
    """

    def __init__(
        self,
        path: str | Path = "quantumos.db",
    ) -> None:
        """
        Create a database connection.

        Args:
            path:
                SQLite database path.

                Use ':memory:' for an in-memory database,
                which is useful for tests.
        """

        self.path = str(path)

        try:
            self.connection = sqlite3.connect(
                self.path,
                check_same_thread=False,
            )

            self.connection.row_factory = (
                sqlite3.Row
            )

            self._initialize()

        except sqlite3.Error as exc:
            raise DatabaseError(
                f"failed to initialize database: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        """Create database tables if they do not exist."""

        try:
            cursor = self.connection.cursor()

            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    shots INTEGER NOT NULL,
                    circuit TEXT NOT NULL,
                    backend TEXT,
                    submitted_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    error TEXT,
                    metadata TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    backend_id TEXT NOT NULL,
                    backend_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    shots INTEGER NOT NULL,
                    counts TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    error TEXT,
                    metadata TEXT NOT NULL,

                    FOREIGN KEY(job_id)
                        REFERENCES jobs(job_id)
                );

                CREATE TABLE IF NOT EXISTS resources (
                    resource_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    num_qubits INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    supported_operations TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

            self.connection.commit()

        except sqlite3.Error as exc:
            self.connection.rollback()

            raise DatabaseError(
                f"failed to initialize tables: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Job operations
    # ------------------------------------------------------------------

    def save_job(
        self,
        job: JobRecord,
    ) -> None:
        """Insert or update a job record."""

        if not isinstance(
            job,
            JobRecord,
        ):
            raise TypeError(
                "job must be a JobRecord"
            )

        try:
            self.connection.execute(
                """
                INSERT INTO jobs (
                    job_id,
                    status,
                    shots,
                    circuit,
                    backend,
                    submitted_at,
                    started_at,
                    completed_at,
                    error,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_id)
                DO UPDATE SET
                    status = excluded.status,
                    shots = excluded.shots,
                    circuit = excluded.circuit,
                    backend = excluded.backend,
                    submitted_at = excluded.submitted_at,
                    started_at = excluded.started_at,
                    completed_at = excluded.completed_at,
                    error = excluded.error,
                    metadata = excluded.metadata
                """,
                (
                    job.job_id,
                    job.status,
                    job.shots,
                    json.dumps(
                        job.circuit
                    ),
                    job.backend,
                    job.submitted_at.isoformat(),
                    (
                        job.started_at.isoformat()
                        if job.started_at
                        else None
                    ),
                    (
                        job.completed_at.isoformat()
                        if job.completed_at
                        else None
                    ),
                    job.error,
                    json.dumps(
                        job.metadata
                    ),
                ),
            )

            self.connection.commit()

        except (sqlite3.Error, TypeError) as exc:
            self.connection.rollback()

            raise DatabaseError(
                f"failed to save job '{job.job_id}': {exc}"
            ) from exc

    def get_job(
        self,
        job_id: str,
    ) -> JobRecord | None:
        """Retrieve a job by ID."""

        row = self.connection.execute(
            """
            SELECT *
            FROM jobs
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()

        if row is None:
            return None

        return JobRecord(
            job_id=row["job_id"],
            status=row["status"],
            shots=row["shots"],
            circuit=json.loads(
                row["circuit"]
            ),
            backend=row["backend"],
            submitted_at=_parse_datetime(
                row["submitted_at"]
            ),
            started_at=_parse_optional_datetime(
                row["started_at"]
            ),
            completed_at=_parse_optional_datetime(
                row["completed_at"]
            ),
            error=row["error"],
            metadata=json.loads(
                row["metadata"]
            ),
        )

    def list_jobs(
        self,
        limit: int = 100,
    ) -> list[JobRecord]:
        """Return recent job records."""

        if limit < 1:
            raise ValueError(
                "limit must be at least 1"
            )

        rows = self.connection.execute(
            """
            SELECT *
            FROM jobs
            ORDER BY submitted_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            self._job_from_row(row)
            for row in rows
        ]

    def delete_job(
        self,
        job_id: str,
    ) -> bool:
        """
        Delete a job.

        Returns:
            True if a row was deleted.
        """

        try:
            cursor = self.connection.execute(
                """
                DELETE FROM jobs
                WHERE job_id = ?
                """,
                (job_id,),
            )

            self.connection.commit()

            return cursor.rowcount > 0

        except sqlite3.Error as exc:
            self.connection.rollback()

            raise DatabaseError(
                f"failed to delete job '{job_id}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Execution operations
    # ------------------------------------------------------------------

    def save_execution(
        self,
        execution: ExecutionRecord,
    ) -> None:
        """Insert or update an execution record."""

        if not isinstance(
            execution,
            ExecutionRecord,
        ):
            raise TypeError(
                "execution must be an ExecutionRecord"
            )

        try:
            self.connection.execute(
                """
                INSERT INTO executions (
                    execution_id,
                    job_id,
                    backend_id,
                    backend_name,
                    status,
                    shots,
                    counts,
                    started_at,
                    completed_at,
                    error,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(execution_id)
                DO UPDATE SET
                    job_id = excluded.job_id,
                    backend_id = excluded.backend_id,
                    backend_name = excluded.backend_name,
                    status = excluded.status,
                    shots = excluded.shots,
                    counts = excluded.counts,
                    started_at = excluded.started_at,
                    completed_at = excluded.completed_at,
                    error = excluded.error,
                    metadata = excluded.metadata
                """,
                (
                    execution.execution_id,
                    execution.job_id,
                    execution.backend_id,
                    execution.backend_name,
                    execution.status,
                    execution.shots,
                    json.dumps(
                        execution.counts
                    ),
                    execution.started_at.isoformat(),
                    (
                        execution.completed_at.isoformat()
                        if execution.completed_at
                        else None
                    ),
                    execution.error,
                    json.dumps(
                        execution.metadata
                    ),
                ),
            )

            self.connection.commit()

        except sqlite3.Error as exc:
            self.connection.rollback()

            raise DatabaseError(
                "failed to save execution "
                f"'{execution.execution_id}': {exc}"
            ) from exc

    def get_execution(
        self,
        execution_id: str,
    ) -> ExecutionRecord | None:
        """Retrieve an execution by ID."""

        row = self.connection.execute(
            """
            SELECT *
            FROM executions
            WHERE execution_id = ?
            """,
            (execution_id,),
        ).fetchone()

        if row is None:
            return None

        return self._execution_from_row(
            row
        )

    def list_executions(
        self,
        limit: int = 100,
    ) -> list[ExecutionRecord]:
        """Return recent execution records."""

        if limit < 1:
            raise ValueError(
                "limit must be at least 1"
            )

        rows = self.connection.execute(
            """
            SELECT *
            FROM executions
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            self._execution_from_row(row)
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Resource operations
    # ------------------------------------------------------------------

    def save_resource(
        self,
        resource: ResourceRecord,
    ) -> None:
        """Insert or update a resource record."""

        if not isinstance(
            resource,
            ResourceRecord,
        ):
            raise TypeError(
                "resource must be a ResourceRecord"
            )

        try:
            self.connection.execute(
                """
                INSERT INTO resources (
                    resource_id,
                    name,
                    resource_type,
                    num_qubits,
                    status,
                    supported_operations,
                    metadata,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(resource_id)
                DO UPDATE SET
                    name = excluded.name,
                    resource_type = excluded.resource_type,
                    num_qubits = excluded.num_qubits,
                    status = excluded.status,
                    supported_operations =
                        excluded.supported_operations,
                    metadata = excluded.metadata,
                    updated_at = excluded.updated_at
                """,
                (
                    resource.resource_id,
                    resource.name,
                    resource.resource_type,
                    resource.num_qubits,
                    resource.status,
                    json.dumps(
                        resource.supported_operations
                    ),
                    json.dumps(
                        resource.metadata
                    ),
                    resource.updated_at.isoformat(),
                ),
            )

            self.connection.commit()

        except sqlite3.Error as exc:
            self.connection.rollback()

            raise DatabaseError(
                "failed to save resource "
                f"'{resource.resource_id}': {exc}"
            ) from exc

    def get_resource(
        self,
        resource_id: str,
    ) -> ResourceRecord | None:
        """Retrieve a resource by ID."""

        row = self.connection.execute(
            """
            SELECT *
            FROM resources
            WHERE resource_id = ?
            """,
            (resource_id,),
        ).fetchone()

        if row is None:
            return None

        return self._resource_from_row(
            row
        )

    def list_resources(self) -> list[ResourceRecord]:
        """Return all stored resources."""

        rows = self.connection.execute(
            """
            SELECT *
            FROM resources
            ORDER BY name
            """
        ).fetchall()

        return [
            self._resource_from_row(row)
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def statistics(self) -> dict[str, int]:
        """Return basic database statistics."""

        jobs = self.connection.execute(
            "SELECT COUNT(*) FROM jobs"
        ).fetchone()[0]

        executions = self.connection.execute(
            "SELECT COUNT(*) FROM executions"
        ).fetchone()[0]

        resources = self.connection.execute(
            "SELECT COUNT(*) FROM resources"
        ).fetchone()[0]

        return {
            "jobs": jobs,
            "executions": executions,
            "resources": resources,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _job_from_row(
        row: sqlite3.Row,
    ) -> JobRecord:
        """Convert a database row into a JobRecord."""

        return JobRecord(
            job_id=row["job_id"],
            status=row["status"],
            shots=row["shots"],
            circuit=json.loads(
                row["circuit"]
            ),
            backend=row["backend"],
            submitted_at=_parse_datetime(
                row["submitted_at"]
            ),
            started_at=_parse_optional_datetime(
                row["started_at"]
            ),
            completed_at=_parse_optional_datetime(
                row["completed_at"]
            ),
            error=row["error"],
            metadata=json.loads(
                row["metadata"]
            ),
        )

    @staticmethod
    def _execution_from_row(
        row: sqlite3.Row,
    ) -> ExecutionRecord:
        """Convert a database row into an ExecutionRecord."""

        return ExecutionRecord(
            execution_id=row["execution_id"],
            job_id=row["job_id"],
            backend_id=row["backend_id"],
            backend_name=row["backend_name"],
            status=row["status"],
            shots=row["shots"],
            counts=json.loads(
                row["counts"]
            ),
            started_at=_parse_datetime(
                row["started_at"]
            ),
            completed_at=_parse_optional_datetime(
                row["completed_at"]
            ),
            error=row["error"],
            metadata=json.loads(
                row["metadata"]
            ),
        )

    @staticmethod
    def _resource_from_row(
        row: sqlite3.Row,
    ) -> ResourceRecord:
        """Convert a database row into a ResourceRecord."""

        return ResourceRecord(
            resource_id=row["resource_id"],
            name=row["name"],
            resource_type=row["resource_type"],
            num_qubits=row["num_qubits"],
            status=row["status"],
            supported_operations=json.loads(
                row["supported_operations"]
            ),
            metadata=json.loads(
                row["metadata"]
            ),
            updated_at=_parse_datetime(
                row["updated_at"]
            ),
        )

    def close(self) -> None:
        """Close the database connection."""

        self.connection.close()

    def __enter__(self) -> Database:
        """Enter database context."""

        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        """Exit database context."""

        self.close()


def _parse_datetime(value: str):
    """Parse an ISO-8601 datetime."""

    from datetime import datetime

    return datetime.fromisoformat(value)


def _parse_optional_datetime(
    value: str | None,
):
    """Parse an optional ISO-8601 datetime."""

    if value is None:
        return None

    return _parse_datetime(value)