import SwiftUI
import WidgetKit

struct GoalzWidgetEntry: TimelineEntry {
    let date: Date
    let goal: Goal?
    let snapshot: GoalSnapshot?
}

struct GoalzWidgetProvider: TimelineProvider {
    func placeholder(in context: Context) -> GoalzWidgetEntry {
        GoalzWidgetEntry(date: .now, goal: demoGoal, snapshot: ProgressCalculator.makeSnapshot(for: demoGoal))
    }

    func getSnapshot(in context: Context, completion: @escaping (GoalzWidgetEntry) -> Void) {
        let goal = GoalStore().loadGoal() ?? demoGoal
        completion(GoalzWidgetEntry(date: .now, goal: goal, snapshot: ProgressCalculator.makeSnapshot(for: goal)))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<GoalzWidgetEntry>) -> Void) {
        guard let goal = GoalStore().loadGoal() else {
            let entry = GoalzWidgetEntry(date: .now, goal: nil, snapshot: nil)
            completion(Timeline(entries: [entry], policy: .never))
            return
        }

        let dates = ProgressCalculator.makeTimelineDates(for: goal, now: .now)
        let entries = dates.map { date in
            GoalzWidgetEntry(
                date: date,
                goal: goal,
                snapshot: ProgressCalculator.makeSnapshot(for: goal, now: date)
            )
        }

        let reloadPolicy: TimelineReloadPolicy = entries.last?.snapshot?.isComplete == true ? .never : .atEnd
        completion(Timeline(entries: entries, policy: reloadPolicy))
    }

    private var demoGoal: Goal {
        Goal(
            title: "Ship Goalz",
            totalDays: 30,
            startDate: .now.addingTimeInterval(-(60 * 60 * 24 * 4)),
            theme: .sunset,
            widgetStyle: .ring
        )
    }
}

struct GoalzWidget: Widget {
    let kind = "GoalzWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: GoalzWidgetProvider()) { entry in
            GoalzWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Goalz")
        .description("Keep one goal visible on your Home Screen or Lock Screen.")
        .supportedFamilies([.systemSmall, .systemMedium, .accessoryCircular, .accessoryRectangular])
        .contentMarginsDisabled()
    }
}

private struct GoalzWidgetEntryView: View {
    @Environment(\.widgetFamily) private var family
    @Environment(\.colorScheme) private var colorScheme
    let entry: GoalzWidgetEntry

    var body: some View {
        if let goal = entry.goal, let snapshot = entry.snapshot {
            switch family {
            case .systemSmall:
                homeSmall(goal: goal, snapshot: snapshot)
            case .systemMedium:
                homeMedium(goal: goal, snapshot: snapshot)
            case .accessoryCircular:
                lockCircular(goal: goal, snapshot: snapshot)
            case .accessoryRectangular:
                lockRectangular(goal: goal, snapshot: snapshot)
            default:
                homeSmall(goal: goal, snapshot: snapshot)
            }
        } else {
            switch family {
            case .accessoryCircular:
                emptyCircularWidget
            case .accessoryRectangular:
                emptyRectangularWidget
            default:
                emptyHomeWidget
            }
        }
    }

