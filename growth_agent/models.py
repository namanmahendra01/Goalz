from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BudgetConfig:
    daily_max_usd: int
    channel_caps_usd: dict[str, int]


@dataclass(frozen=True)
class GuardrailConfig:
    min_blended_roas: float
    min_spend_before_pause_usd: int


@dataclass(frozen=True)
class ChannelConfig:
    enabled: bool
    mode: str


@dataclass(frozen=True)
class AppConfig:
    budget: BudgetConfig
    guardrails: GuardrailConfig
    channels: dict[str, ChannelConfig]

    def enabled_channels(self) -> list[str]:
        return sorted(
            name for name, channel in self.channels.items()
            if channel.enabled and channel.mode != "off"
        )


@dataclass(frozen=True)
class ChannelMetrics:
    spend_usd: float
    revenue_usd: float
    roas: float
    conversions: int


@dataclass(frozen=True)
class MetricsSnapshot:
    blended_roas: float
    attributed_revenue_usd: float
    total_marketing_spend_usd: float
    channels: dict[str, ChannelMetrics]


@dataclass(frozen=True)
class Action:
    code: str
    payload: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanSummary:
    mode: str
    blended_roas: float


@dataclass(frozen=True)
class DailyPlan:
    summary: PlanSummary
    actions: list[Action]


@dataclass(frozen=True)
class WorkflowResult:
    plan: DailyPlan
    missing_secrets: dict[str, list[str]]
    report_markdown: str
