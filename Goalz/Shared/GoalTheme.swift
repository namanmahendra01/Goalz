import Foundation

public enum GoalTheme: String, Codable, Equatable, Sendable {
    case sunset
    case electric
    case aurora
    case monochrome
    case ocean
    case violet
    case ember
    case forest
    case neonLime
    case roseGold
    case iceBlue

    public enum Variant: String, Codable, CaseIterable, Equatable, Sendable {
        case light
        case dark
    }

    public struct Palette: Equatable, Sendable {
        public let backgroundHex: String
        public let completedHex: String
        public let remainingHex: String

        public init(backgroundHex: String, completedHex: String, remainingHex: String) {
            self.backgroundHex = backgroundHex
            self.completedHex = completedHex
            self.remainingHex = remainingHex
        }
    }

    public static var allCases: [GoalTheme] {
        [
            .sunset,
            .ocean,
            .aurora,
            .monochrome,
            .violet,
            .ember,
            .forest,
            .neonLime,
            .roseGold,
            .iceBlue,
        ]
    }

    public var name: String {
        switch self {
        case .sunset:
            "Sunset Red"
        case .electric:
            "Ocean"
        case .aurora:
            "Aurora Mint"
        case .monochrome:
            "Soft Mono"
        case .ocean:
            "Ocean"
        case .violet:
            "Violet"
        case .ember:
            "Ember"
        case .forest:
            "Forest"
        case .neonLime:
            "Neon Lime"
        case .roseGold:
            "Rose Gold"
        case .iceBlue:
            "Ice Blue"
        }
    }

    public var accentHex: String {
        switch self {
        case .sunset:
            "#FF5A4F"
        case .electric:
            "#4D8DFF"
        case .aurora:
            "#41D6B7"
        case .monochrome:
            "#F2F2F7"
        case .ocean:
            "#4D8DFF"
        case .violet:
            "#8E68FF"
        case .ember:
            "#FF7A45"
        case .forest:
            "#2F9B6A"
        case .neonLime:
            "#B7FF3C"
        case .roseGold:
            "#D8929C"
        case .iceBlue:
            "#72C7FF"
        }
    }

    public func palette(for variant: Variant) -> Palette {
        switch self {
        case .sunset:
            switch variant {
            case .light:
                Palette(backgroundHex: "#FFF5EF", completedHex: "#FF6B5E", remainingHex: "#D8B8B4")
            case .dark:
                Palette(backgroundHex: "#23161B", completedHex: "#FF6B5E", remainingHex: "#7E8B97")
            }
        case .electric:
            switch variant {
            case .light:
                Palette(backgroundHex: "#EEF6FF", completedHex: "#4D8DFF", remainingHex: "#BCD0E8")
            case .dark:
                Palette(backgroundHex: "#101D31", completedHex: "#69A8FF", remainingHex: "#627993")
            }
        case .aurora:
            switch variant {
            case .light:
                Palette(backgroundHex: "#EFFCF7", completedHex: "#41D6B7", remainingHex: "#B7DCD5")
            case .dark:
                Palette(backgroundHex: "#12231F", completedHex: "#52E3C3", remainingHex: "#68857F")
            }
        case .monochrome:
            switch variant {
            case .light:
                Palette(backgroundHex: "#F7F8FA", completedHex: "#2C3138", remainingHex: "#C4CAD1")
            case .dark:
                Palette(backgroundHex: "#16181D", completedHex: "#F7F8FA", remainingHex: "#6D737C")
            }
        case .ocean:
            switch variant {
            case .light:
                Palette(backgroundHex: "#EEF6FF", completedHex: "#4D8DFF", remainingHex: "#BCD0E8")
            case .dark:
                Palette(backgroundHex: "#101D31", completedHex: "#69A8FF", remainingHex: "#627993")
            }
        case .violet:
            switch variant {
            case .light:
                Palette(backgroundHex: "#F5F0FF", completedHex: "#8E68FF", remainingHex: "#C9BDEB")
            case .dark:
                Palette(backgroundHex: "#1D1630", completedHex: "#A884FF", remainingHex: "#746A93")
            }
        case .ember:
            switch variant {
            case .light:
                Palette(backgroundHex: "#FFF4EC", completedHex: "#FF7A45", remainingHex: "#D9BBA9")
            case .dark:
                Palette(backgroundHex: "#261914", completedHex: "#FF8C5F", remainingHex: "#866D61")
            }
        case .forest:
            switch variant {
            case .light:
                Palette(backgroundHex: "#EEF8F1", completedHex: "#2F9B6A", remainingHex: "#B7CFBF")
            case .dark:
                Palette(backgroundHex: "#14231A", completedHex: "#4DBA86", remainingHex: "#667E70")
            }
        case .neonLime:
            switch variant {
            case .light:
                Palette(backgroundHex: "#FAFFE9", completedHex: "#9FEC21", remainingHex: "#C9D7A5")
            case .dark:
                Palette(backgroundHex: "#1B2012", completedHex: "#B7FF3C", remainingHex: "#798365")
            }
        case .roseGold:
            switch variant {
            case .light:
                Palette(backgroundHex: "#FFF4F6", completedHex: "#D8929C", remainingHex: "#D9BCC1")
            case .dark:
                Palette(backgroundHex: "#24191D", completedHex: "#E0A2AB", remainingHex: "#876F74")
            }
        case .iceBlue:
            switch variant {
            case .light:
                Palette(backgroundHex: "#F1FAFF", completedHex: "#72C7FF", remainingHex: "#A9BED0")
            case .dark:
                Palette(backgroundHex: "#14212A", completedHex: "#8AD4FF", remainingHex: "#6B818F")
            }
        }
    }

    public var widgetBackgroundHex: String { palette(for: .dark).backgroundHex }
    public var widgetCompletedHex: String { palette(for: .dark).completedHex }
    public var widgetRemainingHex: String { palette(for: .dark).remainingHex }

    public func primaryTextHex(for variant: Variant) -> String {
        switch variant {
        case .light:
            "#111418"
        case .dark:
            "#F8FAFC"
        }
    }

    public func secondaryTextHex(for variant: Variant) -> String {
        switch variant {
        case .light:
            "#5B6470"
        case .dark:
            "#A7B4C4"
        }
    }
}

public enum GoalWidgetStyle: String, Codable, CaseIterable, Equatable, Sendable {
    case ring
    case filled
    case minimal

    public var name: String {
        switch self {
        case .ring:
            "Ring Focus"
        case .filled:
            "Filled Grid"
        case .minimal:
            "Minimal Counter"
        }
    }
}
