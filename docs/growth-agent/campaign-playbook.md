# Goalz — Paid acquisition playbook (v1)

**Live listing (US):** [Goalz: Goal Countdown Widget on the App Store](https://apps.apple.com/us/app/goalz-goal-countdown-widget/id6762053420)

**Positioning:** One active goal, daily countdown, Home Screen + Lock Screen widgets. No ads, no account. Premium productivity ($4.99).

**Budget posture (starting):** ~**$25/day total** — align caps with repo config: Google **$7**, Apple Search Ads **$10**, Meta **$8** (tune after **7** days of data).

**Destination URL (use everywhere):**

```text
https://apps.apple.com/us/app/goalz-goal-countdown-widget/id6762053420?utm_source={source}&utm_medium=paid&utm_campaign=goalz_launch_v1&utm_content={creative}
```

Replace `{source}` with `google`, `meta`, or `apple_search`. Replace `{creative}` with a short slug (e.g. `countdown_widget`, `one_goal`, `lock_screen`).

---

## 1) Apple Search Ads (highest intent)

1. Open [Apple Search Ads](https://searchads.apple.com/).
2. **Campaign** → **App promotion** → choose **Goalz** (bundle `com.ziro.goalzdots.iphone`).
3. **Markets:** start **United States** (expand only after stable CPA).
4. **Match types:** brand + category keywords (examples to test): `goal tracker`, `countdown widget`, `lock screen widget goals`, `habit goal`, `single goal app`, `goal countdown`.
5. **Bidding:** start conservative CPT; raise only on keywords with installs at acceptable cost.
6. **Daily budget:** ~**$10** (stay within your global cap).
7. **Creatives:** use App Store screenshots; lead with “one goal + widgets + no clutter”.

**Note:** Complete **Business Details** and app selection in Apple Ads if the account shows ads on hold.

---

## 2) Google Ads — App or Search (pick one to start)

**Recommended for speed:** **App campaign** (Google will optimize across inventory) if your MCC/account is ready.

1. Open [Google Ads](https://ads.google.com/).
2. **New campaign** → objective **App promotion** → **App installs** (or **App engagement** later).
3. **Platform:** iOS → paste the **App Store URL** (with UTMs).
4. **Geo:** US to start. **Languages:** English.
5. **Budget:** daily ~**$7**; let learning run **~3–7 days** before big changes.
6. **Creatives:** 5–10 short headlines; emphasize widgets + single-goal focus. (Optional: copy bank in repo `growth_agent/marketing/ad_copy.json` on branch `feature/growth-agent-v1`.)
7. **Conversion:** ensure install / first-open signals are wired; for ROAS tracking you need **revenue-capable** conversion values in Google (premium purchase / modeled LTV if you use it).

---

## 3) Meta Ads (Facebook / Instagram)

1. Open [Meta Ads Manager](https://adsmanager.facebook.com/).
2. **Campaign** objective: **Sales** or **App promotion** (whichever matches your account + pixel/SKAN setup).
3. **Ad set:** iOS, US, placements automatic to start (or Advantage+ placements).
4. **Optimization:** purchases or installs depending on signal strength; iOS may be noisy early—keep creative volume high.
5. **Daily budget:** ~**$8**.
6. **Creative:** 9:16 and 1:1 short loops showing **Lock Screen + Home Screen widget** + in-app countdown.
7. **Link:** App Store URL with `utm_source=meta`.

Resolve **Business portfolio / restrictions** in Business Settings if Ads Manager blocks publishing.

---

## 4) Creative angles (keep honest, no hype)

- **Single-goal focus** vs cluttered multi-habit apps
- **Widgets always visible** (Home + Lock Screen)
- **Fast setup**, **no account**, **no ads**
- **30-day challenges**, study / fitness / shipping-a-project narratives

---

## 5) Measurement (blended ROAS)

**Definition:** `attributed_revenue / total_ad_spend` across channels (your growth agent uses this guardrail).

- **Apple / Google / Meta:** export spend from each; revenue from App Store Connect (units × price minus refunds) plus any analytics you trust.
- **Do not** pretend ROAS is precise until conversion values are stable.

---

## 6) Daily ops

- Repo **growth agent** (branch `feature/growth-agent-v1`): `daily-run` with `--google-live` pulls the Google slice of performance; Apple/Meta still need manual export or future API wiring.
- **Rule of thumb:** change one thing per day per channel (bid *or* creative *or* budget—not all three).

---

## 7) Compliance

- No misleading claims; widgets require supported iOS versions per [App Store listing](https://apps.apple.com/us/app/goalz-goal-countdown-widget/id6762053420).
- Privacy: your listing states data not collected—keep product behavior aligned with that.
