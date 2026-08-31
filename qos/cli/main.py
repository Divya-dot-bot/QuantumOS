"""
QuantumOS Command Line Interface.

Provides terminal commands for inspecting the QuantumOS runtime,
resources, jobs, and executing quantum workloads.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from qos.runtime.runtime import (
    QuantumRuntime,
    RuntimeStatus,
)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the QuantumOS CLI argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="quantumos",
        description=(
            "QuantumOS - Quantum Operating System MVP"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="QuantumOS 0.1.0",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
    )

    # ------------------------------------------------------------------
    # status
    # ------------------------------------------------------------------

    status_parser = subparsers.add_parser(
        "status",
        help="Show QuantumOS runtime status.",
    )

    status_parser.set_defaults(
        handler=handle_status
    )

    # ------------------------------------------------------------------
    # backends
    # ------------------------------------------------------------------

    backends_parser = subparsers.add_parser(
        "backends",
        help="List available quantum backends.",
    )

    backends_parser.set_defaults(
        handler=handle_backends
    )

    # ------------------------------------------------------------------
    # jobs
    # ------------------------------------------------------------------

    jobs_parser = subparsers.add_parser(
        "jobs",
        help="List submitted jobs.",
    )

    jobs_parser.set_defaults(
        handler=handle_jobs
    )

    # ------------------------------------------------------------------
    # start
    # ------------------------------------------------------------------

    start_parser = subparsers.add_parser(
        "start",
        help="Start the QuantumOS runtime.",
    )

    start_parser.set_defaults(
        handler=handle_start
    )

    # ------------------------------------------------------------------
    # stop
    # ------------------------------------------------------------------

    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop the QuantumOS runtime.",
    )

    stop_parser.set_defaults(
        handler=handle_stop
    )

    # ------------------------------------------------------------------
    # run
    # ------------------------------------------------------------------

    run_parser = subparsers.add_parser(
        "run",
        help="Execute the next queued job.",
    )

    run_parser.set_defaults(
        handler=handle_run
    )

    return parser


# ----------------------------------------------------------------------
# Command handlers
# ----------------------------------------------------------------------


def handle_status(
    runtime: QuantumRuntime,
    args: argparse.Namespace,
) -> int:
    """Handle the status command."""

    statistics = runtime.statistics()

    print(
        json.dumps(
            statistics,
            indent=2,
            default=str,
        )
    )

    return 0


def handle_backends(
    runtime: QuantumRuntime,
    args: argparse.Namespace,
) -> int:
    """Handle the backends command."""

    backends = runtime.resource_manager.list_backends()

    if not backends:
        print("No backends registered.")
        return 0

    for backend in backends:
        print(
            f"{backend.backend_id} | "
            f"{backend.name} | "
            f"{backend.resource_type.value} | "
            f"{backend.num_qubits} qubits | "
            f"{backend.status.value}"
        )

    return 0


def handle_jobs(
    runtime: QuantumRuntime,
    args: argparse.Namespace,
) -> int:
    """Handle the jobs command."""

    jobs = runtime.pending_jobs()

    if not jobs:
        print("No pending jobs.")
        return 0

    for job in jobs:
        print(
            f"{job.id} | "
            f"{job.status.value} | "
            f"shots={job.shots}"
        )

    return 0


def handle_start(
    runtime: QuantumRuntime,
    args: argparse.Namespace,
) -> int:
    """Handle the start command."""

    runtime.start()

    print("QuantumOS runtime started.")

    return 0


def handle_stop(
    runtime: QuantumRuntime,
    args: argparse.Namespace,
) -> int:
    """Handle the stop command."""

    runtime.stop()

    print("QuantumOS runtime stopped.")

    return 0


def handle_run(
    runtime: QuantumRuntime,
    args: argparse.Namespace,
) -> int:
    """Handle the run command."""

    if runtime.status != RuntimeStatus.RUNNING:
        runtime.start()

    try:
        execution = runtime.run_next()

    except Exception as exc:
        print(
            f"Execution failed: {exc}",
            file=sys.stderr,
        )

        return 1

    if execution is None:
        print("No queued jobs.")
        return 0

    print(
        json.dumps(
            execution.as_dict(),
            indent=2,
            default=str,
        )
    )

    return 0


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """
    Run the QuantumOS CLI.

    Args:
        argv:
            Optional command-line arguments.

    Returns:
        Process exit code.
    """

    parser = create_parser()

    args = parser.parse_args(argv)

    runtime = QuantumRuntime()

    handler = getattr(
        args,
        "handler",
        None,
    )

    if handler is None:
        parser.print_help()
        return 0

    return handler(
        runtime,
        args,
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )