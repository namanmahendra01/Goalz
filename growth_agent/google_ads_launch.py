from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from growth_agent.google_ads import GoogleAdsMetricsError, build_google_ads_client, load_google_ads_env


class GoogleAdsLaunchError(RuntimeError):
    pass


def _usd_to_micros(usd: float) -> int:
    return int(round(usd * 1_000_000))


def _escape_gaql_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _load_ad_copy(path: Path) -> tuple[list[str], list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    headlines = list(data.get("google_headlines") or [])
    descriptions = list(data.get("google_descriptions") or [])
    if len(headlines) < 2 or len(descriptions) < 2:
        raise GoogleAdsLaunchError("ad_copy.json needs at least 2 google_headlines and 2 google_descriptions.")
    return headlines[:15], descriptions[:5]


def _find_managed_campaign(
    client,
    customer_id: str,
    campaign_name: str,
) -> tuple[str, object] | None:
    """Return (resource_name, status) if a campaign with this name exists (not REMOVED)."""
    ga = client.get_service("GoogleAdsService")
    safe = _escape_gaql_string(campaign_name)
    query = f"""
        SELECT campaign.resource_name, campaign.status
        FROM campaign
        WHERE campaign.name = '{safe}'
          AND campaign.status != REMOVED
        LIMIT 1
    """
    stream = ga.search_stream(customer_id=customer_id, query=query)
    for batch in stream:
        for row in batch.results:
            return row.campaign.resource_name, row.campaign.status
    return None


def _enable_campaign(client, customer_id: str, resource_name: str) -> None:
    from google.protobuf import field_mask_pb2

    campaign_service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    op.update.resource_name = resource_name
    op.update.status = client.enums.CampaignStatusEnum.ENABLED
    op.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
    campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])


def _create_budget(client, customer_id: str, *, daily_budget_micros: int) -> str:
    svc = client.get_service("CampaignBudgetService")
    op = client.get_type("CampaignBudgetOperation")
    b = op.create
    b.name = f"Goalz Budget {uuid4().hex[:10]}"
    b.amount_micros = daily_budget_micros
    b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    b.explicitly_shared = False
    resp = svc.mutate_campaign_budgets(customer_id=customer_id, operations=[op])
    return resp.results[0].resource_name


def _create_app_campaign(
    client,
    customer_id: str,
    *,
    budget_resource_name: str,
    campaign_name: str,
    bundle_id: str,
    target_cpa_micros: int,
) -> str:
    campaign_service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    c = op.create
    c.name = campaign_name
    c.campaign_budget = budget_resource_name
    c.status = client.enums.CampaignStatusEnum.PAUSED
    c.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.MULTI_CHANNEL
    c.advertising_channel_sub_type = client.enums.AdvertisingChannelSubTypeEnum.APP_CAMPAIGN
    c.target_cpa.target_cpa_micros = target_cpa_micros
    c.app_campaign_setting.app_id = bundle_id
    c.app_campaign_setting.app_store = client.enums.AppCampaignAppStoreEnum.APPLE_APP_STORE
    c.app_campaign_setting.bidding_strategy_goal_type = (
        client.enums.AppCampaignBiddingStrategyGoalTypeEnum.OPTIMIZE_INSTALLS_TARGET_INSTALL_COST
    )
    c.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )
    c.start_date_time = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d 000000")
    c.end_date_time = (datetime.now() + timedelta(days=365)).strftime("%Y%m%d 235959")

    resp = campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
    return resp.results[0].resource_name


def _add_us_english_targeting(client, customer_id: str, campaign_resource_name: str) -> None:
    """United States + English (en)."""
    cc_svc = client.get_service("CampaignCriterionService")

    ops: list = []

    loc_op = client.get_type("CampaignCriterionOperation")
    loc = loc_op.create
    loc.campaign = campaign_resource_name
    loc.location.geo_target_constant = "geoTargetConstants/2840"
    ops.append(loc_op)

    lang_op = client.get_type("CampaignCriterionOperation")
    lang = lang_op.create
    lang.campaign = campaign_resource_name
    lang.language.language_constant = "languageConstants/1000"
    ops.append(lang_op)

    cc_svc.mutate_campaign_criteria(customer_id=customer_id, operations=ops)


def _create_ad_group(client, customer_id: str, campaign_resource_name: str) -> str:
    ag_svc = client.get_service("AdGroupService")
    op = client.get_type("AdGroupOperation")
    ag = op.create
    ag.name = f"Goalz Ad Group {uuid4().hex[:8]}"
    ag.status = client.enums.AdGroupStatusEnum.ENABLED
    ag.campaign = campaign_resource_name
    resp = ag_svc.mutate_ad_groups(customer_id=customer_id, operations=[op])
    return resp.results[0].resource_name


