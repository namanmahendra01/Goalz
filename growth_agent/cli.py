from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from pathlib import Path

from growth_agent.campaign_links import campaign_asset_bundle
from growth_agent.oauth import (
    build_google_ads_authorization_url,
    build_google_ads_token_payload,
    build_meta_debug_token_url,
)
from growth_agent.runtime import (
    REQUIRED_SECRETS,
    load_metrics_snapshot,
    run_daily_workflow,
    run_daily_workflow_with_metrics,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goalz growth automation entrypoint")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily_run = subparsers.add_parser("daily-run", help="Build the daily plan and report")
    daily_run.add_argument("--config", required=True, type=Path)
    daily_run.add_argument("--metrics", required=True, type=Path)
    daily_run.add_argument("--report-out", required=True, type=Path)
    daily_run.add_argument("--json-out", type=Path)
    daily_run.add_argument("--summary-out", type=Path)
    daily_run.add_argument(
        "--google-live",
        action="store_true",
        help="Replace google_ads metrics using the Google Ads API (requires env secrets + pip deps)",
    )
    daily_run.add_argument(
        "--google-days",
        type=int,
        default=7,
        help="Lookback window for Google Ads metrics when using --google-live (default: 7)",
    )

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

    campaign_assets = subparsers.add_parser(
        "campaign-assets",
        help="Print App Store tracking URLs and bundled ad copy for Google, Meta, and Apple Search Ads",
    )
    campaign_assets.add_argument(
        "--manifest",
        type=Path,
        default=Path("growth_agent/marketing/app_manifest.json"),
    )
    campaign_assets.add_argument("--content", default="default", help="utm_content slug (per creative or ad group)")
    campaign_assets.add_argument("--campaign", default="goalz_launch_v1", help="utm_campaign value")
    campaign_assets.add_argument(
        "--ad-copy",
        type=Path,
        default=Path("growth_agent/marketing/ad_copy.json"),
    )

    google_launch = subparsers.add_parser(
        "google-ads-launch",
        help="Create or enable the Goalz iOS App campaign via Google Ads API (no UI)",
    )
    google_launch.add_argument(
        "--manifest",
        type=Path,
        default=Path("growth_agent/marketing/app_manifest.json"),
    )
    google_launch.add_argument(
        "--ad-copy",
        type=Path,
        default=Path("growth_agent/marketing/ad_copy.json"),
    )
    google_launch.add_argument(
        "--campaign-name",
        default=None,
        help="Override GOOGLE_ADS_GOALZ_CAMPAIGN_NAME (default: Goalz Autonomous Launch)",
    )
    google_launch.add_argument("--daily-budget-usd", type=float, default=None)
    google_launch.add_argument("--target-cpa-usd", type=float, default=None)
    google_launch.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned settings without calling the API",
    )

    return parser.parse_args()


def provided_secret_names_from_env() -> set[str]:
    declared = {
        secret_name
        for channel_secret_names in REQUIRED_SECRETS.values()
        for secret_name in channel_secret_names
    }
    return {secret_name for secret_name in declared if os.getenv(secret_name)}


def run_daily(args: argparse.Namespace) -> int:
    metrics = load_metrics_snapshot(args.metrics)
    if args.google_live:
        from growth_agent.google_ads import (
            GoogleAdsMetricsError,
            fetch_google_ads_channel_metrics,
            merge_google_channel_metrics,
        )

        try:
            google = fetch_google_ads_channel_metrics(days=args.google_days)
        except GoogleAdsMetricsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        metrics = merge_google_channel_metrics(metrics, google)

    result = run_daily_workflow_with_metrics(
        config_path=args.config,
        metrics=metrics,
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


def run_google_ads_launch(args: argparse.Namespace) -> int:
    from growth_agent.google_ads_launch import (
        GoogleAdsLaunchError,
        LaunchParams,
        default_launch_params,
        launch_goalz_app_campaign,
    )

    defaults = default_launch_params()
    params = LaunchParams(
        campaign_name=(args.campaign_name or defaults.campaign_name),
        daily_budget_usd=args.daily_budget_usd if args.daily_budget_usd is not None else defaults.daily_budget_usd,
        target_cpa_usd=args.target_cpa_usd if args.target_cpa_usd is not None else defaults.target_cpa_usd,
        dry_run=args.dry_run or defaults.dry_run,
    )
    try:
        result = launch_goalz_app_campaign(
            manifest_path=args.manifest,
            ad_copy_path=args.ad_copy,
            params=params,
        )
    except GoogleAdsLaunchError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


def print_campaign_assets(args: argparse.Namespace) -> int:
    bundle = campaign_asset_bundle(
        args.manifest,
        content=args.content,
        campaign=args.campaign,
    )
    payload: dict[str, object] = dict(bundle)
    if args.ad_copy.is_file():
        payload["ad_copy"] = json.loads(args.ad_copy.read_text(encoding="utf-8"))
    print(json.dumps(payload, indent=2))
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
    if args.command == "campaign-assets":
        return print_campaign_assets(args)
    if args.command == "google-ads-launch":
        return run_google_ads_launch(args)
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
