import RealityKit
import SwiftUI
#if canImport(ExperienceCore)
import ExperienceCore
#endif

struct WindowModelStage: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @State private var yaw = -9.0
    @State private var pitch = -3.0
    @State private var zoom = 1.0
    @GestureState private var dragOffset = CGSize.zero

    private var modelURL: URL? {
        Bundle.main.resourceURL?.appending(path: model.selectedAssetPath)
    }

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(.black.opacity(0.72))
                .overlay {
                    RadialGradient(
                        colors: [ExperienceTheme.glow.opacity(0.16), .clear],
                        center: .center,
                        startRadius: 15,
                        endRadius: 350
                    )
                }

            if let recipe = model.activeRecipe {
                WindowRecipeRealityView(recipe: recipe)
                    .environmentObject(model)
                    .id(recipe.recipe.id.rawValue)
                    .scaleEffect(zoom)
                    .rotation3DEffect(
                        .degrees(pitch - Double(dragOffset.height) * 0.12),
                        axis: (x: 1, y: 0, z: 0)
                    )
                    .rotation3DEffect(
                        .degrees(yaw + Double(dragOffset.width) * 0.16),
                        axis: (x: 0, y: 1, z: 0)
                    )
                    .gesture(modelDragGesture)
            } else if let modelURL, FileManager.default.fileExists(atPath: modelURL.path()) {
                Model3D(url: modelURL) { phase in
                    switch phase {
                    case .empty:
                        ProgressView("Loading selected teaching set…")
                            .controlSize(.large)
                    case .success(let entityView):
                        entityView
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .padding(38)
                    case .failure(let error):
                        loadFailure(error.localizedDescription)
                    @unknown default:
                        loadFailure("Unknown model state")
                    }
                }
                .id(model.selectedAssetID)
                .saturation(model.activePresentation?.saturationMultiplier ?? 1)
                .opacity(windowModelOpacity)
                .scaleEffect(zoom)
                .rotation3DEffect(
                    .degrees(pitch - Double(dragOffset.height) * 0.12),
                    axis: (x: 1, y: 0, z: 0)
                )
                .rotation3DEffect(
                    .degrees(yaw + Double(dragOffset.width) * 0.16),
                    axis: (x: 0, y: 1, z: 0)
                )
                .gesture(modelDragGesture)
            } else {
                loadFailure("The selected resource is not in this development bundle.")
            }

            VStack {
                HStack {
                    Label("Conceptual · generic · not to clinical scale", systemImage: "exclamationmark.magnifyingglass")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(ExperienceTheme.amber)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(.black.opacity(0.72), in: Capsule())
                    Spacer()
                    Label(model.detailTierTitle, systemImage: "circle.hexagongrid")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(ExperienceTheme.mint)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(.black.opacity(0.72), in: Capsule())
                }
                Spacer()
                controls
            }
            .padding(18)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(ExperienceTheme.mint.opacity(0.16), lineWidth: 1)
        }
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private var modelDragGesture: some Gesture {
        DragGesture(minimumDistance: 1)
            .updating($dragOffset) { value, state, _ in state = value.translation }
            .onEnded { value in
                yaw += Double(value.translation.width) * 0.16
                pitch = min(65, max(-65, pitch - Double(value.translation.height) * 0.12))
            }
    }

    private var windowModelOpacity: Double {
        guard let presentation = model.activePresentation else { return 1 }
        return max(0.68, min(1, 0.62 + presentation.secondaryDetailVisibilityRatio * 0.38))
    }

    private var controls: some View {
        HStack(spacing: 12) {
            Button { yaw -= 15 } label: { Image(systemName: "rotate.left") }
            Button { zoom = max(0.62, zoom - 0.12) } label: { Image(systemName: "minus.magnifyingglass") }
            Button {
                yaw = -9
                pitch = -3
                zoom = 1
            } label: { Image(systemName: "viewfinder") }
            Button { zoom = min(2.2, zoom + 0.12) } label: { Image(systemName: "plus.magnifyingglass") }
            Button { yaw += 15 } label: { Image(systemName: "rotate.right") }
        }
        .labelStyle(.iconOnly)
        .buttonStyle(.bordered)
        .padding(10)
        .background(.black.opacity(0.52), in: Capsule())
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Model view controls")
    }

    private func loadFailure(_ message: String) -> some View {
        ContentUnavailableView(
            "Teaching model unavailable",
            systemImage: "cube.transparent",
            description: Text(message)
        )
    }
}

