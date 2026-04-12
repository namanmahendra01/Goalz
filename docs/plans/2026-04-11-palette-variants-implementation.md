# Palette Variants Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand Goalz from a small fixed palette set to 10 named palettes with light and dark variants, and apply those variants consistently in the app preview and widgets.

**Architecture:** Keep palette data in shared model code so tests, app UI, and widget rendering all read the same source of truth. Represent each theme as a named palette with two variant triplets: background, completed dots, and remaining dots. Use environment color scheme in SwiftUI/widget views to pick the correct variant at render time.

**Tech Stack:** SwiftUI, WidgetKit, XCTest via Swift Testing, shared Swift model code.

---

### Task 1: Expand shared palette model

**Files:**
- Modify: `Goalz/Shared/GoalTheme.swift`
- Modify: `GoalzCoreTests/GoalzCoreTests.swift`

**Step 1: Write the failing test**

Add tests verifying:
- there are exactly 10 theme cases
- each theme exposes both light and dark palette variants
- each variant provides background/completed/remaining colors

**Step 2: Run test to verify it fails**

Run: `swift test`

Expected: FAIL because the current theme model only supports a small palette set without explicit variants.

**Step 3: Write minimal implementation**

Add 10 theme cases and shared palette structs with light/dark values.

**Step 4: Run test to verify it passes**

Run: `swift test`

Expected: PASS.

### Task 2: Apply palette variants to app and widget

**Files:**
- Modify: `Goalz/UI/GlassStyle.swift`
- Modify: `Goalz/Features/Setup/QuickSetupView.swift`
- Modify: `GoalzWidget/GoalzWidget.swift`

**Step 1: Write the failing test**

Add a focused shared test for one theme to verify variant selection returns distinct light/dark colors.

**Step 2: Run test to verify it fails**

Run: `swift test`

Expected: FAIL because variant selection helpers do not exist yet.

**Step 3: Write minimal implementation**

Update app preview/theme picker and widget rendering to use the new palette model.

**Step 4: Run test to verify it passes**

Run:
- `swift test`
- `xcodebuild build -project "Goalz.xcodeproj" -scheme "Goalz" -destination 'generic/platform=iOS Simulator'`

Expected: PASS.