    private func homeSmall(goal: Goal, snapshot: GoalSnapshot) -> some View {
        GeometryReader { geometry in
            dotMatrix(
                goal: goal,
                snapshot: snapshot,
                canvasSize: geometry.size,
                outerPadding: 10
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .containerBackground(for: .widget) {
            glassBackground(goal.theme)
        }
    }

    private func homeMedium(goal: Goal, snapshot: GoalSnapshot) -> some View {
        GeometryReader { geometry in
            dotMatrix(
                goal: goal,
                snapshot: snapshot,
                canvasSize: geometry.size,
                outerPadding: 12
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .containerBackground(for: .widget) {
            glassBackground(goal.theme)
        }
    }

    private func lockCircular(goal: Goal, snapshot: GoalSnapshot) -> some View {
        let palette = goal.theme.palette(for: widgetVariant)

        return ZStack {
            Circle().fill(Color(hex: palette.completedHex).opacity(0.16))
            Circle().stroke(Color(hex: palette.remainingHex).opacity(0.22), lineWidth: 8)
            Circle()
                .trim(from: 0, to: snapshot.progress)
                .stroke(Color(hex: palette.completedHex), style: StrokeStyle(lineWidth: 8, lineCap: .round))
                .rotationEffect(.degrees(-90))
            Text("\(snapshot.remainingDays)")
                .font(.system(size: 18, weight: .bold, design: .rounded))
                .foregroundStyle(.white)
        }
        .containerBackground(for: .widget) {
            Color.clear
        }
    }

    private func lockRectangular(goal: Goal, snapshot: GoalSnapshot) -> some View {
        HStack(spacing: 8) {
            Text("\(snapshot.remainingDays)")
                .font(.system(size: 22, weight: .bold, design: .rounded))
                .foregroundStyle(.primary)

            VStack(alignment: .leading, spacing: 1) {
                Text(goal.title)
                    .font(.caption.bold())
                    .lineLimit(1)
                Text("Day \(snapshot.elapsedDays)")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
        .containerBackground(for: .widget) {
            Color.clear
        }
    }

    private var emptyHomeWidget: some View {
        let palette = GoalTheme.sunset.palette(for: widgetVariant)

        return RoundedRectangle(cornerRadius: 26, style: .continuous)
            .fill(.clear)
            .overlay {
                VStack(spacing: 12) {
                    Image(systemName: "plus.circle.fill")
                        .font(.system(size: 28, weight: .semibold))
                        .foregroundStyle(Color(hex: palette.completedHex))

                    HStack(spacing: 6) {
                        ForEach(0..<8, id: \.self) { _ in
                            Circle()
                                .fill(Color(hex: palette.remainingHex))
                                .frame(width: 8, height: 8)
                        }
                    }
                }
            }
        .containerBackground(for: .widget) {
            glassBackground(.sunset)
        }
    }

    private var emptyCircularWidget: some View {
        let palette = GoalTheme.sunset.palette(for: widgetVariant)

        return ZStack {
            Circle().fill(Color(hex: palette.completedHex).opacity(0.16))
            Image(systemName: "plus")
                .font(.system(size: 16, weight: .bold))
                .foregroundStyle(.white)
        }
        .containerBackground(for: .widget) {
            Color.clear
        }
    }

    private var emptyRectangularWidget: some View {
        let palette = GoalTheme.sunset.palette(for: widgetVariant)

        return HStack(spacing: 8) {
            Image(systemName: "plus.circle.fill")
                .foregroundStyle(Color(hex: palette.completedHex))
            Text("Add in Goalz")
                .font(.caption.bold())
        }
        .containerBackground(for: .widget) {
            Color.clear
        }
    }

    private func dotMatrix(goal: Goal, snapshot: GoalSnapshot, canvasSize: CGSize, outerPadding: CGFloat) -> some View {
        let palette = goal.theme.palette(for: widgetVariant)
        let layout = dotLayout(for: snapshot.totalDays, in: canvasSize, outerPadding: outerPadding)
        let columns = Array(repeating: GridItem(.fixed(layout.dotSize), spacing: layout.spacing), count: layout.columns)
        let dotStates = ProgressCalculator.makeDotStates(for: snapshot)

        return LazyVGrid(columns: columns, alignment: .center, spacing: layout.spacing) {
            ForEach(Array(dotStates.enumerated()), id: \.offset) { index, isFilled in
                Circle()
                    .fill(isFilled ? Color(hex: palette.completedHex) : Color(hex: palette.remainingHex))
                    .frame(width: layout.dotSize, height: layout.dotSize)
            }
        }
        .padding(layout.innerPadding)
        .padding(outerPadding)
    }

    private func dotLayout(for totalDays: Int, in size: CGSize, outerPadding: CGFloat) -> (columns: Int, dotSize: CGFloat, spacing: CGFloat, innerPadding: CGFloat) {
        let usableWidth = max(40, size.width - (outerPadding * 2))
        let usableHeight = max(40, size.height - (outerPadding * 2))
        let aspect = usableWidth / usableHeight
        let columns = max(5, Int(ceil(sqrt(Double(totalDays) * Double(aspect)))))
        let rows = max(1, Int(ceil(Double(totalDays) / Double(columns))))
        let innerPadding: CGFloat = min(size.width, size.height) < 170 ? 12 : 14
        let matrixWidth = usableWidth - (innerPadding * 2)
        let matrixHeight = usableHeight - (innerPadding * 2)
        let spacing = max(2, min(4, min(matrixWidth / CGFloat(max(columns, 1)), matrixHeight / CGFloat(max(rows, 1))) * 0.22))
        let dotWidth = (matrixWidth - spacing * CGFloat(columns - 1)) / CGFloat(columns)
        let dotHeight = (matrixHeight - spacing * CGFloat(rows - 1)) / CGFloat(rows)
        let dotSize = max(3, min(dotWidth, dotHeight))

        return (columns, dotSize, spacing, innerPadding)
    }

    private func glassBackground(_ theme: GoalTheme) -> some View {
        let palette = theme.palette(for: widgetVariant)

        return ZStack {
            RoundedRectangle(cornerRadius: 30, style: .continuous)
                .fill(.ultraThinMaterial)

            Color(hex: palette.backgroundHex).opacity(0.82)

            Circle()
                .fill(Color(hex: palette.completedHex).opacity(0.12))
                .blur(radius: 42)
                .offset(x: -34, y: 26)

            RoundedRectangle(cornerRadius: 30, style: .continuous)
                .stroke(.white.opacity(0.14), lineWidth: 1)
        }
    }

    private var widgetVariant: GoalTheme.Variant {
        colorScheme == .dark ? .dark : .light
    }
}

private extension Color {
    init(hex: String) {
        let sanitized = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: sanitized).scanHexInt64(&int)

        let red = Double((int >> 16) & 0xFF) / 255
        let green = Double((int >> 8) & 0xFF) / 255
        let blue = Double(int & 0xFF) / 255

        self.init(red: red, green: green, blue: blue)
    }
}
