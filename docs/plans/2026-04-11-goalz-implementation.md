# Goalz Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a glass-styled SwiftUI iOS app that lets a user create one goal, persist it, preview it, and expose it through Home Screen and Lock Screen widgets.

**Architecture:** Keep the app focused around a single shared goal model and a lightweight storage service backed by an app-group `UserDefaults` suite. Build the SwiftUI app as a small setup flow plus a tracker screen, and mirror the same shared model inside a WidgetKit extension so widgets refresh from the same persisted source.

**Tech Stack:** SwiftUI, WidgetKit, XCTest, app-group `UserDefaults`, Xcode project target configuration.

---

### Task 1: Document and scaffold the shared architecture

**Files:**
- Create: `Goalz/Shared/Goal.swift`
- Create: `Goalz/Shared/GoalTheme.swift`
- Create: `Goalz/Shared/GoalSnapshot.swift`
- Create: `Goalz/Shared/GoalStore.swift`
- Create: `Goalz/Shared/ProgressCalculator.swift`

**Step 1: Write the failing test**

Create tests that assert:
- a goal can round-trip through storage
- progress math returns elapsed and remaining days correctly
- empty storage returns no active goal

**Step 2: Run test to verify it fails**

Run: `xcodebuild test -project Goalz.xcodeproj -scheme Goalz -destination 'platform=iOS Simulator,name=iPhone 16'`

Expected: test target or shared logic tests fail because the model and store do not exist yet.

**Step 3: Write minimal implementation**

Implement codable goal/theme/progress types and a storage service that reads and writes the active goal from shared defaults.

**Step 4: Run test to verify it passes**

Run the same `xcodebuild test` command and confirm the new logic tests pass.

### Task 2: Build the setup flow

**Files:**
- Modify: `Goalz/ContentView.swift`
- Create: `Goalz/Features/Setup/QuickSetupView.swift`
- Create: `Goalz/Features/Setup/ThemePickerView.swift`
- Create: `Goalz/Features/Setup/WidgetPreviewCard.swift`
- Create: `Goalz/UI/Glass/GlassCard.swift`
- Create: `Goalz/UI/Glass/GlassBackground.swift`

**Step 1: Write the failing test**

Add a focused view-model or storage-driven test proving that saving from setup creates an active goal with the selected theme and duration.

**Step 2: Run test to verify it fails**

Run the specific test target/suite and confirm save behavior is not implemented.

**Step 3: Write minimal implementation**

Create the onboarding/setup experience, theme selection, live preview cards, and save action that persists through the shared store.

**Step 4: Run test to verify it passes**

Re-run the focused test and then the full test suite.

### Task 3: Build the live tracker screen

**Files:**
- Create: `Goalz/Features/Tracker/LiveTrackerView.swift`
- Create: `Goalz/Features/Tracker/ProgressGridView.swift`
- Create: `Goalz/Features/Tracker/TrackerMetricCard.swift`
- Modify: `Goalz/ContentView.swift`

**Step 1: Write the failing test**

Add a pure-logic test for the tracker snapshot that verifies labels for current day, remaining days, and completion state.

**Step 2: Run test to verify it fails**

Run the focused test and confirm the tracker snapshot/presentation values are missing.

**Step 3: Write minimal implementation**

Add the tracker view and supporting presentation logic using the shared progress calculator.

**Step 4: Run test to verify it passes**

Run the focused tests and then the full suite.

### Task 4: Add the widget extension

**Files:**
- Create: `GoalzWidget/GoalzWidgetBundle.swift`
- Create: `GoalzWidget/GoalzWidget.swift`
- Create: `GoalzWidget/GoalzWidgetEntry.swift`
- Create: `GoalzWidget/GoalzWidgetProvider.swift`
- Create: `GoalzWidget/GoalzWidgetViews.swift`
- Create: `GoalzWidget/Shared/` copies or references for shared model files as needed
- Modify: `Goalz.xcodeproj/project.pbxproj`

**Step 1: Write the failing test**

Add or expand logic tests that verify widget entry generation from stored goal data and empty-state fallback behavior.

**Step 2: Run test to verify it fails**

Run the focused tests or build command and confirm widget-related types/targets are missing.

**Step 3: Write minimal implementation**

Create the widget extension, connect app-group storage, and support:
- `systemSmall`
- `systemMedium`
- `accessoryCircular`
- `accessoryRectangular`

**Step 4: Run test to verify it passes**

Run tests and a simulator build for the app and widget targets.

### Task 5: Polish, verify, and keep it honest

**Files:**
- Modify nearby files as needed for compile fixes and visual polish

**Step 1: Verification**

Run:
- `xcodebuild test -project Goalz.xcodeproj -scheme Goalz -destination 'platform=iOS Simulator,name=iPhone 16'`
- `xcodebuild build -project Goalz.xcodeproj -scheme Goalz -destination 'generic/platform=iOS'`

**Step 2: Lint and diagnostics**

Read lints for the modified files and fix any issues introduced by the implementation.

**Step 3: Final check**

Verify:
- first launch shows setup
- save transitions to tracker
- tracker reflects live progress
- widgets read the saved goal
- lock and home screen families compile successfully
