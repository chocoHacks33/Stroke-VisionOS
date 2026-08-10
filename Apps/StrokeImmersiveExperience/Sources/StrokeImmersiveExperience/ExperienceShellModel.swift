import Foundation
import SwiftUI
#if canImport(ExperienceCore)
import ExperienceCore
#endif

enum ExperienceScreen: String, CaseIterable, Identifiable {
    case landing
    case cases
    case explore
    case library

    var id: String { rawValue }
}

enum AudienceMode: String, CaseIterable, Identifiable {
    case family = "Family"
    case presenter = "Presenter"

    var id: String { rawValue }

    var systemImage: String {
        switch self {
        case .family: "person.2.fill"
        case .presenter: "person.crop.rectangle"
        }
    }
}

enum ExplanationMode: String, CaseIterable, Identifiable {
    case calm = "Calm"
    case guided = "Guided"
    case scholar = "Scholar"

    var id: String { rawValue }
}

struct FictionalCaseCard: Identifiable, Hashable {
    let id: String
    let displayLabel: String
    let subtitle: String
    let focus: String
    let systemImage: String
    let featuredAssetID: String
}

/// Window-only presentation state. Lesson progression, tool gating, detail-tier
/// policy, and catalog resolution belong to the separate ExperienceCore target.
@MainActor
final class ExperienceShellModel: ObservableObject {
    @Published var screen: ExperienceScreen = .landing
    @Published var audienceMode: AudienceMode = .family
    @Published var explanationMode: ExplanationMode = .guided
    @Published var selectedCaseID = ExperienceShellModel.demoCases[0].id
    @Published var selectedAssetID = ExperienceShellModel.demoCases[0].featuredAssetID
    @Published var selectedAssetPath = "RealityKitContent/Assets/vision_pro_stroke_kit_v2/exports/usdz/thrombectomy_registered_hero_v2.usdz"
    @Published var detailSliderValue = 0.80 {
        didSet {
            let nextTier = tierSelector.select(detailAmount: detailSliderValue, previous: detailTier)
            if detailTier != nextTier {
                detailTier = nextTier
                stateMachine.setDetailTier(nextTier)
                resolveSelectedAsset()
                synchronizeProcedureState()
                sidecarRevision &+= 1
            }
        }
    }
    @Published private(set) var detailTier: VisualDetailTier = .reduced80
    @Published private(set) var catalog: ExperienceAssetCatalog?
    @Published private(set) var catalogLoadError: String?
    @Published var isImmersiveSpaceOpen = false
    @Published var isToolboxVisible = true
    @Published var isNotesVisible = true
    @Published var isVesselPortalVisible = false
    @Published var showSecondaryLayers = false
    @Published var selectedOptionalPathologyAssetID: String?
    @Published private(set) var selectedToolID: ExperienceToolID = .pointer
    @Published var currentNoteIndex = 0
    @Published var assetSearchText = ""
    @Published private(set) var procedureState = ProcedureExperienceState(
        audience: .developer,
        detailTier: .reduced80
    )
    @Published private(set) var activeRecipe: ResolvedExperienceSceneRecipe?
    @Published private(set) var runtimeError: String?
    @Published var pendingTransitionTitle: String?
    @Published private(set) var replayToken = 0
    @Published private(set) var sidecarRevision = 0
    @Published private(set) var actionEmphasisAssetID: String?
    @Published private(set) var isInspectingAsset = false

    private let tierSelector = VisualDetailTierSelector()
    private let recipeLibrary = ExperienceSceneRecipeLibrary()
    private let annotationCatalog = ExperienceAnnotationCatalog()
    private var stateMachine = ProcedureExperienceStateMachine(
        audience: .developer,
        initialTier: .reduced80
    )
    private var pendingStateMachine: ProcedureExperienceStateMachine?
    private var inspectionRecipe: ExperienceSceneRecipe?

