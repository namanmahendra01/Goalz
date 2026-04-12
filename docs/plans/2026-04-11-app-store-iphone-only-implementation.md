# App Store iPhone-Only Release Prep Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prepare Goalz for App Store release as an iPhone-only app with a valid archive path.

**Architecture:** Keep this scoped to project configuration and verification. Update the app and widget target settings so the app is iPhone-only, remove extra non-iPhone supported platforms from the main app target, and verify the project archives successfully for generic iOS release builds.

**Tech Stack:** Xcode project build settings, WidgetKit target configuration, `xcodebuild` verification.

---

### Task 1: Lock the project to iPhone only

**Files:**
- Modify: `Goalz.xcodeproj/project.pbxproj`

**Step 1: Update app target settings**

Set:
- app target `TARGETED_DEVICE_FAMILY = 1`
- app target `SUPPORTED_PLATFORMS = "iphoneos iphonesimulator"`

**Step 2: Update widget target settings**

Set:
- widget target `TARGETED_DEVICE_FAMILY = 1`

**Step 3: Verify settings**

Run:
`xcodebuild -showBuildSettings -project "Goalz.xcodeproj" -scheme "Goalz" | awk '/SUPPORTED_PLATFORMS|TARGETED_DEVICE_FAMILY/ {print}'`

Expected:
- only `iphoneos iphonesimulator`
- only `TARGETED_DEVICE_FAMILY = 1`

### Task 2: Verify release readiness

**Files:**
- Modify nearby config only if archive verification reveals a release blocker

**Step 1: Build simulator**

Run:
`xcodebuild build -project "Goalz.xcodeproj" -scheme "Goalz" -destination 'generic/platform=iOS Simulator'`

Expected: PASS

**Step 2: Archive for generic iOS**

Run:
`xcodebuild archive -project "Goalz.xcodeproj" -scheme "Goalz" -destination 'generic/platform=iOS' -archivePath "/tmp/Goalz.xcarchive"`

Expected: PASS

**Step 3: Report remaining App Store checklist items**

If archive succeeds, report what is still manual:
- App Store Connect metadata
- screenshots
- release notes
- provisioning/team review
