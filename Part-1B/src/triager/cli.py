"""CLI entry point for the Support Ticket Triager."""

from __future__ import annotations

import argparse
import json
import sys

from .triager import triage


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="triager",
        description="Support Ticket Triager CLI",
    )
    parser.add_argument(
        "ticket",
        nargs="?",
        help="Support ticket text to triage",
    )
    parser.add_argument(
        "--file",
        "-f",
        help="Path to a text file containing the ticket",
    )

    args = parser.parse_args(argv)

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    elif args.ticket:
        text = args.ticket
    else:
        text = sys.stdin.read()

    result = triage(text)
    print(json.dumps(result.to_dict(), indent=2))
    sys.exit(0 if not result.is_service_error else 2)


if __name__ == "__main__":
    main()
