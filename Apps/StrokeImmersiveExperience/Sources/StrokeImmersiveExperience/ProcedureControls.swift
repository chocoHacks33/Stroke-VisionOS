#if canImport(ExperienceCore)
import ExperienceCore
#endif
import SwiftUI

struct StepTimelineView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    let compact: Bool

    private var sequence: [ExperienceProcedureStep] {
        ProcedureExperienceStateMachine.sequence(for: model.procedureState.selectedPathway)
    }

    private var currentIndex: Int {
        sequence.firstIndex(of: model.procedureState.currentStep) ?? 0
    }

    var body: some View {
        HStack(spacing: compact ? 6 : 9) {
            ForEach(Array(sequence.enumerated()), id: \.offset) { index, step in
                HStack(spacing: compact ? 6 : 9) {
                    Circle()
                        .fill(dotColor(index: index))
                        .frame(width: compact ? 8 : 10, height: compact ? 8 : 10)
                        .overlay {
                            if index == currentIndex {
                                Circle().stroke(.white.opacity(0.9), lineWidth: 2)
                                    .padding(-3)
                            }
                        }
                        .accessibilityLabel(stepLabel(step))
                        .accessibilityValue(index == currentIndex ? "Current step" : index < currentIndex ? "Completed" : "Upcoming")

                    if index < sequence.count - 1 {
                        Capsule()
                            .fill(index < currentIndex ? ExperienceTheme.mint.opacity(0.65) : .white.opacity(0.16))
                            .frame(width: compact ? 16 : 34, height: 2)
                    }
                }
            }

            if !compact {
                Text("\(currentIndex + 1) / \(max(1, sequence.count))")
                    .font(.caption.monospacedDigit().weight(.semibold))
                    .foregroundStyle(ExperienceTheme.quietText)
                    .padding(.leading, 6)
            }
        }
        .padding(.horizontal, compact ? 10 : 14)
        .padding(.vertical, compact ? 8 : 10)
        .background(.black.opacity(0.36), in: Capsule())
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Educational step timeline")
    }

    private func dotColor(index: Int) -> Color {
        if index == currentIndex { return ExperienceTheme.amber }
        if index < currentIndex { return ExperienceTheme.mint }
        return .white.opacity(0.2)
    }

    private func stepLabel(_ step: ExperienceProcedureStep) -> String {
        step.rawValue.replacingOccurrences(of: "_", with: " ").capitalized
    }
}

struct ProcedureTransportControls: View {
    @EnvironmentObject private var model: ExperienceShellModel
    var compact = true

    var body: some View {
        HStack(spacing: 7) {
            Button {
                model.previousStep()
            } label: {
                Label("Previous step", systemImage: "backward.end.fill")
            }
            .disabled(model.procedureProgress.current <= 1)

            Button {
                model.togglePause()
            } label: {
                Label(
                    model.procedureState.isPaused ? "Resume" : "Pause",
                    systemImage: model.procedureState.isPaused ? "play.fill" : "pause.fill"
                )
            }

            Button {
                model.replayCurrentStep()
            } label: {
                Label("Replay", systemImage: "arrow.counterclockwise")
            }

            Button {
                model.requestNextStep()
            } label: {
                Label("Next step", systemImage: "forward.end.fill")
            }
            .disabled(model.procedureProgress.current >= model.procedureProgress.total)
        }
        .labelStyle(.iconOnly)
        .buttonStyle(.bordered)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Lesson controls")
    }
}
