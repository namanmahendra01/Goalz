import SwiftUI
import WidgetKit

struct LiveTrackerView: View {
    let goal: Goal
    let onReset: () -> Void
    @Environment(\.colorScheme) private var colorScheme
    @State private var showResetConfirmation = false

    var body: some View {
        TimelineView(.periodic(from: .now, by: 900)) { context in
            let snapshot = ProgressCalculator.makeSnapshot(for: goal, now: context.date)

            ZStack {
                GlassBackground(theme: goal.theme)

                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        HeroStatText(title: goal.title, value: "\(snapshot.remainingDays)")
                            .foregroundStyle(goal.theme.primaryTextColor(for: colorScheme))

                        Text(snapshot.remainingLabel)
                            .font(.headline.weight(.medium))
                            .foregroundStyle(goal.theme.secondaryTextColor(for: colorScheme))

                        GlassCard {
                            VStack(alignment: .leading, spacing: 18) {
                                Text("Progress")
                                    .font(.caption.weight(.semibold))
                                    .tracking(3)
                                    .foregroundStyle(goal.theme.secondaryTextColor(for: colorScheme))

                                ProgressGridView(snapshot: snapshot, theme: goal.theme)
                            }
                        }

                        Text("Updates daily.")
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(goal.theme.secondaryTextColor(for: colorScheme))

                        Button(role: .destructive) {
                            showResetConfirmation = true
                        } label: {
                            Text("Start Over")
                                .font(.headline.weight(.semibold))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 16)
                                .background(.white.opacity(0.08))
                                .foregroundStyle(goal.theme.primaryTextColor(for: colorScheme))
                                .clipShape(Capsule())
                        }
                    }
                    .padding(24)
                }
            }
        }
        .alert(GoalExperienceContent.resetWarningTitle, isPresented: $showResetConfirmation) {
            Button("Cancel", role: .cancel) {}
            Button("Start Over", role: .destructive) {
                onReset()
                WidgetCenter.shared.reloadAllTimelines()
            }
        } message: {
            Text(GoalExperienceContent.resetWarningMessage)
        }
    }
}

private struct ProgressGridView: View {
    let snapshot: GoalSnapshot
    let theme: GoalTheme
    @Environment(\.colorScheme) private var colorScheme

    var body: some View {
        let palette = theme.palette(for: colorScheme == .dark ? GoalTheme.Variant.dark : GoalTheme.Variant.light)
        let columns = Array(repeating: GridItem(.flexible(), spacing: 10), count: 5)

        LazyVGrid(columns: columns, spacing: 10) {
            ForEach(0..<snapshot.totalDays, id: \.self) { index in
                Circle()
                    .fill(index < snapshot.elapsedDays ? Color(hex: palette.completedHex) : Color(hex: palette.remainingHex).opacity(0.55))
                    .frame(height: 20)
                    .overlay {
                        Circle()
                            .stroke(index < snapshot.elapsedDays ? Color(hex: palette.completedHex).opacity(0.18) : Color.clear, lineWidth: 1)
                    }
            }
        }
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
