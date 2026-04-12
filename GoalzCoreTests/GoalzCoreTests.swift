import Foundation
import Testing
@testable import GoalzCore

private func makeCalendar() -> Calendar {
    var calendar = Calendar(identifier: .gregorian)
    calendar.timeZone = TimeZone(secondsFromGMT: 0)!
    return calendar
}

@Test("empty storage returns no active goal")
func emptyStorageReturnsNoGoal() throws {
    let store = GoalStore(userDefaults: UserDefaults(suiteName: "tests.goalz.empty")!)

    store.clearGoal()

    #expect(store.loadGoal() == nil)
}

@Test("goal round-trips through storage")
func goalRoundTripsThroughStorage() throws {
    let defaults = UserDefaults(suiteName: "tests.goalz.roundtrip")!
    let store = GoalStore(userDefaults: defaults)
    let goal = Goal(
        title: "Ship Goalz",
        totalDays: 30,
        startDate: Date(timeIntervalSince1970: 1_700_000_000),
        theme: .sunset,
        widgetStyle: .ring
    )

    store.clearGoal()
    store.saveGoal(goal)

    #expect(store.loadGoal() == goal)
}

@Test("progress calculator returns elapsed and remaining days")
func progressCalculatorBuildsExpectedSnapshot() throws {
    let goal = Goal(
        title: "30 Day Run",
        totalDays: 30,
        startDate: Date(timeIntervalSince1970: 1_700_000_000),
        theme: .electric,
        widgetStyle: .filled
    )
    let now = goal.startDate.addingTimeInterval(60 * 60 * 24 * 4)

    let snapshot = ProgressCalculator.makeSnapshot(for: goal, now: now)

    #expect(snapshot.elapsedDays == 5)
    #expect(snapshot.remainingDays == 25)
    #expect(snapshot.isComplete == false)
    #expect(snapshot.progress == 5.0 / 30.0)
}

@Test("progress calculator marks final day as complete")
func progressCalculatorMarksCompletion() throws {
    let goal = Goal(
        title: "Finish",
        totalDays: 7,
        startDate: Date(timeIntervalSince1970: 1_700_000_000),
        theme: .sunset,
        widgetStyle: .minimal
    )
    let now = goal.startDate.addingTimeInterval(60 * 60 * 24 * 8)

    let snapshot = ProgressCalculator.makeSnapshot(for: goal, now: now)

    #expect(snapshot.elapsedDays == 7)
    #expect(snapshot.remainingDays == 0)
    #expect(snapshot.isComplete == true)
    #expect(snapshot.progress == 1)
}

@Test("progress calculator advances on the next calendar day")
func progressCalculatorAdvancesOnNextCalendarDay() throws {
    let calendar = makeCalendar()
    let startDate = Date(timeIntervalSince1970: 1_700_010_800) // 2023-11-14 01:00:00 UTC
    let nextDayMorning = Date(timeIntervalSince1970: 1_700_093_600) // 2023-11-15 00:00:00 UTC
    let goal = Goal(
        title: "Read",
        totalDays: 10,
        startDate: startDate,
        theme: .sunset,
        widgetStyle: .filled
    )

    let snapshot = ProgressCalculator.makeSnapshot(for: goal, now: nextDayMorning, calendar: calendar)

    #expect(snapshot.elapsedDays == 2)
    #expect(snapshot.remainingDays == 8)
}

@Test("timeline dates are generated for each remaining day boundary")
func timelineDatesAreGeneratedForEachDayBoundary() throws {
    let calendar = makeCalendar()
    let startDate = Date(timeIntervalSince1970: 1_700_010_800) // 2023-11-14 01:00:00 UTC
    let now = Date(timeIntervalSince1970: 1_700_020_000) // 2023-11-14 03:33:20 UTC
    let goal = Goal(
        title: "Sprint",
        totalDays: 3,
        startDate: startDate,
        theme: .electric,
        widgetStyle: .filled
    )

    let dates = ProgressCalculator.makeTimelineDates(for: goal, now: now, calendar: calendar)

    #expect(dates.count == 3)
    #expect(dates[0] == now)
    #expect(dates[1] == Date(timeIntervalSince1970: 1_700_092_800)) // 2023-11-15 00:00:00 UTC
    #expect(dates[2] == Date(timeIntervalSince1970: 1_700_179_200)) // 2023-11-16 00:00:00 UTC
}

