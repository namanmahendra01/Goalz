import Foundation

public enum GoalDayInput {
    public static func normalizedDayCount(from text: String, fallback: Int, range: ClosedRange<Int> = 1...365) -> Int {
        guard let value = Int(text.trimmingCharacters(in: .whitespacesAndNewlines)) else {
            return fallback
        }

        return min(max(value, range.lowerBound), range.upperBound)
    }
}
