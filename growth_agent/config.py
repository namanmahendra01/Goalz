from __future__ import annotations

import json
from pathlib import Path

from growth_agent.models import AppConfig, BudgetConfig, ChannelConfig, GuardrailConfig


def load_config(path: Path) -> AppConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    budget = BudgetConfig(
        daily_max_usd=int(payload["budget"]["daily_max_usd"]),
        channel_caps_usd={key: int(value) for key, value in payload["budget"]["channel_caps_usd"].items()},
    )
    guardrails = GuardrailConfig(
        min_blended_roas=float(payload["guardrails"]["min_blended_roas"]),
        min_spend_before_pause_usd=int(payload["guardrails"]["min_spend_before_pause_usd"]),
    )
    channels = {
        name: ChannelConfig(
            enabled=bool(config["enabled"]),
            mode=str(config["mode"]),
        )
        for name, config in payload["channels"].items()
    }
    return AppConfig(
        budget=budget,
        guardrails=guardrails,
        channels=channels,
    )
