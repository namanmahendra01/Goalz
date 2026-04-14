from __future__ import annotations

from growth_agent.models import Action, AppConfig, DailyPlan, MetricsSnapshot, PlanSummary


PAID_CHANNELS = {"google_ads", "apple_search_ads", "meta_ads"}
CONTENT_CHANNELS = set()


def build_daily_plan(config: AppConfig, snapshot: MetricsSnapshot) -> DailyPlan:
    actions: list[Action] = []
    defensive_mode = snapshot.blended_roas < config.guardrails.min_blended_roas
    mode = "defensive" if defensive_mode else "growth"

    for channel_name in config.enabled_channels():
        if channel_name in CONTENT_CHANNELS:
            actions.append(Action(code=f"publish_content:{channel_name}", payload={"mode": mode}))
            continue

        channel_metrics = snapshot.channels.get(channel_name)
        if channel_name in PAID_CHANNELS and channel_metrics is not None:
            if defensive_mode and channel_metrics.spend_usd >= config.guardrails.min_spend_before_pause_usd:
                actions.append(Action(code=f"pause_paid_channel:{channel_name}"))
                continue

            current_cap = config.budget.channel_caps_usd.get(channel_name, 0)
            if (
                not defensive_mode
                and channel_metrics.roas >= config.guardrails.min_blended_roas
                and current_cap > 0
            ):
                increased_cap = min(
                    round(channel_metrics.spend_usd * 1.2),
                    current_cap,
                    config.budget.daily_max_usd,
                )
                if increased_cap > channel_metrics.spend_usd:
                    actions.append(
                        Action(
                            code=f"increase_budget:{channel_name}",
                            payload={"new_daily_cap_usd": increased_cap},
                        )
                    )

    return DailyPlan(
        summary=PlanSummary(mode=mode, blended_roas=snapshot.blended_roas),
        actions=actions,
    )
