import Foundation

public struct GoalSnapshot: Equatable, Sendable {
    public var elapsedDays: Int
    public var remainingDays: Int
    public var totalDays: Int
    public var progress: Double
    public var isComplete: Bool

    public init(
        elapsedDays: Int,
        remainingDays: Int,
        totalDays: Int,
        progress: Double,
        isComplete: Bool
    ) {
        self.elapsedDays = elapsedDays
        self.remainingDays = remainingDays
        self.totalDays = totalDays
        self.progress = progress
        self.isComplete = isComplete
    }

    public var currentDayLabel: String {
        "Day \(elapsedDays) / \(totalDays)"
    }

    public var remainingLabel: String {
        remainingDays == 1 ? "1 day left" : "\(remainingDays) days left"
    }
}
