import RealityKit
import SwiftUI
#if canImport(ExperienceCore)
import ExperienceCore
#endif

struct ImmersiveExperienceView: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @EnvironmentObject private var feedback: InteractionFeedbackController
    @Environment(\.dismissImmersiveSpace) private var dismissImmersiveSpace
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var loadMessage: String?
    @State private var loadAttempt = 0

    var body: some View {
        RealityView { content, attachments in
            let stage = Entity()
            stage.name = "StrokeEducationStage"
            content.add(stage)

            await loadActiveRecipe(into: stage)

            addAttachment(.disclosure, to: stage, attachments: attachments, position: [0, 2.05, -1.18])
            addAttachment(.notes, to: stage, attachments: attachments, position: [-0.72, 1.47, -1.05])
            addAttachment(.toolbox, to: stage, attachments: attachments, position: [0.72, 1.42, -1.02])
            addAttachment(.vesselPortal, to: stage, attachments: attachments, position: [0.62, 1.76, -0.96])
            addAttachment(.controls, to: stage, attachments: attachments, position: [0, 0.78, -1.03])
        } update: { content, attachments in
            guard let stage = content.entities.first(where: { $0.name == "StrokeEducationStage" }) else { return }
            setAttachmentVisibility(.notes, visible: model.isNotesVisible, in: stage)
            setAttachmentVisibility(.toolbox, visible: model.isToolboxVisible, in: stage)
            setAttachmentVisibility(.vesselPortal, visible: model.isVesselPortalVisible, in: stage)
            applyPresentationSidecar(to: stage, restartAnimations: consumeReplayToken(in: stage))

            if let disclosure = attachments.entity(for: ImmersiveAttachmentID.disclosure.rawValue) {
                disclosure.isEnabled = true
            }
        } attachments: {
            Attachment(id: ImmersiveAttachmentID.disclosure.rawValue) {
                SafetyBadge()
            }

            Attachment(id: ImmersiveAttachmentID.notes.rawValue) {
                ImmersiveNotesCard()
                    .environmentObject(model)
            }

            Attachment(id: ImmersiveAttachmentID.toolbox.rawValue) {
                ImmersiveToolboxCard()
                    .environmentObject(model)
            }

            Attachment(id: ImmersiveAttachmentID.vesselPortal.rawValue) {
                DetachedVesselPortal()
                    .environmentObject(model)
            }

            Attachment(id: ImmersiveAttachmentID.controls.rawValue) {
                ImmersiveControlBar(
                    home: {
                        Task {
                            await dismissImmersiveSpace()
                            model.isImmersiveSpaceOpen = false
                            model.resetExperience()
                        }
                    },
                    exit: {
                        Task {
                            await dismissImmersiveSpace()
                            model.isImmersiveSpaceOpen = false
                        }
                    }
                )
                .environmentObject(model)
                .environmentObject(feedback)
            }
        }
        .id("\(activeRecipeKey)::load-\(loadAttempt)")
        .gesture(
            SpatialTapGesture()
                .targetedToAnyEntity()
                .onEnded { _ in
                    feedback.emit(.controlCommit)
                    withAnimation(.easeInOut(duration: 0.2)) {
                        model.isToolboxVisible.toggle()
                    }
                }
        )
        .onDisappear {
            model.isImmersiveSpaceOpen = false
        }
        .overlay(alignment: .top) {
            if let loadMessage {
                VStack(spacing: 8) {
                    Label(loadMessage, systemImage: "exclamationmark.triangle.fill")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(ExperienceTheme.amber)
                    if loadMessage.hasPrefix("Required scene asset failed closed") {
                        Button("Retry asset loading") {
                            self.loadMessage = nil
                            loadAttempt &+= 1
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .padding(12)
                .experienceGlassPanel(cornerRadius: 16)
                .padding(.top, 30)
            }
        }
        .confirmationDialog(
            model.pendingTransitionTitle ?? "Confirm transition",
            isPresented: Binding(
                get: { model.pendingTransitionTitle != nil },
                set: { if !$0 { model.cancelPendingTransition() } }
            ),
            titleVisibility: .visible
        ) {
            Button("Continue to catalogued developer-preview state") {
                model.confirmPendingTransition()
            }
            Button("Keep current view", role: .cancel) {
                model.cancelPendingTransition()
            }
        } message: {
            Text("The next view is scripted, non-graphic, generic, and not surgical instruction or patient-specific guidance.")
        }
        .saturation(activeSaturation)
        .contrast(0.92 + activeSaturation * 0.08)
    }

    private var activeRecipeKey: String {
        model.activeRecipe?.recipe.id.rawValue ?? "fallback::\(model.selectedAssetID)"
    }

    private var activeSaturation: Double {
        guard let assets = model.activeRecipe?.assets, !assets.isEmpty else { return 1 }
        return assets.map(\.asset.presentation.saturationMultiplier).reduce(0, +)
            / Double(assets.count)
    }

    @MainActor
    private func loadActiveRecipe(into stage: Entity) async {
        guard let resourceRoot = Bundle.main.resourceURL else {
            loadMessage = "The resource bundle could not be opened."
            return
        }

        guard let recipe = model.activeRecipe else {
            loadMessage = model.runtimeError ?? "No safe bounded scene recipe is available."
            stage.addChild(fallbackModel())
            stage.addChild(coarseInteractionProxy())
            return
        }

        let sharedRegistrationRoot = Entity()
        sharedRegistrationRoot.name = "AuthoredRegistrationRoot"
        var loadFailures: [String] = []
        var requiredFailure: String?

        for resolvedBinding in recipe.assets {
            let assetID = resolvedBinding.asset.asset.assetID
            do {
                let source = try await RuntimeRealityAssetLoader.loadEntity(
                    assetID: assetID,
                    sourcePath: resolvedBinding.asset.sourcePath,
                    resourceRoot: resourceRoot
                )
                source.name = "BoundAsset::\(assetID)"
                source.isEnabled = resolvedBinding.binding.initiallyVisible
                sharedRegistrationRoot.addChild(source)
            } catch {
                if resolvedBinding.binding.required {
                    requiredFailure = error.localizedDescription
                    break
                }
                loadFailures.append(assetID)
            }
        }

        if let requiredFailure {
            loadMessage = "Required scene asset failed closed: \(requiredFailure)"
            stage.addChild(fallbackModel())
            stage.addChild(coarseInteractionProxy())
            return
        }

        guard !sharedRegistrationRoot.children.isEmpty else {
            loadMessage = "None of the bounded recipe assets could be loaded."
            stage.addChild(fallbackModel())
            stage.addChild(coarseInteractionProxy())
            return
        }

        let fittedRoot = fittedSharedPresentationRoot(containing: sharedRegistrationRoot)
        fittedRoot.name = "ActiveTeachingModel"
        stage.addChild(fittedRoot)
        stage.addChild(coarseInteractionProxy())
        markReplayTokenConsumed(in: stage)
        applyPresentationSidecar(to: stage, restartAnimations: true)
        loadMessage = loadFailures.isEmpty
            ? nil
            : "Optional developer-preview assets were unavailable: \(loadFailures.joined(separator: ", "))"
    }

    /// Applies one fit transform to the entire recipe. Child models keep their
    /// authored transforms so registered anatomy is never normalized per asset.
    private func fittedSharedPresentationRoot(containing sharedRoot: Entity) -> Entity {
        let root = Entity()
        let bounds = sharedRoot.visualBounds(recursive: true, relativeTo: nil)
        let maximumExtent = max(bounds.extents.x, bounds.extents.y, bounds.extents.z)
        let fitScale: Float = maximumExtent.isFinite && maximumExtent > 0.000_001
            ? 0.62 / maximumExtent
            : 1

        root.scale = SIMD3(repeating: fitScale)
        root.position = SIMD3<Float>(0, 1.42, -1.18) - (bounds.center * fitScale)
        root.addChild(sharedRoot)
        return root
    }

    private func coarseInteractionProxy() -> Entity {
        let proxy = Entity()
        proxy.name = "CoarseInteractionProxy"
        proxy.position = [0, 1.42, -1.18]
        proxy.components.set(InputTargetComponent())
        proxy.components.set(CollisionComponent(shapes: [.generateSphere(radius: 0.42)]))
        return proxy
    }

    private func fallbackModel() -> Entity {
        var material = PhysicallyBasedMaterial()
        material.baseColor = .init(tint: .init(red: 0.30, green: 0.82, blue: 0.73, alpha: 0.55))
        material.roughness = 0.34
        material.metallic = 0.08
        let entity = ModelEntity(mesh: .generateSphere(radius: 0.22), materials: [material])
        entity.name = "FallbackTeachingMarker"
        entity.position = [0, 1.42, -1.18]
        return entity
    }

    private func applyPresentationSidecar(to stage: Entity, restartAnimations: Bool) {
        guard stage.findEntity(named: "ActiveTeachingModel") != nil,
              let recipe = model.activeRecipe else { return }

        for resolvedBinding in recipe.assets {
            let assetID = resolvedBinding.asset.asset.assetID
            guard let entity = stage.findEntity(named: "BoundAsset::\(assetID)") else { continue }
            let presentation = resolvedBinding.asset.presentation
            let isOptionalLayer = !resolvedBinding.binding.initiallyVisible
            let flowSuppressed = resolvedBinding.binding.role == .qualitativeFlow
                && presentation.particleOrFlowMode == "none"
            let isHiddenPathologyChoice = resolvedBinding.binding.role == .pathologyFocus
                && !resolvedBinding.binding.initiallyVisible
            let baseVisible = resolvedBinding.binding.initiallyVisible
                || (isOptionalLayer && model.showSecondaryLayers && !isHiddenPathologyChoice)
                || (isHiddenPathologyChoice && model.selectedOptionalPathologyAssetID == assetID)
            let guidanceAllowed = resolvedBinding.binding.role != .guidance
                || model.detailTier != .minimal
                || recipe.assets.count == 1
            let hiddenByClotState = model.procedureState.currentStep == .evtPostTreatmentComparison
                && resolvedBinding.binding.role == .pathologyFocus
                && model.procedureState.completedActions.contains(.previewClotRemovalState)
            entity.isEnabled = baseVisible && guidanceAllowed && !flowSuppressed && !hiddenByClotState

            entity.components.set(OpacityComponent(opacity: 1))
            RealityPresentationSidecars.setActionEmphasis(
                on: entity,
                enabled: assetID == model.actionEmphasisAssetID
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

    private func markReplayTokenConsumed(in stage: Entity) {
        let marker = Entity()
        marker.name = "ReplayToken::\(model.replayToken)::\(model.sidecarRevision)"
        stage.addChild(marker)
    }

    private func consumeReplayToken(in stage: Entity) -> Bool {
        let expectedName = "ReplayToken::\(model.replayToken)::\(model.sidecarRevision)"
        if stage.findEntity(named: expectedName) != nil { return false }
        for child in Array(stage.children) where child.name.hasPrefix("ReplayToken::") {
            child.removeFromParent()
        }
        markReplayTokenConsumed(in: stage)
        return true
    }

    private func startFirstAnimations(in entity: Entity, speed: Float) {
        if let first = entity.availableAnimations.first {
            entity.stopAllAnimations(recursive: false)
            let controller = entity.playAnimation(first, transitionDuration: 0, startsPaused: false)
            controller.speed = speed
            return
        }
        for child in entity.children {
            startFirstAnimations(in: child, speed: speed)
        }
    }

    private func addAttachment(
        _ id: ImmersiveAttachmentID,
        to stage: Entity,
        attachments: RealityViewAttachments,
        position: SIMD3<Float>
    ) {
        guard let entity = attachments.entity(for: id.rawValue) else { return }
        entity.name = "Attachment::\(id.rawValue)"
        entity.position = position
        stage.addChild(entity)
    }

    private func setAttachmentVisibility(
        _ id: ImmersiveAttachmentID,
        visible: Bool,
        in stage: Entity
    ) {
        stage.findEntity(named: "Attachment::\(id.rawValue)")?.isEnabled = visible
    }
}

private enum ImmersiveAttachmentID: String {
    case disclosure
    case notes
    case toolbox
    case vesselPortal
    case controls
}

private struct ImmersiveNotesCard: View {
    @EnvironmentObject private var model: ExperienceShellModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Label("Detached developer-placeholder note", systemImage: "rectangle.and.text.magnifyingglass")
                    .font(.headline)
                Spacer()
                Text(model.explanationMode.rawValue)
                    .font(.caption.bold())
                    .foregroundStyle(ExperienceTheme.mint)
            }

            Text(title)
                .font(.title3.weight(.semibold))
            Text(bodyCopy)
                .font(.callout)
                .foregroundStyle(.white.opacity(0.76))
                .fixedSize(horizontal: false, vertical: true)

            if model.detailTierKey == "full" {
                Divider()
                Label("Unreviewed placeholder copy · generic qualitative display", systemImage: "info.circle.fill")
                    .font(.caption)
                    .foregroundStyle(ExperienceTheme.amber)
            }
        }
        .padding(18)
        .frame(width: 340, alignment: .leading)
        .experienceGlassPanel(cornerRadius: 22, tint: .black.opacity(0.38))
        .accessibilityElement(children: .combine)
    }

    private var title: String {
        if model.isInspectingAsset { return "Neutral asset inspection" }
        return model.selectedPlaceholderNote?.displayCopy.title ?? "Developer-placeholder context"
    }

    private var bodyCopy: String {
        if model.isInspectingAsset {
            return "Developer-preview asset \(model.selectedAssetID). Lesson steps and procedure actions are paused; this detached card is not an anatomy-pinned claim."
        }
        return model.selectedPlaceholderNote?.displayCopy.body
            ?? "Developer-placeholder framing is unavailable for this catalogued state."
    }
}

private struct ImmersiveToolboxCard: View {
    @EnvironmentObject private var model: ExperienceShellModel
    @State private var pendingTool: ExperienceToolDescriptor?

    var body: some View {
        if model.isInspectingAsset {
            inspectionToolbox
        } else {
            lessonToolbox
        }
    }

    private var inspectionToolbox: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Single-asset inspection", systemImage: "cube.transparent.fill")
                .font(.headline)
                .foregroundStyle(ExperienceTheme.mint)
            Text("Procedure tools are disabled while inspecting arbitrary catalog geometry.")
                .font(.caption)
                .foregroundStyle(ExperienceTheme.quietText)
                .fixedSize(horizontal: false, vertical: true)
            Button {
                model.isNotesVisible.toggle()
            } label: {
                Label(model.isNotesVisible ? "Hide metadata" : "Show metadata", systemImage: "note.text")
            }
            Button {
                model.exitInspectionMode()
            } label: {
                Label("Return to lesson", systemImage: "arrow.uturn.backward.circle.fill")
            }
            .buttonStyle(.borderedProminent)
            .tint(ExperienceTheme.mint.opacity(0.72))
        }
        .buttonStyle(.bordered)
        .padding(16)
        .frame(width: 300)
        .experienceGlassPanel(cornerRadius: 22, tint: .black.opacity(0.38))
    }

    private var lessonToolbox: some View {
        VStack(alignment: .leading, spacing: 11) {
            HStack {
                Label("Teaching toolbox", systemImage: "hand.tap.fill")
                    .font(.headline)
                Spacer()
                Button {
                    model.isToolboxVisible = false
                } label: {
                    Image(systemName: "xmark")
                }
                .buttonStyle(.plain)
            }

            Text("Look, then pinch to choose. Tap the model to hide or reveal this panel.")
                .font(.caption)
                .foregroundStyle(ExperienceTheme.quietText)
                .fixedSize(horizontal: false, vertical: true)

            ForEach(model.availableTools) { tool in
                Button {
                    if tool.requiresConfirmation {
                        pendingTool = tool
                    } else {
                        model.activateTool(tool.id)
                    }
                } label: {
                    HStack(spacing: 10) {
                        Image(systemName: tool.systemImageName)
                            .frame(width: 24)
                        Text(displayTitle(for: tool))
                        Spacer()
                        if model.selectedToolID == tool.id {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundStyle(ExperienceTheme.mint)
                        }
                    }
                }
                .buttonStyle(.bordered)
                .tint(model.selectedToolID == tool.id ? ExperienceTheme.mint : .white.opacity(0.26))
            }

            StepTimelineView(compact: true)
            ProcedureTransportControls()

            if !model.procedureState.completedActions.isEmpty {
                Label(
                    "\(model.procedureState.completedActions.count) scripted state recorded · active focus highlighted",
                    systemImage: "checkmark.circle.fill"
                )
                .font(.caption2.weight(.semibold))
                .foregroundStyle(ExperienceTheme.mint)
            }

            Label("Scripted educational state changes only", systemImage: "lock.shield.fill")
                .font(.caption2.weight(.semibold))
                .foregroundStyle(ExperienceTheme.amber)
            if let preset = model.activeRecipe?.recipe.cameraPreset {
                Text("Catalogued view preset: \(String(describing: preset)) · no automatic anatomical navigation")
                    .font(.caption2)
                    .foregroundStyle(ExperienceTheme.quietText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(16)
        .frame(width: 300)
        .experienceGlassPanel(cornerRadius: 22, tint: .black.opacity(0.38))
        .confirmationDialog(
            "Confirm this scripted developer-preview tool?",
            isPresented: Binding(
                get: { pendingTool != nil },
                set: { if !$0 { pendingTool = nil } }
            ),
            titleVisibility: .visible
        ) {
            Button("Continue") {
                if let pendingTool {
                    model.activateTool(pendingTool.id)
                }
                pendingTool = nil
            }
            Button("Cancel", role: .cancel) {
                pendingTool = nil
            }
        } message: {
            Text("The action is a reversible, non-graphic state change. Vessel journeys are detached, magnified, conceptual, and not to anatomical scale.")
        }
    }

    private func displayTitle(for tool: ExperienceToolDescriptor) -> String {
        switch tool.id {
        case .clotRemovalStatePreview: "Removal concept replay"
        case .deviceConceptPreview: "Device concept replay"
        default: tool.title
        }
    }
}

private struct DetachedVesselPortal: View {
    @EnvironmentObject private var model: ExperienceShellModel

    private var modelURL: URL? {
        Bundle.main.resourceURL?.appending(
            path: "RealityKitContent/Assets/vision_pro_stroke_kit_v2/exports/usdz/artery_cutaway_complete_v2.usdz"
        )
    }

    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                Circle()
                    .fill(.black.opacity(0.82))
                Circle()
                    .stroke(ExperienceTheme.amber.opacity(0.72), lineWidth: 3)

                if let modelURL, FileManager.default.fileExists(atPath: modelURL.path()) {
                    Model3D(url: modelURL) { phase in
                        switch phase {
                        case .empty:
                            ProgressView()
                        case .success(let content):
                            content
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .padding(24)
                        case .failure:
                            portalFallback
                        @unknown default:
                            portalFallback
                        }
                    }
                } else {
                    portalFallback
                }
            }
            .frame(width: 250, height: 250)
            .clipShape(Circle())

            Text("DETACHED VESSEL VIGNETTE")
                .font(.caption2.bold())
                .tracking(1.2)
                .foregroundStyle(ExperienceTheme.amber)
            Text("Conceptual · magnified · not to scale")
                .font(.caption2)
                .foregroundStyle(.white.opacity(0.72))

            Button("Return to overview") {
                model.isVesselPortalVisible = false
            }
            .buttonStyle(.bordered)
        }
        .padding(14)
        .experienceGlassPanel(cornerRadius: 130, tint: .black.opacity(0.48))
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Detached conceptual vessel vignette, magnified and not to anatomical scale")
    }

    private var portalFallback: some View {
        Image(systemName: "scope")
            .font(.system(size: 76, weight: .light))
            .foregroundStyle(ExperienceTheme.amber)
    }
}