    static let demoCases: [FictionalCaseCard] = [
        .init(
            id: "fictional_case_01_right_m1_orientation_v1",
            displayLabel: "Fictional Scenario 01",
            subtitle: "Right-M1 anatomy orientation",
            focus: "Locate the generic cerebral arteries and conceptual occlusion marker.",
            systemImage: "brain.head.profile",
            featuredAssetID: "thrombectomy_registered_hero_v2"
        ),
        .init(
            id: "fictional_case_02_flow_cues_v1",
            displayLabel: "Fictional Scenario 02",
            subtitle: "Qualitative flow-cue comparison",
            focus: "Compare illustrative baseline, restricted, and restored display states.",
            systemImage: "waveform.path.ecg",
            featuredAssetID: "cerebral_bloodflow_teaching_set_v2"
        ),
        .init(
            id: "fictional_case_03_structural_detail_v1",
            displayLabel: "Fictional Scenario 03",
            subtitle: "Structural anatomy detail",
            focus: "Reveal one catalogued developer-preview structural layer at a time.",
            systemImage: "square.3.layers.3d",
            featuredAssetID: "neural_detail_registered_review_assembly_v3"
        ),
        .init(
            id: "fictional_case_04_vessel_vignette_v1",
            displayLabel: "Fictional Scenario 04",
            subtitle: "Magnified vessel teaching view",
            focus: "Inspect a detached conceptual vessel-wall view that is not to scale.",
            systemImage: "scope",
            featuredAssetID: "artery_cutaway_complete_v2"
        )
    ]

    var selectedCase: FictionalCaseCard {
        Self.demoCases.first(where: { $0.id == selectedCaseID }) ?? Self.demoCases[0]
    }

    init() {
        loadCatalog()
        resolveSelectedAsset()
        synchronizeProcedureState()
    }

    var detailTierKey: String { detailTier.rawValue }

    var detailTierTitle: String {
        switch detailTier {
        case .minimal: "Calmest visual"
        case .reduced80: "Balanced detail"
        case .full: "Full detail"
        }
    }

    var activePresentation: VisualDetailPresentationParameters? {
        guard let catalog, let resolved = try? catalog.resolve(assetID: selectedAssetID, tier: detailTier) else {
            return nil
        }
        return resolved.presentation
    }

    var catalogAssets: [ExperienceAssetRecord] {
        catalog?.assets ?? []
    }

    /// Metadata remains discoverable for the complete 150-asset release. The UI
    /// locks open-cranial geometry until the separate developer gate is active.
    var accessibleCatalogAssets: [ExperienceAssetRecord] {
        catalogAssets
    }

    /// All built-in copy remains detached and explicitly authorized only as a
    /// developer placeholder. The source catalog intentionally supplies no
    /// anatomical anchors, so the UI never renders leader-line claims.
    var visiblePlaceholderNotes: [ResolvedExperienceAnnotation] {
        guard !isInspectingAsset else { return [] }
        let notes = annotationCatalog.notes(
            for: procedureState.currentStep,
            tier: detailTier,
            authorization: .developerPreviewPlaceholders
        )
        guard !notes.isEmpty else { return [] }
        switch explanationMode {
        case .calm:
            // The persistent safety badge already carries the universal disclosure;
            // prefer one short step-specific idea when one exists.
            return [notes.first(where: { $0.annotation.id != "generic_model_disclosure" }) ?? notes[0]]
        case .guided:
            return Array(notes.prefix(3))
        case .scholar:
            return notes
        }
    }

    var selectedPlaceholderNote: ResolvedExperienceAnnotation? {
        let notes = visiblePlaceholderNotes
        guard !notes.isEmpty else { return nil }
        return notes[min(max(currentNoteIndex, 0), notes.count - 1)]
    }

    var openCranialAssetsUnlocked: Bool {
        isDeveloperOpenBranchAvailable
            && procedureState.selectedPathway == .openCranial
            && procedureState.openCranialAuthorization?.isValidForOpenCranial == true
    }

    func isCatalogAssetLocked(_ asset: ExperienceAssetRecord) -> Bool {
        let isOpenAsset = asset.primaryCategory == .toolsOpenCranial
            || asset.primaryCategory == .openCranialAnatomyState
        return isOpenAsset && !openCranialAssetsUnlocked
    }

