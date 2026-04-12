import Foundation

public enum ProgressCalculator {
    public static func makeSnapshot(for goal: Goal, now: Date = .now, calendar: Calendar = .current) -> GoalSnapshot {
        let startDay = calendar.startOfDay(for: goal.startDate)
        let currentDay = calendar.startOfDay(for: now)
        let elapsedIntervals = calendar.dateComponents([.day], from: startDay, to: currentDay).day ?? 0
        let elapsedDays = max(1, min(goal.totalDays, elapsedIntervals + 1))
        let remainingDays = max(0, goal.totalDays - elapsedDays)
        let progress = min(1, max(0, Double(elapsedDays) / Double(goal.totalDays)))

        return GoalSnapshot(
            elapsedDays: elapsedDays,
            remainingDays: remainingDays,
            totalDays: goal.totalDays,
            progress: progress,
            isComplete: remainingDays == 0
        )
    }

    public static func makeTimelineDates(for goal: Goal, now: Date = .now, calendar: Calendar = .current) -> [Date] {
        let startDay = calendar.startOfDay(for: goal.startDate)
        let currentDay = calendar.startOfDay(for: now)
        let totalOffsets = max(0, goal.totalDays - 1)

        let futureBoundaries = (0...totalOffsets).compactMap { offset -> Date? in
            guard let day = calendar.date(byAdding: .day, value: offset, to: startDay) else {
                return nil
            }

            guard day > now, day >= currentDay else {
                return nil
            }

            return day
        }

        return [now] + futureBoundaries
    }

    public static func makeDotStates(for snapshot: GoalSnapshot) -> [Bool] {
        let filledDots = min(snapshot.elapsedDays, snapshot.totalDays)
        return (0..<snapshot.totalDays).map { $0 < filledDots }
    }
}
