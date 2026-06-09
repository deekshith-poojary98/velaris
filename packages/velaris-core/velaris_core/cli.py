"""Velaris CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from velaris_core.html_report import generate_report
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run


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
        )

        if html_report is not None:
            out = generate_report(json_log, html_report)
            print(f"Report written to {out}")

        return result.exit_code

    if args.command == "report":
        out = generate_report(args.json_log, args.output)
        print(f"Report written to {out}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