    var explanationSummary: String {
        switch explanationMode {
        case .calm:
            "One short idea at a time, with optional details hidden."
        case .guided:
            "A paced explanation with context, labels, and clear next actions."
        case .scholar:
            "Expanded structural labels and catalogued developer-placeholder context."
        }
    }

    var currentStepTitle: String {
        switch procedureState.currentStep {
        case .caseSelect: "Choose a scenario"
        case .orientHead: "Orient the head"
        case .explainStroke: "Understand the blockage"
        case .evtVascularPath: "Follow the vascular route"
        case .evtOcclusion: "Focus on the occlusion"
        case .evtDeviceConcept: "Preview a device concept"
        case .evtPostTreatmentComparison: "Compare illustrative states"
        case .evtRecoveryOverview: "Continue into recovery context"
        case .openConfirmSite: "Confirm the catalogued open-pathway site"
        case .openCranialAccess: "Preview the cranial-access state"
        case .openDuralAccess: "Preview the protective-layer state"
        case .openTreatReviewedCondition: "Preview the catalogued condition state"
        case .openReplaceAndFixBoneFlap: "Preview the closure state"
        case .openPostClosureReview: "Review the post-closure context"
        }
    }

    var procedureProgress: (current: Int, total: Int) {
        stateMachine.progress()
    }

    var isDeveloperOpenBranchAvailable: Bool {
        ProcessInfo.processInfo.environment["STROKE_ENABLE_OPEN_CRANIAL_DEVELOPER_PREVIEW"] == "1"
    }

    var availableTools: [ExperienceToolDescriptor] {
        guard !isInspectingAsset else { return [] }
        return ExperienceToolboxPolicy.availableTools(for: procedureState).filter {
            ExperienceToolboxPolicy.intent(for: $0.id, state: procedureState) != .noOp
        }
    }

    func select(_ caseCard: FictionalCaseCard) {
        selectedCaseID = caseCard.id
        selectAsset(id: caseCard.featuredAssetID)
        stateMachine = ProcedureExperienceStateMachine(
            audience: .developer,
            initialTier: detailTier
        )
        stateMachine.beginEndovascularEducationalPathway()
        synchronizeProcedureState()
        prepareSingleAssetInspection(id: caseCard.featuredAssetID)
        screen = .explore
    }

    func selectAsset(id: String) {
        selectedAssetID = id
        resolveSelectedAsset()
    }

    func inspectAsset(id: String) {
        selectAsset(id: id)
        prepareSingleAssetInspection(id: id)
        screen = .explore
    }

    func resetExperience() {
        selectedCaseID = Self.demoCases[0].id
        selectedAssetID = Self.demoCases[0].featuredAssetID
        selectedAssetPath = Self.fallbackPath(for: selectedAssetID)
        explanationMode = .guided
        detailSliderValue = 0.80
        detailTier = .reduced80
        currentNoteIndex = 0
        isToolboxVisible = true
        isNotesVisible = true
        isVesselPortalVisible = false
        showSecondaryLayers = false
        selectedOptionalPathologyAssetID = nil
        selectedToolID = .pointer
        actionEmphasisAssetID = nil
        inspectionRecipe = nil
        isInspectingAsset = false
        stateMachine = ProcedureExperienceStateMachine(audience: .developer, initialTier: .reduced80)
        synchronizeProcedureState()
        screen = .landing
    }

    func requestNextStep() {
        guard !isInspectingAsset else { return }
        var candidate = stateMachine
        do {
            try candidate.next()
            guard candidate.state.currentStep != stateMachine.state.currentStep else { return }
            if recipeLibrary.recipe(for: candidate.state.currentStep)?.userConfirmedEntry == true {
                pendingStateMachine = candidate
                pendingTransitionTitle = "Open the next detached conceptual teaching state?"
            } else {
                commit(candidate)
            }
        } catch {
            runtimeError = error.localizedDescription
        }
    }

