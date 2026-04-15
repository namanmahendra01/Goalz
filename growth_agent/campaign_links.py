from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def append_utm_params(
    app_store_url: str,
    *,
    source: str,
    medium: str = "paid",
    campaign: str = "goalz_launch_v1",
    content: str,
) -> str:
    parsed = urlparse(app_store_url.strip())
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    query = dict(pairs)
    query["utm_source"] = source
    query["utm_medium"] = medium
    query["utm_campaign"] = campaign
    query["utm_content"] = content
    new_query = urlencode(query)
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )


def tracking_urls_for_channels(
    app_store_url: str,
    *,
    content: str,
    campaign: str = "goalz_launch_v1",
) -> dict[str, str]:
    return {
        "google": append_utm_params(
            app_store_url, source="google", campaign=campaign, content=content
        ),
        "meta": append_utm_params(
            app_store_url, source="meta", campaign=campaign, content=content
        ),
        "apple_search": append_utm_params(
            app_store_url, source="apple_search", campaign=campaign, content=content
        ),
    }


def load_app_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def campaign_asset_bundle(manifest_path: Path, *, content: str, campaign: str) -> dict[str, object]:
    manifest = load_app_manifest(manifest_path)
    app_store = manifest.get("app_store")
    if not isinstance(app_store, dict):
        raise ValueError("app_manifest.json requires an app_store object")
    url_us = str(app_store["url_us"])
    return {
        "app_name": manifest.get("app_name"),
        "bundle_id": manifest.get("bundle_id"),
        "tracking_urls": tracking_urls_for_channels(url_us, content=content, campaign=campaign),
    }