def _create_app_ad(
    client,
    customer_id: str,
    ad_group_resource_name: str,
    headlines: list[str],
    descriptions: list[str],
) -> None:
    ad_svc = client.get_service("AdGroupAdService")
    op = client.get_type("AdGroupAdOperation")
    aga = op.create
    aga.status = client.enums.AdGroupAdStatusEnum.ENABLED
    aga.ad_group = ad_group_resource_name

    def text_asset(text: str):
        a = client.get_type("AdTextAsset")
        a.text = text
        return a

    aga.ad.app_ad.headlines.extend([text_asset(t) for t in headlines])
    aga.ad.app_ad.descriptions.extend([text_asset(t) for t in descriptions])

    ad_svc.mutate_ad_group_ads(customer_id=customer_id, operations=[op])


@dataclass(frozen=True)
class LaunchParams:
    campaign_name: str
    daily_budget_usd: float
    target_cpa_usd: float
    dry_run: bool


def launch_goalz_app_campaign(
    *,
    manifest_path: Path,
    ad_copy_path: Path,
    params: LaunchParams,
) -> dict[str, object]:
    """Create (or resume) a Goalz iOS App campaign via the Google Ads API.

    Idempotent: if ``params.campaign_name`` already exists, PAUSED campaigns are
    enabled; ENABLED campaigns are left as-is.
    """
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    app_store = manifest.get("app_store")
    if not isinstance(app_store, dict):
        raise GoogleAdsLaunchError("app_manifest.json must contain an app_store object.")
    bundle_id = str(manifest.get("bundle_id") or "").strip()
    if not bundle_id:
        raise GoogleAdsLaunchError("app_manifest.json must set bundle_id.")

    if params.dry_run:
        return {
            "dry_run": True,
            "campaign_name": params.campaign_name,
            "daily_budget_micros": _usd_to_micros(params.daily_budget_usd),
            "target_cpa_micros": _usd_to_micros(params.target_cpa_usd),
            "bundle_id": bundle_id,
        }

    env = load_google_ads_env()
    client = build_google_ads_client(env)
    customer_id = env.customer_id

    headlines, descriptions = _load_ad_copy(ad_copy_path)
    daily_micros = _usd_to_micros(params.daily_budget_usd)
    target_cpa_micros = _usd_to_micros(params.target_cpa_usd)

    existing = _find_managed_campaign(client, customer_id, params.campaign_name)
    enabled = client.enums.CampaignStatusEnum.ENABLED
    paused = client.enums.CampaignStatusEnum.PAUSED
    if existing is not None:
        resource_name, status = existing
        if status == enabled:
            return {
                "already_exists": True,
                "campaign_resource_name": resource_name,
                "status": "ENABLED",
                "action": "none",
            }
        if status == paused:
            _enable_campaign(client, customer_id, resource_name)
            return {
                "already_exists": True,
                "campaign_resource_name": resource_name,
                "status": "ENABLED",
                "action": "enabled_existing_paused_campaign",
            }
        return {
            "already_exists": True,
            "campaign_resource_name": resource_name,
            "status": repr(status),
            "action": "unexpected_status_no_changes",
        }

    try:
        from google.ads.googleads.errors import GoogleAdsException
    except ImportError as exc:
        raise GoogleAdsLaunchError(
            "google-ads is not installed. pip install -r requirements-growth.txt"
        ) from exc

    try:
        budget_rn = _create_budget(client, customer_id, daily_budget_micros=daily_micros)
        campaign_rn = _create_app_campaign(
            client,
            customer_id,
            budget_resource_name=budget_rn,
            campaign_name=params.campaign_name,
            bundle_id=bundle_id,
            target_cpa_micros=target_cpa_micros,
        )
        _add_us_english_targeting(client, customer_id, campaign_rn)
        ad_group_rn = _create_ad_group(client, customer_id, campaign_rn)
        _create_app_ad(client, customer_id, ad_group_rn, headlines, descriptions)
        _enable_campaign(client, customer_id, campaign_rn)
    except GoogleAdsException as exc:
        parts = [f"request_id={exc.request_id}"]
        for err in exc.failure.errors:
            parts.append(err.message)
        raise GoogleAdsLaunchError("\n".join(parts)) from exc
    except GoogleAdsMetricsError as exc:
        raise GoogleAdsLaunchError(str(exc)) from exc

    return {
        "already_exists": False,
        "campaign_resource_name": campaign_rn,
        "budget_created": budget_rn,
        "status": "ENABLED",
        "action": "created_app_campaign",
    }


def default_launch_params() -> LaunchParams:
    name = os.getenv("GOOGLE_ADS_GOALZ_CAMPAIGN_NAME", "Goalz Autonomous Launch").strip() or "Goalz Autonomous Launch"
    daily = float(os.getenv("GOOGLE_ADS_GOALZ_DAILY_BUDGET_USD", "7"))
    tcpa = float(os.getenv("GOOGLE_ADS_GOALZ_TARGET_CPA_USD", "5"))
    dry = os.getenv("GOOGLE_ADS_LAUNCH_DRY_RUN", "").lower() in ("1", "true", "yes")
    return LaunchParams(campaign_name=name, daily_budget_usd=daily, target_cpa_usd=tcpa, dry_run=dry)