@Test("dot states match total days exactly")
func dotStatesMatchTotalDaysExactly() throws {
    let snapshot = GoalSnapshot(
        elapsedDays: 1,
        remainingDays: 88,
        totalDays: 89,
        progress: 1.0 / 89.0,
        isComplete: false
    )

    let dots = ProgressCalculator.makeDotStates(for: snapshot)

    #expect(dots.count == 89)
    #expect(dots.filter { $0 }.count == 1)
    #expect(dots.filter { !$0 }.count == 88)
}

@Test("themes expose readable widget palette colors")
func themesExposeReadableWidgetPaletteColors() throws {
    #expect(GoalTheme.allCases.count == 10)
    #expect(GoalTheme.sunset.palette(for: .light).backgroundHex == "#FFF5EF")
    #expect(GoalTheme.sunset.palette(for: .dark).backgroundHex == "#23161B")
    #expect(GoalTheme.ocean.palette(for: .dark).completedHex == "#69A8FF")
    #expect(GoalTheme.iceBlue.palette(for: .light).remainingHex == "#A9BED0")
}

@Test("theme variants differ between light and dark")
func themeVariantsDifferBetweenLightAndDark() throws {
    let light = GoalTheme.forest.palette(for: .light)
    let dark = GoalTheme.forest.palette(for: .dark)

    #expect(light.backgroundHex != dark.backgroundHex)
    #expect(light.completedHex != dark.completedHex)
    #expect(light.remainingHex != dark.remainingHex)
}

@Test("theme text colors stay readable across variants")
func themeTextColorsStayReadableAcrossVariants() throws {
    #expect(GoalTheme.sunset.primaryTextHex(for: .light) == "#111418")
    #expect(GoalTheme.sunset.primaryTextHex(for: .dark) == "#F8FAFC")
    #expect(GoalTheme.ocean.secondaryTextHex(for: .light) == "#5B6470")
    #expect(GoalTheme.ocean.secondaryTextHex(for: .dark) == "#A7B4C4")
}

@Test("typed day input is parsed and clamped")
func typedDayInputIsParsedAndClamped() throws {
    #expect(GoalDayInput.normalizedDayCount(from: "61", fallback: 30) == 61)
    #expect(GoalDayInput.normalizedDayCount(from: "0", fallback: 30) == 1)
    #expect(GoalDayInput.normalizedDayCount(from: "999", fallback: 30) == 365)
    #expect(GoalDayInput.normalizedDayCount(from: "abc", fallback: 30) == 30)
}

@Test("motivation quote is stable for the same goal")
func motivationQuoteIsStableForSameGoal() throws {
    let goal = Goal(
        id: UUID(uuidString: "11111111-1111-1111-1111-111111111111")!,
        title: "Run",
        totalDays: 30,
        startDate: Date(timeIntervalSince1970: 1_700_000_000),
        theme: .sunset,
        widgetStyle: .filled
    )

    let first = GoalExperienceContent.quote(for: goal)
    let second = GoalExperienceContent.quote(for: goal)

    #expect(first == second)
    #expect(first.isEmpty == false)
}

@Test("widget guide includes home and lock screen steps")
func widgetGuideIncludesHomeAndLockScreenSteps() throws {
    #expect(GoalExperienceContent.homeScreenSteps.count == 3)
    #expect(GoalExperienceContent.lockScreenSteps.count == 3)
    #expect(GoalExperienceContent.successMessage == "Goal created")
    #expect(GoalExperienceContent.resetWarningTitle == "Start over?")
}