private struct ImmersiveControlBar: View {
    @EnvironmentObject private var model: ExperienceShellModel
    let home: () -> Void
    let exit: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button(action: home) {
                Label("Reset and return home", systemImage: "house.fill")
            }
            if model.isInspectingAsset {
                Button {
                    model.exitInspectionMode()
                } label: {
                    Label("Return to lesson", systemImage: "arrow.uturn.backward")
                }
            } else {
                ProcedureTransportControls()
                StepTimelineView(compact: true)
            }
            Divider().frame(height: 24)
            Button {
                model.isNotesVisible.toggle()
            } label: {
                Label(model.isNotesVisible ? "Hide notes" : "Show notes", systemImage: "note.text")
            }
            Button {
                model.isToolboxVisible.toggle()
            } label: {
                Label(model.isToolboxVisible ? "Hide tools" : "Show tools", systemImage: "wrench.and.screwdriver")
            }
            Divider().frame(height: 24)
            Text(model.detailTierTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(ExperienceTheme.mint)
            InteractionFeedbackSettingsButton()
            Button(action: exit) {
                Label("Exit", systemImage: "xmark.circle.fill")
            }
        }
        .buttonStyle(.bordered)
        .padding(12)
        .experienceGlassPanel(cornerRadius: 22, tint: .black.opacity(0.42))
    }
}
