import SwiftUI

extension GoalTheme {
    func palette(for colorScheme: ColorScheme) -> GoalTheme.Palette {
        palette(for: colorScheme == .dark ? GoalTheme.Variant.dark : GoalTheme.Variant.light)
    }

    func primaryTextColor(for colorScheme: ColorScheme) -> Color {
        Color(hex: primaryTextHex(for: colorScheme == .dark ? GoalTheme.Variant.dark : GoalTheme.Variant.light))
    }

    func secondaryTextColor(for colorScheme: ColorScheme) -> Color {
        Color(hex: secondaryTextHex(for: colorScheme == .dark ? GoalTheme.Variant.dark : GoalTheme.Variant.light))
    }

    var accentColor: Color {
        Color(hex: widgetCompletedHex)
    }

    var secondaryColor: Color {
        Color(hex: widgetRemainingHex)
    }

    var backgroundGradient: LinearGradient {
        LinearGradient(
            colors: [
                Color(hex: widgetBackgroundHex),
                accentColor.opacity(0.35),
                Color.black.opacity(0.92),
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    var displayName: String { name }
}

struct GlassBackground: View {
    var theme: GoalTheme
    @Environment(\.colorScheme) private var colorScheme

    var body: some View {
        let palette = theme.palette(for: colorScheme)

        ZStack {
            LinearGradient(
                colors: [
                    Color(hex: palette.backgroundHex),
                    Color(hex: palette.completedHex).opacity(0.35),
                    Color.black.opacity(colorScheme == .dark ? 0.92 : 0.2),
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )

            Circle()
                .fill(Color(hex: palette.completedHex).opacity(0.32))
                .blur(radius: 120)
                .frame(width: 280, height: 280)
                .offset(x: 120, y: -220)

            Circle()
                .fill(Color(hex: palette.remainingHex).opacity(0.24))
                .blur(radius: 160)
                .frame(width: 320, height: 320)
                .offset(x: -140, y: 260)

            LinearGradient(
                colors: [.white.opacity(0.12), .clear, .black.opacity(0.16)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
        .ignoresSafeArea()
    }
}

struct GlassCard<Content: View>: View {
    var cornerRadius: CGFloat = 30
    @ViewBuilder var content: Content

    var body: some View {
        content
            .padding(20)
            .background {
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .fill(.ultraThinMaterial)
                    .overlay {
                        RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                            .strokeBorder(.white.opacity(0.18), lineWidth: 1)
                    }
                    .shadow(color: .black.opacity(0.25), radius: 30, y: 20)
            }
    }
}

struct HeroStatText: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title.uppercased())
                .font(.caption.weight(.semibold))
                .tracking(3)
                .foregroundStyle(.secondary)

            Text(value)
                .font(.system(size: 46, weight: .bold, design: .rounded))
                .foregroundStyle(.primary)
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