    func confirmPendingTransition() {
        guard let pendingStateMachine else { return }
        commit(pendingStateMachine)
        self.pendingStateMachine = nil
        pendingTransitionTitle = nil
    }

    func cancelPendingTransition() {
        pendingStateMachine = nil
        pendingTransitionTitle = nil
    }

    func previousStep() {
        guard !isInspectingAsset else { return }
        var candidate = stateMachine
        do {
            try candidate.previous()
            commit(candidate)
        } catch {
            runtimeError = error.localizedDescription
        }
    }

    func togglePause() {
        guard !isInspectingAsset else { return }
        if stateMachine.state.isPaused {
            stateMachine.resume()
            replayCurrentStep()
        } else {
            stateMachine.pause()
        }
        synchronizeProcedureState(rebuildRecipe: false)
    }

    func replayCurrentStep() {
        replayToken &+= 1
    }

    func activateTool(_ toolID: ExperienceToolID) {
        guard !isInspectingAsset else { return }
        let intent = ExperienceToolboxPolicy.intent(for: toolID, state: stateMachine.state)
        selectedToolID = toolID
        switch intent {
        case .noOp:
            break
        case .toggleAnnotations:
            isNotesVisible.toggle()
        case .toggleLayerVisibility:
            showSecondaryLayers.toggle()
        case .cameraPreset(let preset):
            if preset == .arteryLumenThreshold {
                isVesselPortalVisible = true
            }
        case .procedureAction(let action):
            do {
                actionEmphasisAssetID = activeRecipe?.assets.first(where: {
                    $0.binding.role == .educationalTool
                        || $0.binding.role == .pathologyFocus
                        || $0.binding.role == .registeredState
                })?.asset.asset.assetID
                if action == .previewReviewedConditionState {
                    selectedOptionalPathologyAssetID = activeRecipe?.assets.first(where: {
                        $0.binding.role == .pathologyFocus && !$0.binding.initiallyVisible
                    })?.asset.asset.assetID
                }
                if action == .revealCranialAccessLayer
                    || action == .revealDuralAccessLayer
                    || action == .previewClosureState
                    || action == .compareClosureStates {
                    showSecondaryLayers = true
                }
                try stateMachine.perform(action)
                synchronizeProcedureState(rebuildRecipe: false)
                if action == .previewDeviceConcept
                    || action == .previewClotRemovalState
                    || action == .compareIllustrativeFlowStates
                    || action == .previewClosureState {
                    replayCurrentStep()
                }
            } catch {
                runtimeError = error.localizedDescription
            }
        case .restoreOriginal:
            restoreOverview()
        }
    }

    func clearRuntimeError() {
        runtimeError = nil
    }

    func restoreOverview() {
        stateMachine.restoreOverview()
        isVesselPortalVisible = false
        showSecondaryLayers = false
        selectedOptionalPathologyAssetID = nil
        selectedToolID = .pointer
        actionEmphasisAssetID = nil
        inspectionRecipe = nil
        isInspectingAsset = false
        synchronizeProcedureState()
    }

    func beginDeveloperOpenCranialPreview() {
        guard isDeveloperOpenBranchAvailable else {
            runtimeError = "The separate open-cranial developer preview is not enabled."
            return
        }
        var developerMachine = ProcedureExperienceStateMachine(
            audience: .developer,
            initialTier: detailTier
        )
        let authorization = ReviewedPathwayAuthorization(
            pathway: .openCranial,
            reviewedScenarioID: "developer-placeholder-open-pathway",
            reviewedContentRevision: "catalog-v1-unapproved-placeholder",
            audience: .developer
        )
        do {
            try developerMachine.beginOpenCranialEducationalPathway(authorization: authorization)
            pendingStateMachine = developerMachine
            pendingTransitionTitle = "Enter the separately gated, non-graphic open-cranial developer preview?"
        } catch {
            runtimeError = error.localizedDescription
        }
    }

    static func fallbackPath(for assetID: String) -> String {
        "RealityKitContent/Assets/vision_pro_stroke_kit_v2/exports/usdz/\(assetID).usdz"
    }

