import SwiftUI

struct ExperienceRootView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @EnvironmentObject private var feedback: InteractionFeedbackController
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        ZStack {
            ExperienceTheme.canvas.ignoresSafeArea()
            ambientBackdrop

            switch model.screen {
            case .landing:
                LandingView()
                    .transition(.opacity.combined(with: .scale(scale: 0.98)))
            case .cases:
                CaseLibraryView()
                    .transition(.opacity.combined(with: .move(edge: .trailing)))
            case .explore:
                ExploreShellView()
                    .transition(.opacity)
            case .library:
                AssetLibraryShellView()
                    .transition(.opacity.combined(with: .move(edge: .bottom)))
            }
        }
        .animation(reduceMotion ? nil : .easeInOut(duration: 0.28), value: model.screen)
        .frame(minWidth: 1_080, minHeight: 700)
        .onChange(of: model.screen) { oldValue, newValue in
            guard oldValue != newValue else { return }
            feedback.emit(newValue == .landing ? .restoreComplete : .majorViewTransition)
        }
        .onChange(of: model.detailTier) { oldValue, newValue in
            guard oldValue != newValue else { return }
            // The continuous slider remains quiet; one cue is emitted only when
            // it crosses a semantic visual-detail tier boundary.
            feedback.emit(.controlCommit)
        }
        .onChange(of: model.procedureState.currentStep) { oldValue, newValue in
            guard oldValue != newValue else { return }
            let steps = ProcedureExperienceStateMachine.sequence(
                for: model.procedureState.selectedPathway
            )
            let oldIndex = steps.firstIndex(of: oldValue) ?? 0
            let newIndex = steps.firstIndex(of: newValue) ?? oldIndex
            feedback.emit(newIndex < oldIndex ? .navigateBack : .confirmedStateChange)
        }
        .onChange(of: model.pendingTransitionTitle) { _, newValue in
            if newValue != nil { feedback.emit(.actionRequiresAttention) }
        }
        .onChange(of: model.runtimeError) { _, newValue in
            if newValue != nil { feedback.emit(.actionRequiresAttention) }
        }
        .onChange(of: model.replayToken) { oldValue, newValue in
            if oldValue != newValue { feedback.emit(.controlCommit) }
        }
        .onChange(of: model.isImmersiveSpaceOpen) { oldValue, newValue in
            if oldValue != newValue { feedback.emit(.majorViewTransition) }
        }
        .onChange(of: scenePhase) { _, newValue in
            if newValue == .active {
                feedback.applicationDidBecomeActive()
            } else {
                feedback.applicationWillResignActive()
            }
        }
    }

    private var ambientBackdrop: some View {
        ZStack {
            RadialGradient(
                colors: [ExperienceTheme.glow.opacity(0.15), .clear],
                center: .center,
                startRadius: 20,
                endRadius: 560
            )
            .offset(x: 90, y: 40)

            LinearGradient(
                colors: [.black.opacity(0.1), .black.opacity(0.82)],
                startPoint: .top,
                endPoint: .bottom
            )
        }
        .allowsHitTesting(false)
        .ignoresSafeArea()
    }
}
