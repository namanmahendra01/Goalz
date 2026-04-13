# Goalz Growth Agent Secrets

Add these to the GitHub repository as `Settings -> Secrets and variables -> Actions`.

Fastest CLI helper:

```bash
python3 -m growth_agent.cli secret-guide \
  --config growth_agent/config/default.json
```

That prints the exact `gh secret set ...` commands required for the current ads-only contract.

## Google Ads

- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_CUSTOMER_ID`
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_REFRESH_TOKEN`

Recommended additional repo variables later:

- search campaign IDs
- keyword group IDs
- geo targets

## Apple Search Ads

- `APPLE_SEARCH_ADS_ORG_ID`
- `APPLE_SEARCH_ADS_CERTIFICATE_PEM`
- `APPLE_SEARCH_ADS_KEY_ID`
- `APPLE_SEARCH_ADS_PRIVATE_KEY_PEM`

Recommended additional repo variables later:

- primary campaign IDs
- ad group IDs
- keyword group IDs

## Meta Ads

- `META_ACCESS_TOKEN`
- `META_AD_ACCOUNT_ID`
- `META_APP_ID`
- `META_APP_SECRET`

Recommended additional repo variables later:

- primary campaign IDs
- ad set IDs
- creative IDs

## Important

- Keep all credentials in GitHub Secrets only.
- Do not commit tokens, PEM contents, or account IDs to the repository.
- Start by adding secrets and running the `Validate Goalz Growth Secrets` workflow manually.
- Replace `growth_agent/config/sample_metrics.json` with real metrics collection before trusting the daily planner for actual spend changes.
- Current live V1 is ads-only: Google Search, Apple Search Ads, and Meta Ads.

## CLI examples

Single-line secrets:

```bash
printf '%s' "$META_APP_ID" | gh secret set META_APP_ID
printf '%s' "$META_APP_SECRET" | gh secret set META_APP_SECRET
printf '%s' "$GOOGLE_ADS_CUSTOMER_ID" | gh secret set GOOGLE_ADS_CUSTOMER_ID
```

PEM/file secrets:

```bash
gh secret set APPLE_SEARCH_ADS_PRIVATE_KEY_PEM < private_key.pem
gh secret set APPLE_SEARCH_ADS_CERTIFICATE_PEM < certificate.pem
```
