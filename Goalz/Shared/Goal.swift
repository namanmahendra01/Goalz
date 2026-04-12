import Foundation

public struct Goal: Codable, Equatable, Sendable, Identifiable {
    public let id: UUID
    public var title: String
    public var totalDays: Int
    public var startDate: Date
    public var theme: GoalTheme
    public var widgetStyle: GoalWidgetStyle

    public init(
        id: UUID = UUID(),
        title: String,
        totalDays: Int,
        startDate: Date,
        theme: GoalTheme,
        widgetStyle: GoalWidgetStyle
    ) {
        self.id = id
        self.title = title
        self.totalDays = totalDays
        self.startDate = startDate
        self.theme = theme
        self.widgetStyle = widgetStyle
    }
}
