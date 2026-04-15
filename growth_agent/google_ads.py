from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date, timedelta

from growth_agent.models import ChannelMetrics, MetricsSnapshot


class GoogleAdsMetricsError(RuntimeError):
    pass


def normalize_google_ads_customer_id(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if not digits:
        raise GoogleAdsMetricsError("Google Ads customer id is empty after normalization.")
    return digits


def channel_metrics_from_google_totals(
    *,
    cost_micros: int,
    conversions_value: float,
    conversions: float,
) -> ChannelMetrics:
    spend_usd = cost_micros / 1_000_000
    revenue_usd = float(conversions_value)
    roas = revenue_usd / spend_usd if spend_usd > 0 else 0.0
    conversions_int = int(round(conversions))
    return ChannelMetrics(
        spend_usd=spend_usd,
        revenue_usd=revenue_usd,
        roas=roas,
        conversions=conversions_int,
    )


def merge_google_channel_metrics(snapshot: MetricsSnapshot, google: ChannelMetrics) -> MetricsSnapshot:
    channels = dict(snapshot.channels)
    channels["google_ads"] = google
    total_spend = sum(channel.spend_usd for channel in channels.values())
    total_revenue = sum(channel.revenue_usd for channel in channels.values())
    blended_roas = total_revenue / total_spend if total_spend > 0 else 0.0
    return MetricsSnapshot(
        blended_roas=blended_roas,
        attributed_revenue_usd=total_revenue,
        total_marketing_spend_usd=total_spend,
        channels=channels,
    )


@dataclass(frozen=True)
class GoogleAdsEnv:
    developer_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    customer_id: str
    login_customer_id: str | None


def load_google_ads_env() -> GoogleAdsEnv:
    missing = [
        name
        for name in (
            "GOOGLE_ADS_DEVELOPER_TOKEN",
            "GOOGLE_ADS_CLIENT_ID",
            "GOOGLE_ADS_CLIENT_SECRET",
            "GOOGLE_ADS_REFRESH_TOKEN",
            "GOOGLE_ADS_CUSTOMER_ID",
        )
        if not os.getenv(name)
    ]
    if missing:
        raise GoogleAdsMetricsError(
            "Missing Google Ads environment variables: " + ", ".join(sorted(missing))
        )

    login_raw = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip()
    login_customer_id = normalize_google_ads_customer_id(login_raw) if login_raw else None

    return GoogleAdsEnv(
        developer_token=os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        client_id=os.environ["GOOGLE_ADS_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        refresh_token=os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        customer_id=normalize_google_ads_customer_id(os.environ["GOOGLE_ADS_CUSTOMER_ID"]),
        login_customer_id=login_customer_id,
    )


def build_google_ads_client(env: GoogleAdsEnv | None = None):
    """Return a configured GoogleAdsClient (loads google-ads lazily)."""
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError as exc:
        raise GoogleAdsMetricsError(
            "google-ads is not installed. Install dependencies with: "
            "pip install -r requirements-growth.txt"
        ) from exc

    env = env or load_google_ads_env()

    config: dict[str, object] = {
        "developer_token": env.developer_token,
        "client_id": env.client_id,
        "client_secret": env.client_secret,
        "refresh_token": env.refresh_token,
        "use_proto_plus": True,
    }
    if env.login_customer_id:
        config["login_customer_id"] = env.login_customer_id

    try:
        return GoogleAdsClient.load_from_dict(config)
    except Exception as exc:
        raise GoogleAdsMetricsError(f"Failed to initialize Google Ads client: {exc}") from exc


def fetch_google_ads_channel_metrics(*, env: GoogleAdsEnv | None = None, days: int = 7) -> ChannelMetrics:
    if days < 1 or days > 365:
        raise GoogleAdsMetricsError("days must be between 1 and 365.")

    env = env or load_google_ads_env()
    client = build_google_ads_client(env)

    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)

    query = f"""
        SELECT
          segments.date,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM customer
        WHERE segments.date BETWEEN '{start.isoformat()}' AND '{end.isoformat()}'
    """

    ga_service = client.get_service("GoogleAdsService")
    total_cost_micros = 0
    total_conversions = 0.0
    total_conversions_value = 0.0

    try:
        stream = ga_service.search_stream(customer_id=env.customer_id, query=query)
        for batch in stream:
            for row in batch.results:
                total_cost_micros += int(row.metrics.cost_micros)
                total_conversions += float(row.metrics.conversions)
                total_conversions_value += float(row.metrics.conversions_value)
    except Exception as exc:
        raise GoogleAdsMetricsError(
            "Google Ads query failed. If you use a manager account, set "
            "GOOGLE_ADS_LOGIN_CUSTOMER_ID to the manager (MCC) id. "
            f"Details: {exc}"
        ) from exc

    return channel_metrics_from_google_totals(
        cost_micros=total_cost_micros,
        conversions=total_conversions,
        conversions_value=total_conversions_value,
    )
