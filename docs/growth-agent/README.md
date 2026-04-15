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
