from __future__ import annotations

from growth_agent.models import WorkflowResult


def render_report(result: WorkflowResult) -> str:
    lines = [
        "# Goalz Growth Agent Daily Report",
        "",
        f"- Mode: `{result.plan.summary.mode}`",
        f"- Blended ROAS: `{result.plan.summary.blended_roas:.2f}`",
        "",
        "## Actions",
    ]

    if result.plan.actions:
        for action in result.plan.actions:
            lines.append(f"- `{action.code}`")
    else:
        lines.append("- No actions planned.")

    lines.extend(["", "## Missing Secrets"])
    if result.missing_secrets:
        for channel, secrets in sorted(result.missing_secrets.items()):
            lines.append(f"- `{channel}`: {', '.join(f'`{secret}`' for secret in secrets)}")
    else:
        lines.append("- None")

    lines.append("")
    return "\n".join(lines)
