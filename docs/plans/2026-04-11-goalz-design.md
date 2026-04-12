# Goalz Design

## Product Goal

Goalz is a focused iOS app that helps a user create one active goal, choose a countdown duration, personalize its visual style, and surface that goal as a Home Screen and Lock Screen widget.

## Experience Principles

- Fast setup: the first meaningful result should appear in under a minute.
- One active goal: reduce list management and keep the widget emotionally clear.
- Glass-first UI: use current iOS translucent materials, soft blur, and layered highlights instead of heavy cards and hard borders.
- Glanceable progress: the app and widget should communicate progress in one second.
- Personalization without clutter: offer curated themes and widget styles instead of deep customization menus.

## User Journey

### Entry

On first launch, the user sees a short promise and a primary action to create a goal.

### Quick Setup

The user enters:

- Goal title
- Number of days
- Theme
- Preferred widget emphasis

The screen uses large editorial typography, soft materials, and live previews inspired by the Stitch references.

### Save

When the user saves, the app persists the goal to shared app-group storage and refreshes widgets.

### Tracker

The main app becomes a live tracker view that shows:

- Goal title
- Day count and days remaining
- A simple progress grid
- Theme-aware glass cards
- A reset/edit action

### Widget Ready

The app includes a dedicated section explaining that widgets become available immediately but must still be added by the user through the iOS widget picker.

## Information Architecture

- `GoalzApp`: app entry and top-level routing
- `ContentView`: chooses between onboarding/setup and tracker
- Shared model layer: goal, theme, style, progress calculations, storage
- Reusable UI layer: glass surfaces, gradients, metric pills, progress grid
- Widget extension: small/medium Home Screen plus circular/rectangular Lock Screen families

## Visual Direction

The visual system blends the Stitch editorial references with current iOS liquid-glass patterns:

- translucent surfaces with blur and subtle tint
- saturated accent glows behind key elements
- oversized numeric hierarchy
- rounded geometry and nested materials
- restrained shadows and specular highlights

## Technical Direction

- SwiftUI for app UI
- WidgetKit for Home Screen and Lock Screen widgets
- Shared `UserDefaults` suite in an app group for app/widget synchronization
- Small pure-Swift logic layer for progress and widget presentation
- XCTest target covering progress calculations and storage encoding/decoding

## Constraints

- iOS cannot place widgets automatically; the app can only make them available.
- Widget content must remain concise because Lock Screen families have tight layout limits.
- Shared data model must stay simple so the widget timeline can decode quickly and reliably.
