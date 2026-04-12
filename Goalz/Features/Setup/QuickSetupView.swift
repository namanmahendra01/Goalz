import SwiftUI

struct QuickSetupView: View {
    @State private var title = ""
    @State private var totalDays = 30
    @State private var dayInput = "30"
    @State private var selectedTheme: GoalTheme = .sunset
    @FocusState private var isDayInputFocused: Bool
    @Environment(\.colorScheme) private var colorScheme

    let onSave: (Goal) -> Void

    var body: some View {
        ZStack {
            GlassBackground(theme: selectedTheme)

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Goalz")
                            .font(.system(size: 38, weight: .bold, design: .rounded))
                            .foregroundStyle(selectedTheme.primaryTextColor(for: colorScheme))

                        Text("Name it. Pick days. Save.")
                            .font(.headline)
                            .foregroundStyle(selectedTheme.secondaryTextColor(for: colorScheme))
                    }

                    GlassCard {
                        VStack(alignment: .leading, spacing: 16) {
                            TextField("Run 5km", text: $title)
                                .textInputAutocapitalization(.sentences)
                                .padding(.horizontal, 18)
                                .padding(.vertical, 16)
                                .background(.white.opacity(0.08))
                                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                                .font(.title3.weight(.semibold))
                                .foregroundStyle(selectedTheme.primaryTextColor(for: colorScheme))

                            label("Days")
                            HStack(spacing: 12) {
                                TextField("30", text: $dayInput)
                                    .keyboardType(.numberPad)
                                    .focused($isDayInputFocused)
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 12)
                                    .background(.white.opacity(0.08))
                                    .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                                    .font(.title2.bold())
                                    .foregroundStyle(selectedTheme.primaryTextColor(for: colorScheme))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .onChange(of: dayInput) { _, newValue in
                                        totalDays = GoalDayInput.normalizedDayCount(from: newValue, fallback: totalDays)
                                    }
                                    .onSubmit {
                                        dayInput = "\(GoalDayInput.normalizedDayCount(from: dayInput, fallback: totalDays))"
                                        totalDays = GoalDayInput.normalizedDayCount(from: dayInput, fallback: totalDays)
                                    }

                                Stepper("", value: $totalDays, in: 1...365)
                                    .labelsHidden()
                                    .tint(selectedTheme.accentColor)
                            }
                            .onChange(of: totalDays) { _, newValue in
                                dayInput = "\(newValue)"
                            }
                            .onChange(of: isDayInputFocused) { _, focused in
                                if !focused {
                                    let normalized = GoalDayInput.normalizedDayCount(from: dayInput, fallback: totalDays)
                                    totalDays = normalized
                                    dayInput = "\(normalized)"
                                }
                            }

                            label("Theme")
                            LazyVGrid(columns: [GridItem(.adaptive(minimum: 90), spacing: 12)], spacing: 12) {
                                ForEach(GoalTheme.allCases, id: \.self) { theme in
                                    Button {
                                        selectedTheme = theme
                                    } label: {
                                        ThemeSwatchCard(theme: theme, isSelected: theme == selectedTheme)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }

                    WidgetPreviewCard(
                        goalTitle: previewTitle,
                        totalDays: totalDays,
                        theme: selectedTheme
                    )

                    Button {
                        onSave(
                            Goal(
                                title: previewTitle,
                                totalDays: totalDays,
                                startDate: .now,
                                theme: selectedTheme,
                                widgetStyle: .filled
                            )
                        )
                    } label: {
                        Text("Save")
                            .font(.headline.weight(.bold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 18)
                            .background(selectedTheme.accentColor)
                            .foregroundStyle(.white)
                            .clipShape(Capsule())
                            .shadow(color: selectedTheme.accentColor.opacity(0.5), radius: 24, y: 16)
                    }
                    .padding(.bottom, 12)
                }
                .padding(24)
            }
        }
    }

    private var previewTitle: String {
        let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? "Ship Goalz" : trimmed
    }

    private func label(_ text: String) -> some View {
        Text(text.uppercased())
            .font(.caption.weight(.semibold))
            .tracking(3)
            .foregroundStyle(selectedTheme.secondaryTextColor(for: colorScheme))
    }
}

private struct WidgetPreviewCard: View {
    let goalTitle: String
    let totalDays: Int
    let theme: GoalTheme
    @Environment(\.colorScheme) private var colorScheme

    var body: some View {
        GlassCard {
            VStack(alignment: .leading, spacing: 14) {
                Text("Preview")
                    .font(.caption.weight(.semibold))
                    .tracking(3)
                    .foregroundStyle(theme.secondaryTextColor(for: colorScheme))

                HStack(alignment: .center, spacing: 16) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(goalTitle)
                            .font(.headline.bold())
                            .foregroundStyle(theme.primaryTextColor(for: colorScheme))
                            .lineLimit(1)

                        Text("\(totalDays) days")
                            .foregroundStyle(theme.secondaryTextColor(for: colorScheme))
                    }

                    Spacer()

                    Text("\(totalDays)")
                        .font(.system(size: 34, weight: .bold, design: .rounded))
                        .foregroundStyle(theme.primaryTextColor(for: colorScheme))
                }

                HStack(spacing: 6) {
                    ForEach(0..<min(totalDays, 10), id: \.self) { index in
                        Circle()
                            .fill(index < 3 ? theme.accentColor : theme.secondaryColor)
                            .frame(width: 12, height: 12)
                    }
                }

                HStack(spacing: 10) {
                    paletteMiniCard(title: "Light", palette: theme.palette(for: GoalTheme.Variant.light))
                    paletteMiniCard(title: "Dark", palette: theme.palette(for: GoalTheme.Variant.dark))
                }
            }
        }
    }

    private func paletteMiniCard(title: String, palette: GoalTheme.Palette) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(theme.secondaryTextColor(for: colorScheme))

            HStack(spacing: 4) {
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .fill(Color(hex: palette.backgroundHex))
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .fill(Color(hex: palette.completedHex))
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .fill(Color(hex: palette.remainingHex))
            }
            .frame(height: 18)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct ThemeSwatchCard: View {
    let theme: GoalTheme
    let isSelected: Bool
    @Environment(\.colorScheme) private var colorScheme

    var body: some View {
        let palette = theme.palette(for: GoalTheme.Variant.light)

        return VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Circle()
                    .fill(Color(hex: palette.backgroundHex))
                Circle()
                    .fill(Color(hex: palette.completedHex))
                Circle()
                    .fill(Color(hex: palette.remainingHex))
            }
            .frame(height: 16)

            Text(theme.name)
                .font(.caption.weight(.semibold))
                .foregroundStyle(theme.primaryTextColor(for: colorScheme))
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(isSelected ? .white.opacity(0.16) : .white.opacity(0.08))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(isSelected ? .white.opacity(0.35) : .white.opacity(0.08), lineWidth: 1)
        }
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
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