    private func loadCatalog() {
        guard let resourceRoot = Bundle.main.resourceURL else {
            catalogLoadError = "The application resource root is unavailable."
            return
        }
        let catalogURL = resourceRoot.appending(
            path: "RealityKitContent/InterfaceMedia/visual_detail_variants_v1/visual_detail_variant_catalog_v1.json"
        )
        do {
            catalog = try ExperienceAssetCatalog(contentsOf: catalogURL)
            catalogLoadError = nil
        } catch {
            catalog = nil
            catalogLoadError = error.localizedDescription
        }
    }

    private func resolveSelectedAsset() {
        guard let resolved = try? catalog?.resolve(assetID: selectedAssetID, tier: detailTier) else {
            selectedAssetPath = Self.fallbackPath(for: selectedAssetID)
            return
        }
        selectedAssetPath = resolved.sourcePath
    }

    private func commit(_ candidate: ProcedureExperienceStateMachine) {
        stateMachine = candidate
        isVesselPortalVisible = false
        showSecondaryLayers = false
        selectedOptionalPathologyAssetID = nil
        selectedToolID = .pointer
        actionEmphasisAssetID = nil
        inspectionRecipe = nil
        isInspectingAsset = false
        synchronizeProcedureState()
    }

    private func synchronizeProcedureState(rebuildRecipe: Bool = true) {
        procedureState = stateMachine.state
        if rebuildRecipe {
            resolveActiveRecipe()
        }
    }

    private func resolveActiveRecipe() {
        guard let catalog else {
            activeRecipe = nil
            return
        }
        do {
            if let inspectionRecipe {
                activeRecipe = try recipeLibrary.resolve(
                    inspectionRecipe,
                    tier: detailTier,
                    catalog: catalog,
                    context: .developerPreview
                )
            } else if let recipe = recipeLibrary.recipe(for: stateMachine.state.currentStep) {
                activeRecipe = try recipeLibrary.resolve(
                    recipe,
                    state: stateMachine.state,
                    catalog: catalog,
                    context: .developerPreview
                )
            } else {
                activeRecipe = nil
            }
            runtimeError = nil
        } catch {
            activeRecipe = nil
            runtimeError = error.localizedDescription
        }
    }

    private func prepareSingleAssetInspection(id: String) {
        guard let record = catalog?.asset(id: id) else { return }
        let role: SceneAssetRole
        let camera: ExperienceCameraPresetID
        switch record.primaryCategory {
        case .pathologyMacro:
            role = .pathologyFocus
            camera = .occlusionCloseup
        case .anatomyVascular:
            role = .vascularFocus
            camera = .vascularRoute
        case .bloodFlowTeaching:
            role = .qualitativeFlow
            camera = .illustrativeFlowComparison
        case .microConceptual:
            role = .qualitativeFlow
            camera = .microcirculationConcept
        case .toolsEndovascular, .toolsOpenCranial:
            role = .educationalTool
            camera = .deviceConcept
        case .clinicalContext, .spatialEnvironment:
            role = .clinicalContext
            camera = .consultationOverview
        case .guidance:
            role = .guidance
            camera = .consultationOverview
        case .compositeAssembly, .openCranialAnatomyState:
            role = .registeredState
            camera = .headOrientation
        case .adaptivePresentation, .anatomyCNSMacro, .anatomyHeadNeckSupport:
            role = .anatomyFocus
            camera = .headOrientation
        }

        inspectionRecipe = ExperienceSceneRecipe(
            id: .init(rawValue: "CATALOG_SINGLE_\(id)"),
            pathway: .overview,
            step: nil,
            cameraPreset: camera,
            assetBindings: [.init(id, role: role)],
            userConfirmedEntry: record.primaryCategory == .microConceptual
        )
        isInspectingAsset = true
        resolveActiveRecipe()
    }

    func exitInspectionMode() {
        inspectionRecipe = nil
        isInspectingAsset = false
        actionEmphasisAssetID = nil
        showSecondaryLayers = false
        selectedOptionalPathologyAssetID = nil
        resolveActiveRecipe()
    }
}
