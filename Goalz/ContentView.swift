//
//  ContentView.swift
//  Goalz
//
//  Created by Naman Mahendra on 11/04/26.
//

import SwiftUI
import WidgetKit

struct ContentView: View {
    @State private var activeGoal: Goal?
    @State private var showCreationToast = false
    @State private var showWidgetGuide = false

    private let store = GoalStore()

    var body: some View {
        ZStack(alignment: .top) {
            Group {
                if let goal = activeGoal {
                    LiveTrackerView(goal: goal) {
                        store.clearGoal()
                        activeGoal = nil
                    }
                } else {
                    QuickSetupView { goal in
                        store.saveGoal(goal)
                        activeGoal = goal
                        WidgetCenter.shared.reloadAllTimelines()
                        showCreationToast = true
                        showWidgetGuide = true
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2.2) {
                            showCreationToast = false
                        }
                    }
                }
            }

            if showCreationToast {
                ToastBanner(message: GoalExperienceContent.successMessage)
                    .padding(.top, 18)
                    .transition(.move(edge: .top).combined(with: .opacity))
                    .zIndex(1)
            }
        }
        .animation(.easeInOut(duration: 0.24), value: showCreationToast)
        .sheet(isPresented: $showWidgetGuide) {
            if let goal = activeGoal {
                WidgetGuideSheet(goal: goal)
            }
        }
        .onAppear {
            activeGoal = store.loadGoal()
        }
    }
}

private struct ToastBanner: View {
    let message: String

    var body: some View {
        Text(message)
            .font(.subheadline.weight(.semibold))
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(.ultraThinMaterial)
            .clipShape(Capsule())
            .overlay {
                Capsule()
                    .stroke(.white.opacity(0.12), lineWidth: 1)
            }
    }
}

private struct WidgetGuideSheet: View {
    @Environment(\.dismiss) private var dismiss
    let goal: Goal

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Add your widget")
                            .font(.system(size: 30, weight: .bold, design: .rounded))

                        Text("“\(GoalExperienceContent.quote(for: goal))”")
                            .font(.headline)
                            .foregroundStyle(.secondary)
                    }

                    guideCard(title: "Home Screen", steps: GoalExperienceContent.homeScreenSteps)
                    guideCard(title: "Lock Screen", steps: GoalExperienceContent.lockScreenSteps)

                    Button("Done") {
                        dismiss()
                    }
                    .font(.headline.weight(.bold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(.primary)
                    .foregroundStyle(.background)
                    .clipShape(Capsule())
                }
            }
            .padding(24)
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    private func guideCard(title: String, steps: [String]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline.bold())

            ForEach(Array(steps.enumerated()), id: \.offset) { index, step in
                HStack(alignment: .top, spacing: 10) {
                    Text("\(index + 1).")
                        .font(.subheadline.bold())
                        .foregroundStyle(.secondary)
                    Text(step)
                        .font(.subheadline)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

}

#Preview("Setup") {
    ContentView()
}

#Preview("Tracker") {
    LiveTrackerView(
        goal: Goal(
            title: "Ship Goalz",
            totalDays: 30,
            startDate: .now.addingTimeInterval(-(60 * 60 * 24 * 4)),
            theme: .sunset,
            widgetStyle: .ring
        ),
        onReset: {}
    )
}
