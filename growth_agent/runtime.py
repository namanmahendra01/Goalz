from __future__ import annotations

import json
from pathlib import Path

from growth_agent.config import load_config
from growth_agent.models import ChannelMetrics, MetricsSnapshot, WorkflowResult
from growth_agent.planner import build_daily_plan
from growth_agent.reporting import render_report

from growth_agent.models import AppConfig


REQUIRED_SECRETS: dict[str, list[str]] = {
    "google_ads": [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_CUSTOMER_ID",
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_REFRESH_TOKEN",
    ],
    "apple_search_ads": [
        "APPLE_SEARCH_ADS_ORG_ID",
        "APPLE_SEARCH_ADS_CERTIFICATE_PEM",
        "APPLE_SEARCH_ADS_KEY_ID",
        "APPLE_SEARCH_ADS_PRIVATE_KEY_PEM",
    ],
    "meta_ads": [
        "META_ACCESS_TOKEN",
        "META_AD_ACCOUNT_ID",
        "META_APP_ID",
        "META_APP_SECRET",
    ],
    "x_posts": [
        "X_ACCESS_TOKEN",
        "X_ACCESS_TOKEN_SECRET",
        "X_API_KEY",
        "X_API_SECRET",
    ],
    "reddit_posts": [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_PASSWORD",
        "REDDIT_USERNAME",
    ],
    "product_hunt": [
        "PRODUCT_HUNT_ACCESS_TOKEN",
    ],
}


def missing_secrets_for_enabled_channels(
    config: AppConfig,
    provided_secret_names: set[str],
) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}
    for channel_name in config.enabled_channels():
        required = REQUIRED_SECRETS.get(channel_name, [])
        unresolved = [secret for secret in required if secret not in provided_secret_names]
        if unresolved:
            missing[channel_name] = unresolved
    return missing


def load_metrics_snapshot(path: Path) -> MetricsSnapshot:
    payload = json.loads(path.read_text(encoding="utf-8"))
    channels = {
        name: ChannelMetrics(
            spend_usd=float(metrics["spend_usd"]),
            revenue_usd=float(metrics["revenue_usd"]),
            roas=float(metrics["roas"]),
            conversions=int(metrics["conversions"]),
        )
        for name, metrics in payload["channels"].items()
    }
    return MetricsSnapshot(
        blended_roas=float(payload["blended_roas"]),
        attributed_revenue_usd=float(payload["attributed_revenue_usd"]),
        total_marketing_spend_usd=float(payload["total_marketing_spend_usd"]),
        channels=channels,
    )


def run_daily_workflow_with_metrics(
    config_path: Path,
    metrics: MetricsSnapshot,
    provided_secret_names: set[str],
) -> WorkflowResult:
    config = load_config(config_path)
    plan = build_daily_plan(config, metrics)
    missing_secrets = missing_secrets_for_enabled_channels(config, provided_secret_names)
    result = WorkflowResult(
        plan=plan,
        missing_secrets=missing_secrets,
        report_markdown="",
    )
    report_markdown = render_report(result)
    return WorkflowResult(
        plan=plan,
        missing_secrets=missing_secrets,
        report_markdown=report_markdown,
    )


def run_daily_workflow(
    config_path: Path,
    metrics_path: Path,
    provided_secret_names: set[str],
) -> WorkflowResult:
    metrics = load_metrics_snapshot(metrics_path)
    return run_daily_workflow_with_metrics(config_path, metrics, provided_secret_names)
