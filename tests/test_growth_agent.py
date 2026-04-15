import json
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse
from pathlib import Path

from growth_agent.config import load_config
from growth_agent.models import ChannelMetrics, MetricsSnapshot
from growth_agent.oauth import (
    GOOGLE_ADS_SCOPE,
    META_GRAPH_BASE_URL,
    build_google_ads_authorization_url,
    build_google_ads_token_payload,
    build_meta_debug_token_url,
)
from growth_agent.planner import build_daily_plan
from growth_agent.campaign_links import append_utm_params, campaign_asset_bundle
from growth_agent.google_ads import (
    channel_metrics_from_google_totals,
    merge_google_channel_metrics,
    normalize_google_ads_customer_id,
)
from growth_agent.runtime import (
    missing_secrets_for_enabled_channels,
    run_daily_workflow,
    run_daily_workflow_with_metrics,
    load_metrics_snapshot,
)


class GrowthAgentConfigTests(unittest.TestCase):
    def test_load_config_parses_enabled_channels_and_guardrails(self) -> None:
        payload = {
            "budget": {"daily_max_usd": 25, "channel_caps_usd": {"google_ads": 7, "apple_search_ads": 10, "meta_ads": 8}},
            "guardrails": {"min_blended_roas": 5.0, "min_spend_before_pause_usd": 15},
            "channels": {
                "google_ads": {"enabled": True, "mode": "live"},
                "apple_search_ads": {"enabled": True, "mode": "live"},
                "meta_ads": {"enabled": True, "mode": "live"},
                "x_posts": {"enabled": False, "mode": "off"},
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(json.dumps(payload), encoding="utf-8")

            config = load_config(config_path)

        self.assertEqual(config.budget.daily_max_usd, 25)
        self.assertEqual(config.guardrails.min_blended_roas, 5.0)
        self.assertEqual(config.enabled_channels(), ["apple_search_ads", "google_ads", "meta_ads"])
        self.assertEqual(config.channels["apple_search_ads"].mode, "live")

    def test_missing_secrets_only_checks_enabled_channels(self) -> None:
        payload = {
            "budget": {"daily_max_usd": 25, "channel_caps_usd": {}},
            "guardrails": {"min_blended_roas": 5.0, "min_spend_before_pause_usd": 15},
            "channels": {
                "google_ads": {"enabled": True, "mode": "live"},
                "apple_search_ads": {"enabled": True, "mode": "live"},
                "meta_ads": {"enabled": True, "mode": "live"},
                "x_posts": {"enabled": False, "mode": "off"},
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(json.dumps(payload), encoding="utf-8")
            config = load_config(config_path)

        missing = missing_secrets_for_enabled_channels(
            config,
            provided_secret_names={"APPLE_SEARCH_ADS_ORG_ID"},
        )

        self.assertEqual(
            missing,
            {
                "google_ads": ["GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET", "GOOGLE_ADS_CUSTOMER_ID", "GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_REFRESH_TOKEN"],
                "apple_search_ads": ["APPLE_SEARCH_ADS_CERTIFICATE_PEM", "APPLE_SEARCH_ADS_KEY_ID", "APPLE_SEARCH_ADS_PRIVATE_KEY_PEM"],
                "meta_ads": ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID", "META_APP_ID", "META_APP_SECRET"]
            },
        )


class GrowthPlannerTests(unittest.TestCase):
    def test_build_daily_plan_pauses_paid_channels_when_blended_roas_is_below_target(self) -> None:
        payload = {
            "budget": {"daily_max_usd": 25, "channel_caps_usd": {"google_ads": 7, "apple_search_ads": 10, "meta_ads": 8}},
            "guardrails": {"min_blended_roas": 5.0, "min_spend_before_pause_usd": 15},
            "channels": {
                "google_ads": {"enabled": True, "mode": "live"},
                "apple_search_ads": {"enabled": True, "mode": "live"},
                "meta_ads": {"enabled": True, "mode": "live"},
                "x_posts": {"enabled": False, "mode": "off"},
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(json.dumps(payload), encoding="utf-8")
            config = load_config(config_path)

        snapshot = MetricsSnapshot(
            blended_roas=2.4,
            attributed_revenue_usd=24,
            total_marketing_spend_usd=10,
            channels={
                "google_ads": ChannelMetrics(spend_usd=17, revenue_usd=30, roas=1.76, conversions=1),
                "apple_search_ads": ChannelMetrics(spend_usd=18, revenue_usd=40, roas=2.2, conversions=2),
                "meta_ads": ChannelMetrics(spend_usd=16, revenue_usd=20, roas=1.25, conversions=1),
            },
        )

        plan = build_daily_plan(config, snapshot)

        self.assertEqual(plan.summary.mode, "defensive")
        self.assertIn("pause_paid_channel:google_ads", [action.code for action in plan.actions])
        self.assertIn("pause_paid_channel:apple_search_ads", [action.code for action in plan.actions])
        self.assertIn("pause_paid_channel:meta_ads", [action.code for action in plan.actions])
        self.assertEqual(len(plan.actions), 3)

    def test_build_daily_plan_scales_best_paid_channel_within_cap(self) -> None:
        payload = {
            "budget": {"daily_max_usd": 25, "channel_caps_usd": {"google_ads": 7, "apple_search_ads": 10, "meta_ads": 8}},
            "guardrails": {"min_blended_roas": 5.0, "min_spend_before_pause_usd": 15},
            "channels": {
                "google_ads": {"enabled": True, "mode": "live"},
                "apple_search_ads": {"enabled": True, "mode": "live"},
                "meta_ads": {"enabled": True, "mode": "live"},
                "x_posts": {"enabled": False, "mode": "off"},
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            config_path.write_text(json.dumps(payload), encoding="utf-8")
            config = load_config(config_path)

        snapshot = MetricsSnapshot(
            blended_roas=6.1,
            attributed_revenue_usd=61,
            total_marketing_spend_usd=10,
            channels={
                "google_ads": ChannelMetrics(spend_usd=5, revenue_usd=35, roas=7.0, conversions=4),
                "apple_search_ads": ChannelMetrics(spend_usd=8, revenue_usd=56, roas=7.0, conversions=7),
                "meta_ads": ChannelMetrics(spend_usd=6, revenue_usd=18, roas=3.0, conversions=2),
            },
        )

        plan = build_daily_plan(config, snapshot)

        increase_actions = [action for action in plan.actions if action.code == "increase_budget:apple_search_ads"]
        self.assertEqual(plan.summary.mode, "growth")
        self.assertEqual(len(increase_actions), 1)
        self.assertEqual(increase_actions[0].payload["new_daily_cap_usd"], 10)
        self.assertNotIn("publish_content:x_posts", [action.code for action in plan.actions])


class CampaignLinksTests(unittest.TestCase):
    def test_append_utm_params_preserves_existing_query(self) -> None:
        base = "https://apps.apple.com/us/app/example/id123?mt=8"
        url = append_utm_params(base, source="google", content="c1")
        self.assertIn("mt=8", url)
        self.assertIn("utm_source=google", url)
        self.assertIn("utm_content=c1", url)

    def test_campaign_asset_bundle_reads_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "growth_agent" / "marketing" / "app_manifest.json"
        bundle = campaign_asset_bundle(manifest, content="test", campaign="goalz_launch_v1")
        self.assertIn("tracking_urls", bundle)
        urls = bundle["tracking_urls"]
        assert isinstance(urls, dict)
        self.assertIn("google", urls)
        self.assertTrue(str(urls["google"]).startswith("https://apps.apple.com/"))


class GoogleAdsMetricsTests(unittest.TestCase):
    def test_normalize_google_ads_customer_id_strips_formatting(self) -> None:
        self.assertEqual(normalize_google_ads_customer_id("123-456-7890"), "1234567890")

    def test_channel_metrics_from_google_totals_computes_roas(self) -> None:
        metrics = channel_metrics_from_google_totals(
            cost_micros=5_000_000,
            conversions_value=20.0,
            conversions=2.2,
        )
        self.assertAlmostEqual(metrics.spend_usd, 5.0)
        self.assertAlmostEqual(metrics.revenue_usd, 20.0)
        self.assertAlmostEqual(metrics.roas, 4.0)
        self.assertEqual(metrics.conversions, 2)

    def test_merge_google_channel_metrics_recomputes_blended_totals(self) -> None:
        snapshot = MetricsSnapshot(
            blended_roas=1.0,
            attributed_revenue_usd=1.0,
            total_marketing_spend_usd=1.0,
            channels={
                "google_ads": ChannelMetrics(spend_usd=5, revenue_usd=10, roas=2.0, conversions=1),
                "meta_ads": ChannelMetrics(spend_usd=5, revenue_usd=15, roas=3.0, conversions=2),
            },
        )
        google = ChannelMetrics(spend_usd=10, revenue_usd=40, roas=4.0, conversions=4)
        merged = merge_google_channel_metrics(snapshot, google)

        self.assertAlmostEqual(merged.channels["google_ads"].spend_usd, 10.0)
        self.assertAlmostEqual(merged.channels["meta_ads"].spend_usd, 5.0)
        self.assertAlmostEqual(merged.total_marketing_spend_usd, 15.0)
        self.assertAlmostEqual(merged.attributed_revenue_usd, 55.0)
        self.assertAlmostEqual(merged.blended_roas, 55.0 / 15.0)


class GrowthWorkflowSnapshotTests(unittest.TestCase):
    def test_run_daily_workflow_with_metrics_matches_file_loader(self) -> None:
        config_payload = {
            "budget": {"daily_max_usd": 25, "channel_caps_usd": {"google_ads": 7, "apple_search_ads": 10, "meta_ads": 8}},
            "guardrails": {"min_blended_roas": 5.0, "min_spend_before_pause_usd": 15},
            "channels": {
                "google_ads": {"enabled": True, "mode": "live"},
                "apple_search_ads": {"enabled": True, "mode": "live"},
                "meta_ads": {"enabled": True, "mode": "live"},
            },
        }
        metrics_payload = {
            "blended_roas": 5.8,
            "attributed_revenue_usd": 58,
            "total_marketing_spend_usd": 10,
            "channels": {
                "google_ads": {"spend_usd": 5, "revenue_usd": 35, "roas": 7.0, "conversions": 4},
                "apple_search_ads": {"spend_usd": 8, "revenue_usd": 56, "roas": 7.0, "conversions": 7},
                "meta_ads": {"spend_usd": 6, "revenue_usd": 18, "roas": 3.0, "conversions": 2},
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            metrics_path = Path(tmp_dir) / "metrics.json"
            config_path.write_text(json.dumps(config_payload), encoding="utf-8")
            metrics_path.write_text(json.dumps(metrics_payload), encoding="utf-8")

            metrics = load_metrics_snapshot(metrics_path)
            from_file = run_daily_workflow(
                config_path=config_path,
                metrics_path=metrics_path,
                provided_secret_names=set(),
            )
            from_snapshot = run_daily_workflow_with_metrics(
                config_path=config_path,
                metrics=metrics,
                provided_secret_names=set(),
            )

        self.assertEqual(from_file.report_markdown, from_snapshot.report_markdown)


class GrowthWorkflowTests(unittest.TestCase):
    def test_run_daily_workflow_reports_missing_live_secrets(self) -> None:
        config_payload = {
            "budget": {"daily_max_usd": 25, "channel_caps_usd": {"google_ads": 7, "apple_search_ads": 10, "meta_ads": 8}},
            "guardrails": {"min_blended_roas": 5.0, "min_spend_before_pause_usd": 15},
            "channels": {
                "google_ads": {"enabled": True, "mode": "live"},
                "apple_search_ads": {"enabled": True, "mode": "live"},
                "meta_ads": {"enabled": True, "mode": "live"},
            },
        }
        metrics_payload = {
            "blended_roas": 5.8,
            "attributed_revenue_usd": 58,
            "total_marketing_spend_usd": 10,
            "channels": {
                "google_ads": {"spend_usd": 5, "revenue_usd": 35, "roas": 7.0, "conversions": 4},
                "apple_search_ads": {"spend_usd": 8, "revenue_usd": 56, "roas": 7.0, "conversions": 7},
                "meta_ads": {"spend_usd": 6, "revenue_usd": 18, "roas": 3.0, "conversions": 2},
            },
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            metrics_path = Path(tmp_dir) / "metrics.json"
            config_path.write_text(json.dumps(config_payload), encoding="utf-8")
            metrics_path.write_text(json.dumps(metrics_payload), encoding="utf-8")

            result = run_daily_workflow(
                config_path=config_path,
                metrics_path=metrics_path,
                provided_secret_names={"APPLE_SEARCH_ADS_ORG_ID"},
            )

        self.assertEqual(result.plan.summary.mode, "growth")
        self.assertIn("## Missing Secrets", result.report_markdown)
        self.assertIn("GOOGLE_ADS_DEVELOPER_TOKEN", result.report_markdown)
        self.assertEqual(result.missing_secrets["apple_search_ads"][0], "APPLE_SEARCH_ADS_CERTIFICATE_PEM")


class OAuthHelperTests(unittest.TestCase):
    def test_google_ads_authorization_url_contains_required_oauth_parameters(self) -> None:
        url = build_google_ads_authorization_url(
            client_id="client-123",
            redirect_uri="http://localhost:8080/callback",
            state="goalz-state",
        )

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "accounts.google.com")
        self.assertEqual(parsed.path, "/o/oauth2/v2/auth")
        self.assertEqual(params["client_id"], ["client-123"])
        self.assertEqual(params["redirect_uri"], ["http://localhost:8080/callback"])
        self.assertEqual(params["scope"], [GOOGLE_ADS_SCOPE])
        self.assertEqual(params["access_type"], ["offline"])
        self.assertEqual(params["prompt"], ["consent"])
        self.assertEqual(params["response_type"], ["code"])
        self.assertEqual(params["state"], ["goalz-state"])

    def test_google_ads_token_payload_matches_expected_exchange_contract(self) -> None:
        endpoint, payload = build_google_ads_token_payload(
            client_id="client-123",
            client_secret="secret-456",
            redirect_uri="http://localhost:8080/callback",
            code="auth-code",
        )

        self.assertEqual(endpoint, "https://oauth2.googleapis.com/token")
        self.assertEqual(
            payload,
            {
                "client_id": "client-123",
                "client_secret": "secret-456",
                "code": "auth-code",
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:8080/callback",
            },
        )

    def test_meta_debug_token_url_contains_expected_parameters(self) -> None:
        url = build_meta_debug_token_url(
            app_id="123",
            app_secret="456",
            input_token="user-token",
        )

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        self.assertEqual(f"{parsed.scheme}://{parsed.netloc}", META_GRAPH_BASE_URL)
        self.assertEqual(parsed.path, "/debug_token")
        self.assertEqual(params["input_token"], ["user-token"])
        self.assertEqual(params["access_token"], ["123|456"])


if __name__ == "__main__":
    unittest.main()
