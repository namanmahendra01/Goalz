from __future__ import annotations

import argparse
import json
import os
import secrets
from pathlib import Path

from growth_agent.oauth import (
    build_google_ads_authorization_url,
    build_google_ads_token_payload,
    build_meta_debug_token_url,
)
from growth_agent.runtime import REQUIRED_SECRETS, run_daily_workflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goalz growth automation entrypoint")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily_run = subparsers.add_parser("daily-run", help="Build the daily plan and report")
    daily_run.add_argument("--config", required=True, type=Path)
    daily_run.add_argument("--metrics", required=True, type=Path)
    daily_run.add_argument("--report-out", required=True, type=Path)
    daily_run.add_argument("--json-out", type=Path)
    daily_run.add_argument("--summary-out", type=Path)

    validate = subparsers.add_parser("validate-secrets", help="Validate available secrets for enabled live channels")
    validate.add_argument("--config", required=True, type=Path)

    google_auth = subparsers.add_parser("google-auth-url", help="Generate a Google Ads OAuth authorization URL")
    google_auth.add_argument("--client-id", required=True)
    google_auth.add_argument("--redirect-uri", required=True)
    google_auth.add_argument("--state")

    google_exchange = subparsers.add_parser("google-token-payload", help="Print the Google token exchange payload")
    google_exchange.add_argument("--client-id", required=True)
    google_exchange.add_argument("--client-secret", required=True)
    google_exchange.add_argument("--redirect-uri", required=True)
    google_exchange.add_argument("--code", required=True)

    meta_debug = subparsers.add_parser("meta-debug-url", help="Generate the Meta debug token URL")
    meta_debug.add_argument("--app-id", required=True)
    meta_debug.add_argument("--app-secret", required=True)
    meta_debug.add_argument("--input-token", required=True)

    secret_guide = subparsers.add_parser("secret-guide", help="Print gh CLI commands for the active secret contract")
    secret_guide.add_argument("--config", required=True, type=Path)

    return parser.parse_args()


def provided_secret_names_from_env() -> set[str]:
    declared = {
        secret_name
        for channel_secret_names in REQUIRED_SECRETS.values()
        for secret_name in channel_secret_names
    }
    return {secret_name for secret_name in declared if os.getenv(secret_name)}


def run_daily(args: argparse.Namespace) -> int:
    result = run_daily_workflow(
        config_path=args.config,
        metrics_path=args.metrics,
        provided_secret_names=provided_secret_names_from_env(),
    )

    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(result.report_markdown, encoding="utf-8")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(
                {
                    "mode": result.plan.summary.mode,
                    "blended_roas": result.plan.summary.blended_roas,
                    "actions": [
                        {"code": action.code, "payload": action.payload}
                        for action in result.plan.actions
                    ],
                    "missing_secrets": result.missing_secrets,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    if args.summary_out:
        args.summary_out.write_text(result.report_markdown, encoding="utf-8")

    print(result.report_markdown)
    return 0


def validate_secrets(args: argparse.Namespace) -> int:
    result = run_daily_workflow(
        config_path=args.config,
        metrics_path=Path("growth_agent/config/sample_metrics.json"),
        provided_secret_names=provided_secret_names_from_env(),
    )
    print(result.report_markdown)
    return 1 if result.missing_secrets else 0


def print_google_auth_url(args: argparse.Namespace) -> int:
    state = args.state or secrets.token_urlsafe(16)
    print(
        build_google_ads_authorization_url(
            client_id=args.client_id,
            redirect_uri=args.redirect_uri,
            state=state,
        )
    )
    return 0


def print_google_token_payload(args: argparse.Namespace) -> int:
    endpoint, payload = build_google_ads_token_payload(
        client_id=args.client_id,
        client_secret=args.client_secret,
        redirect_uri=args.redirect_uri,
        code=args.code,
    )
    print(json.dumps({"token_endpoint": endpoint, "payload": payload}, indent=2))
    return 0


def print_meta_debug_url(args: argparse.Namespace) -> int:
    print(
        build_meta_debug_token_url(
            app_id=args.app_id,
            app_secret=args.app_secret,
            input_token=args.input_token,
        )
    )
    return 0


def print_secret_guide(args: argparse.Namespace) -> int:
    result = run_daily_workflow(
        config_path=args.config,
        metrics_path=Path("growth_agent/config/sample_metrics.json"),
        provided_secret_names=set(),
    )
    for channel, names in sorted(result.missing_secrets.items()):
        print(f"# {channel}")
        for name in names:
            print(f"gh secret set {name}")
        print("")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "daily-run":
        return run_daily(args)
    if args.command == "validate-secrets":
        return validate_secrets(args)
    if args.command == "google-auth-url":
        return print_google_auth_url(args)
    if args.command == "google-token-payload":
        return print_google_token_payload(args)
    if args.command == "meta-debug-url":
        return print_meta_debug_url(args)
    if args.command == "secret-guide":
        return print_secret_guide(args)
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
