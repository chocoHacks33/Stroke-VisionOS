import SwiftUI

@main
struct StrokeImmersiveExperienceApp: App {
    @StateObject private var model = ExperienceShellModel()
    @StateObject private var feedback = InteractionFeedbackController()
    @State private var immersionStyle: ImmersionStyle = .full

    var body: some Scene {
        WindowGroup(id: ExperienceSpaceID.controlWindow) {
            ExperienceRootView()
                .environmentObject(model)
                .environmentObject(feedback)
                .preferredColorScheme(.dark)
                .task {
                    await runPackagedAssetProbeIfRequested()
                    runInteractionFeedbackProbeIfRequested()
                }
        }
        .defaultSize(width: 1_280, height: 820)

        ImmersiveSpace(id: ExperienceSpaceID.immersiveStage) {
            ImmersiveExperienceView()
                .environmentObject(model)
                .environmentObject(feedback)
        }
        .immersionStyle(selection: $immersionStyle, in: .full)
    }

    @MainActor
    private func runInteractionFeedbackProbeIfRequested() {
        guard ProcessInfo.processInfo.environment["STROKE_RUNTIME_FEEDBACK_PROBE"] == "1" else {
            return
        }
        let summary = feedback.runtimeResourceSummary
        let playbackStarted = feedback.emit(.confirmedStateChange, bypassCooldown: true)
        NSLog(
            "[StrokeFeedbackProbe] %@ earcons=%ld ambience_ready=%@ event=confirmed_state_change",
            playbackStarted && summary.earcons == 7 && summary.ambienceReady ? "PASS" : "FAIL",
            summary.earcons,
            summary.ambienceReady ? "true" : "false"
        )
    }

    @MainActor
    private func runPackagedAssetProbeIfRequested() async {
        let environment = ProcessInfo.processInfo.environment
        if let inspectionAssetID = environment["STROKE_RUNTIME_UI_PROBE_ID"],
           !inspectionAssetID.isEmpty {
            model.inspectAsset(id: inspectionAssetID)
        }
        guard let probeValue = environment["STROKE_RUNTIME_ASSET_PROBE_ID"],
              !probeValue.isEmpty,
              let resourceRoot = Bundle.main.resourceURL,
              let catalog = model.catalog else {
            return
        }

        let assetIDs = probeValue == "all"
            ? catalog.assets.map(\.assetID)
            : probeValue.split(separator: ",").map(String.init)
        var failures: [String] = []
        for assetID in assetIDs {
            do {
                let resolved = try catalog.resolve(assetID: assetID, tier: .full)
                _ = try await RuntimeRealityAssetLoader.loadEntity(
                    assetID: assetID,
                    sourcePath: resolved.sourcePath,
                    resourceRoot: resourceRoot
                )
                NSLog("[StrokeAssetProbe] PASS asset_id=%@", assetID)
            } catch {
                failures.append(assetID)
                NSLog("[StrokeAssetProbe] FAIL asset_id=%@ error=%@", assetID, error.localizedDescription)
            }
        }
        NSLog(
            "[StrokeAssetProbe] SUMMARY requested=%ld passed=%ld failed=%ld failed_ids=%@",
            assetIDs.count,
            assetIDs.count - failures.count,
            failures.count,
            failures.joined(separator: ",")
        )
    }
}

enum ExperienceSpaceID {
    static let controlWindow = "stroke-care-control-window"
    static let immersiveStage = "stroke-care-immersive-stage"
}
