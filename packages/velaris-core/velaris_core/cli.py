"""Velaris CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from velaris_core.capability_info import (
    UnknownCapabilityError,
    capabilities_to_json,
    capability_to_json,
    describe_capability,
    format_capabilities_list,
    format_capability_detail,
    list_capabilities,
)
from velaris_core.discovery import discover, format_tree, to_json
from velaris_core.doctor import format_report, report_to_json, run_diagnostics
from velaris_core.errors import CollectionError
from velaris_core.html_report import generate_report
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run
from velaris_core.scaffold import ScaffoldError, format_success_message, init_project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="velaris")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run Velaris tests")
    run_parser.add_argument(
        "paths",
        nargs="*",
        default=["tests"],
        help="Test files or directories",
    )
    run_parser.add_argument(
        "--config",
        default="velaris.toml",
        help="Path to velaris.toml",
    )
    run_parser.add_argument(
        "--json-log",
        default=None,
        help="Write JSON-lines event log to PATH",
    )
    run_parser.add_argument(
        "--html-report",
        nargs="?",
        const="report.html",
        default=None,
        metavar="PATH",
        help="Generate static HTML report after the run (default: report.html)",
    )
    run_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show lifecycle events (run, resolve, pass/fail, teardown)",
    )
    run_parser.add_argument(
        "--debug",
        action="store_true",
        help="Show all events including capability observations",
    )
    run_parser.add_argument(
        "--tag",
        action="append",
        default=None,
        help="Run tests matching this tag (can be specified multiple times for OR behavior)",
    )

    collect_parser = subparsers.add_parser(
        "collect",
        help="Discover tests and show what would run — no execution",
    )
    collect_parser.add_argument(
        "paths",
        nargs="*",
        default=["tests"],
        help="Test files or directories",
    )
    collect_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit collected tests as a JSON array instead of a tree",
    )
    collect_parser.add_argument(
        "--tag",
        action="append",
        default=None,
        help="Filter collected tests matching this tag (can be specified multiple times for OR behavior)",
    )

    capabilities_parser = subparsers.add_parser(
        "capabilities",
        help="List capabilities Velaris knows about — no execution",
    )
    capabilities_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit capability IDs as a JSON array",
    )

    capability_parser = subparsers.add_parser(
        "capability",
        help="Show one capability's description, methods, and providers",
    )
    capability_parser.add_argument(
        "capability_id",
        help="Capability ID to describe (e.g. browser)",
    )
    capability_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit capability metadata as a JSON object",
    )

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Diagnose the local Velaris environment — no execution",
    )
    doctor_parser.add_argument(
        "paths",
        nargs="*",
        default=["tests"],
        help="Test files or directories to check (default: tests)",
    )
    doctor_parser.add_argument(
        "--config",
        default="velaris.toml",
        help="Path to velaris.toml",
    )
    doctor_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit diagnostics as a JSON object",
    )

    report_parser = subparsers.add_parser(
        "report",
        help="Generate a static HTML report from a JSON event log",
    )
    report_parser.add_argument(
        "json_log",
        help="Path to JSON-lines event log (from velaris run --json-log)",
    )
    report_parser.add_argument(
        "-o",
        "--output",
        default="report.html",
        help="Output HTML file path (default: report.html)",
    )

    init_parser = subparsers.add_parser(
        "init",
        help="Create a new Velaris project with a passing sample test",
    )
    init_parser.add_argument(
        "project_name",
        help="Project directory to create (parent directories are created if needed)",
    )

    args = parser.parse_args(argv)
    if args.command == "run":
        output_mode = OutputMode.DEFAULT
        if args.debug:
            output_mode = OutputMode.DEBUG
        elif args.verbose:
            output_mode = OutputMode.VERBOSE

        json_log = args.json_log
        html_report = args.html_report
        if html_report is not None and json_log is None:
            json_log = str(Path(html_report).with_suffix(".jsonl"))

        result = run(
            args.paths,
            config_path=args.config,
            json_log=json_log,
            output_mode=output_mode,
            tags=args.tag,
        )

        if html_report is not None:
            out = generate_report(json_log, html_report)
            print(f"Report written to {out}")

        return result.exit_code

    if args.command == "collect":
        try:
            tests = discover(args.paths, tags=args.tag)
        except CollectionError as exc:
            print(f"CollectionError:\n{exc}", file=sys.stderr)
            return 1
        print(to_json(tests) if args.json else format_tree(tests))
        return 0

    if args.command == "capabilities":
        ids = list_capabilities()
        print(capabilities_to_json(ids) if args.json else format_capabilities_list(ids))
        return 0

    if args.command == "capability":
        try:
            meta = describe_capability(args.capability_id)
        except UnknownCapabilityError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(capability_to_json(meta) if args.json else format_capability_detail(meta))
        return 0

    if args.command == "doctor":
        report = run_diagnostics(args.paths, config_path=args.config)
        print(report_to_json(report) if args.json else format_report(report))
        return report.exit_code

    if args.command == "report":
        out = generate_report(args.json_log, args.output)
        print(f"Report written to {out}")
        return 0

    if args.command == "init":
        try:
            init_project(args.project_name)
        except ScaffoldError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(format_success_message(args.project_name), end="")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
