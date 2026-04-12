import Foundation

public struct GoalStore {
    public static let suiteName = "group.com.ziro.goalz"
    public static let goalKey = "activeGoal"

    private let userDefaults: UserDefaults
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    public init(userDefaults: UserDefaults? = nil) {
        self.userDefaults = userDefaults ?? Self.makeSharedDefaults()
    }

    public func saveGoal(_ goal: Goal) {
        let data = try? encoder.encode(goal)
        userDefaults.set(data, forKey: Self.goalKey)
    }

    public func loadGoal() -> Goal? {
        guard let data = userDefaults.data(forKey: Self.goalKey) else {
            return nil
        }

        return try? decoder.decode(Goal.self, from: data)
    }

    public func clearGoal() {
        userDefaults.removeObject(forKey: Self.goalKey)
    }

    private static func makeSharedDefaults() -> UserDefaults {
        UserDefaults(suiteName: suiteName) ?? .standard
    }
}
