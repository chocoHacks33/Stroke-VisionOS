import SwiftUI

@main
struct StrokeImmersiveExperienceApp: App {
    @StateObject private var model = ExperienceShellModel()
    @State private var immersionStyle: ImmersionStyle = .full

    var body: some Scene {
        WindowGroup(id: ExperienceSpaceID.controlWindow) {
            ExperienceRootView()
                .environmentObject(model)
                .preferredColorScheme(.dark)
        }
        .defaultSize(width: 1_280, height: 820)

        ImmersiveSpace(id: ExperienceSpaceID.immersiveStage) {
            ImmersiveExperienceView()
                .environmentObject(model)
        }
        .immersionStyle(selection: $immersionStyle, in: .full)
    }
}

enum ExperienceSpaceID {
    static let controlWindow = "stroke-care-control-window"
    static let immersiveStage = "stroke-care-immersive-stage"
}
