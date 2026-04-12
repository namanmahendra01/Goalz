import Foundation

public enum GoalExperienceContent {
    private static let quotes = [
        "One day at a time.",
        "Small steps still move you.",
        "Consistency beats intensity.",
        "Show up again tomorrow.",
        "Progress compounds quietly.",
    ]

    public static let successMessage = "Goal created"
    public static let resetWarningTitle = "Start over?"
    public static let resetWarningMessage = "Your countdown will start again from day one."

    public static let homeScreenSteps = [
        "Touch and hold the Home Screen.",
        "Tap Edit, then Add Widget.",
        "Search Goalz Dots and add it.",
    ]

    public static let lockScreenSteps = [
        "Touch and hold the Lock Screen.",
        "Tap Customize, then Lock Screen.",
        "Add Goalz Dots to a widget slot.",
    ]

    public static func quote(for goal: Goal) -> String {
        let seed = abs(goal.title.hashValue ^ goal.totalDays)
        return quotes[seed % quotes.count]
    }
}
