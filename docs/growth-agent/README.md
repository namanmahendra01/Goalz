# Goalz Growth Agent

This repository now includes a repo-contained growth control plane for `Goalz`.

Operating model:

- Cursor builds and improves the system.
- GitHub Actions runs the daily workflow.
- Ad platform credentials live in `GitHub Secrets`.
- Reports are emitted as GitHub Actions artifacts and summaries.

## What exists now

- `growth_agent/`
  - deterministic config loader
  - daily planner with ROAS guardrails
  - secret validation
  - markdown/json report generation
  - CLI entrypoint for Actions
- `.github/workflows/growth-agent-daily.yml`
  - daily scheduled run
  - manual trigger
  - report artifact upload
- `.github/workflows/validate-growth-secrets.yml`
  - manual secret completeness check
- `growth_agent/config/default.json`
  - budget, guardrails, and channel modes
- `growth_agent/prompts/`
  - marketing and safety policy prompts for Cursor-driven iteration

## Current runtime behavior

The current live V1 is intentionally conservative:

- it calculates the daily mode (`growth` or `defensive`)
- it plans actions such as pausing paid channels or increasing budget inside caps
- it reports missing secrets by channel
- it can optionally pull **live Google Ads** spend/conversion value for the `google_ads` slice of the metrics snapshot (see `--google-live`)
- it is ready for GitHub Actions scheduling

This gets the autonomous control loop and reporting in place first, which is the safest foundation for later platform-specific executors.

## Channel posture

- `Google Ads`: search-first paid automation
- `Apple Search Ads`: highest-intent app-store paid automation
- `Meta Ads`: paid social expansion after creatives and account targets are configured

## Live App Store

- [Goalz: Goal Countdown Widget (US)](https://apps.apple.com/us/app/goalz-goal-countdown-widget/id6762053420)

Campaign launch steps, budgets, and platform links: [campaign-playbook.md](./campaign-playbook.md) (and [campaign.html](./campaign.html) for a short HTML summary).

### Google Ads — fully automated App campaign (no UI)

After GitHub Actions secrets are set, the workflow **Google Ads — Goalz App campaign** (`.github/workflows/google-ads-launch.yml`) runs on a **weekly** schedule and can be triggered manually. It calls:

```bash
python3 -m growth_agent.cli google-ads-launch \
  --manifest growth_agent/marketing/app_manifest.json \
  --ad-copy growth_agent/marketing/ad_copy.json
```

This creates an **iOS App campaign** (bundle id from `app_manifest.json`), **US + English** targeting, **~$7/day** budget and **~$5 target CPA** by default (override via env: `GOOGLE_ADS_GOALZ_DAILY_BUDGET_USD`, `GOOGLE_ADS_GOALZ_TARGET_CPA_USD`, `GOOGLE_ADS_GOALZ_CAMPAIGN_NAME`). The run is **idempotent**: an existing **ENABLED** campaign named `Goalz Autonomous Launch` is left unchanged; a **PAUSED** one is re-enabled.

Dry run locally: add `--dry-run` or set `GOOGLE_ADS_LAUNCH_DRY_RUN=true`.

## Daily usage

Install Python deps once (includes the official Google Ads API client):

```bash
python3 -m pip install -r requirements-growth.txt
```

Local:

```bash
python3 -m growth_agent.cli daily-run \
  --config growth_agent/config/default.json \
  --metrics growth_agent/config/sample_metrics.json \
  --google-live \
  --report-out docs/growth-agent/daily-report.md \
  --json-out docs/growth-agent/daily-report.json
```

Omit `--google-live` if you only want file-based metrics (offline testing).

Paste-ready tracking URLs + headline/copy bank:

```bash
python3 -m growth_agent.cli campaign-assets
```

Optional: `--content lock_screen` to change `utm_content` for a specific creative.

Secrets validation:

```bash
python3 -m growth_agent.cli validate-secrets \
  --config growth_agent/config/default.json
```

CLI secret bootstrap guide:

```bash
python3 -m growth_agent.cli secret-guide \
  --config growth_agent/config/default.json
```

Google Ads OAuth URL generation:

```bash
python3 -m growth_agent.cli google-auth-url \
  --client-id "$GOOGLE_ADS_CLIENT_ID" \
  --redirect-uri http://localhost:8080/callback
```

Google Ads token exchange payload preview:

```bash
python3 -m growth_agent.cli google-token-payload \
  --client-id "$GOOGLE_ADS_CLIENT_ID" \
  --client-secret "$GOOGLE_ADS_CLIENT_SECRET" \
  --redirect-uri http://localhost:8080/callback \
  --code "AUTH_CODE"
```

Meta debug-token URL generation:

```bash
python3 -m growth_agent.cli meta-debug-url \
  --app-id "$META_APP_ID" \
  --app-secret "$META_APP_SECRET" \
  --input-token "$META_ACCESS_TOKEN"
```

## Final setup still needed

The remaining sure-needed inputs are all GitHub-side:

- platform secrets in `GitHub Secrets`
- channel-specific account and campaign target IDs
- replacement of sample metrics with live metrics collection

See:

- `docs/growth-agent/secrets.md`
- `growth_agent/config/default.json`
- `docs/growth-agent/secrets.md`
