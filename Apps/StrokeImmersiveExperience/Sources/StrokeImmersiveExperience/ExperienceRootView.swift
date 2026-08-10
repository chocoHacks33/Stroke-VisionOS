import SwiftUI

struct ExperienceRootView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

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