private struct WindowRecipeRealityView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let recipe: ResolvedExperienceSceneRecipe
    @State private var loadError: String?

    var body: some View {
        RealityView { content in
            let sceneRoot = Entity()
            sceneRoot.name = "WindowRecipeRoot"

            guard let resourceRoot = Bundle.main.resourceURL else {
                content.add(sceneRoot)
                return
            }

            let registrationRoot = Entity()
            registrationRoot.name = "WindowAuthoredRegistrationRoot"
            var requiredFailure: String?
            for binding in recipe.assets {
                let id = binding.asset.asset.assetID
                let url = resourceRoot.appending(path: binding.asset.sourcePath)
                guard FileManager.default.fileExists(atPath: url.path()) else {
                    if binding.binding.required { requiredFailure = id; break }
                    continue
                }
                do {
                    let entity = try await Entity(contentsOf: url)
                    entity.name = "WindowBoundAsset::\(id)"
                    entity.isEnabled = binding.binding.initiallyVisible
                    registrationRoot.addChild(entity)
                } catch {
                    if binding.binding.required { requiredFailure = id; break }
                }
            }

            if let requiredFailure {
                loadError = "Required scene asset failed closed: \(requiredFailure)"
                sceneRoot.addChild(windowFallback())
                content.add(sceneRoot)
                return
            }

            if !registrationRoot.children.isEmpty {
                let bounds = registrationRoot.visualBounds(recursive: true, relativeTo: nil)
                let extent = max(bounds.extents.x, bounds.extents.y, bounds.extents.z)
                let scale: Float = extent.isFinite && extent > 0.000_001 ? 0.44 / extent : 1
                sceneRoot.scale = SIMD3(repeating: scale)
                sceneRoot.position = -(bounds.center * scale)
                sceneRoot.addChild(registrationRoot)
            }
            content.add(sceneRoot)
            markReplayTokenConsumed(in: sceneRoot)
            applySidecars(in: sceneRoot, restartAnimations: true)
        } update: { content in
            guard let sceneRoot = content.entities.first(where: { $0.name == "WindowRecipeRoot" }) else { return }
            applySidecars(in: sceneRoot, restartAnimations: consumeReplayToken(in: sceneRoot))
        } placeholder: {
            ProgressView("Composing \(recipe.assets.count) bounded scene assets…")
                .controlSize(.large)
        }
        .saturation(averageSaturation)
        .overlay {
            if let loadError {
                ContentUnavailableView(
                    "Scene unavailable",
                    systemImage: "exclamationmark.triangle.fill",
                    description: Text(loadError)
                )
            }
        }
    }

    private var averageSaturation: Double {
        guard !recipe.assets.isEmpty else { return 1 }
        return recipe.assets.map(\.asset.presentation.saturationMultiplier).reduce(0, +)
            / Double(recipe.assets.count)
    }

    private func applySidecars(in root: Entity, restartAnimations: Bool) {
        for binding in model.activeRecipe?.assets ?? recipe.assets {
            let id = binding.asset.asset.assetID
            guard let entity = root.findEntity(named: "WindowBoundAsset::\(id)") else { continue }
            let presentation = binding.asset.presentation
            let flowSuppressed = binding.binding.role == .qualitativeFlow
                && presentation.particleOrFlowMode == "none"
            let isHiddenPathologyChoice = binding.binding.role == .pathologyFocus
                && !binding.binding.initiallyVisible
            let baseVisible = binding.binding.initiallyVisible
                || (!binding.binding.initiallyVisible && model.showSecondaryLayers && !isHiddenPathologyChoice)
                || (isHiddenPathologyChoice && model.selectedOptionalPathologyAssetID == id)
            let guidanceAllowed = binding.binding.role != .guidance
                || model.detailTier != .minimal
                || recipe.assets.count == 1
            let hiddenByClotState = model.procedureState.currentStep == .evtPostTreatmentComparison
                && binding.binding.role == .pathologyFocus
                && model.procedureState.completedActions.contains(.previewClotRemovalState)
            entity.isEnabled = baseVisible && guidanceAllowed && !flowSuppressed && !hiddenByClotState

            entity.components.set(OpacityComponent(opacity: 1))
            RealityPresentationSidecars.setActionEmphasis(
                on: entity,
                enabled: id == model.actionEmphasisAssetID
            )

            let shouldAnimate = !reduceMotion
                && !model.procedureState.isPaused
                && presentation.motionMode != "static"
                && presentation.motionSpeedMultiplier > 0
            if shouldAnimate && restartAnimations {
                startFirstAnimations(in: entity, speed: Float(presentation.motionSpeedMultiplier))
            } else if !shouldAnimate {
                entity.stopAllAnimations(recursive: true)
            }
        }
    }

    private func startFirstAnimations(in entity: Entity, speed: Float) {
        if let animation = entity.availableAnimations.first {
            entity.stopAllAnimations(recursive: false)
            let controller = entity.playAnimation(animation, transitionDuration: 0, startsPaused: false)
            controller.speed = speed
            return
        }
        for child in entity.children {
            startFirstAnimations(in: child, speed: speed)
        }
    }

    private func markReplayTokenConsumed(in root: Entity) {
        let marker = Entity()
        marker.name = "WindowReplayToken::\(model.replayToken)::\(model.sidecarRevision)"
        root.addChild(marker)
    }

    private func consumeReplayToken(in root: Entity) -> Bool {
        let expected = "WindowReplayToken::\(model.replayToken)::\(model.sidecarRevision)"
        if root.findEntity(named: expected) != nil { return false }
        for child in Array(root.children) where child.name.hasPrefix("WindowReplayToken::") {
            child.removeFromParent()
        }
        markReplayTokenConsumed(in: root)
        return true
    }

    private func windowFallback() -> Entity {
        let material = UnlitMaterial(color: .init(red: 0.30, green: 0.82, blue: 0.73, alpha: 0.42))
        return ModelEntity(mesh: .generateSphere(radius: 0.16), materials: [material])
    }
}
