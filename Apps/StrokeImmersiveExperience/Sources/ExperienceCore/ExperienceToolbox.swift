import Foundation

public enum ExperienceToolID: String, CaseIterable, Codable, Sendable, Hashable {
    case pointer
    case orbit
    case focus
    case annotation
    case layerVisibility
    case vascularFlyThrough
    case deviceConceptPreview
    case clotRemovalStatePreview
    case flowStateComparison
    case openAccessStatePreview
    case openDuralStatePreview
    case openConditionStatePreview
    case openClosureStatePreview
    case restoreOriginal
}

public enum ExperienceToolKind: String, Codable, Sendable, Hashable {
    case navigation
    case explanation
    case scriptedEducationalState
    case safety
}

public struct ExperienceToolDescriptor: Codable, Sendable, Hashable, Identifiable {
    public let id: ExperienceToolID
    public let title: String
    public let systemImageName: String
    public let kind: ExperienceToolKind
    public let requiresConfirmation: Bool
    public let nonGraphicOnly: Bool

    public init(
        id: ExperienceToolID,
        title: String,
        systemImageName: String,
        kind: ExperienceToolKind,
        requiresConfirmation: Bool = false,
        nonGraphicOnly: Bool = true
    ) {
        self.id = id
        self.title = title
        self.systemImageName = systemImageName
        self.kind = kind
        self.requiresConfirmation = requiresConfirmation
        self.nonGraphicOnly = nonGraphicOnly
    }
}

public enum ExperienceInputSource: String, Codable, Sendable, Hashable {
    case systemSpatialTap
    case systemPinch
    case directTouch
    case simulatorPointer
    case keyboard
    case accessibilityAction
}

/// Semantic input only. The app relies on visionOS-owned focus/pinch behavior and never stores
/// joint poses, raw gaze, pupil measurements, or inferred emotion.
public enum ExperienceGestureCommand: Codable, Sendable, Hashable {
    case toggleToolbox
    case dismissToolbox
    case selectTool(ExperienceToolID)
    case activateSelectedTool
    case selectFocusedHotspot(String)
    case orbit(horizontal: Double, vertical: Double)
    case boundedZoom(delta: Double)
    case next
    case previous
    case pauseOrResume
    case restoreOriginal
}

public struct ExperienceInputEvent: Codable, Sendable, Hashable {
    public let source: ExperienceInputSource
    public let command: ExperienceGestureCommand

    public init(source: ExperienceInputSource, command: ExperienceGestureCommand) {
        self.source = source
        self.command = command
    }
}

public enum ExperienceToolIntent: Sendable, Hashable {
    case noOp
    case procedureAction(ExperienceProcedureAction)
    case cameraPreset(ExperienceCameraPresetID)
    case toggleAnnotations
    case toggleLayerVisibility
    case restoreOriginal
}

public struct ExperienceToolboxState: Sendable, Hashable {
    public var isPresented: Bool
    public var selectedTool: ExperienceToolID

    public init(isPresented: Bool = false, selectedTool: ExperienceToolID = .pointer) {
        self.isPresented = isPresented
        self.selectedTool = selectedTool
    }

    public mutating func apply(_ event: ExperienceInputEvent, availableTools: Set<ExperienceToolID>) {
        switch event.command {
        case .toggleToolbox:
            isPresented.toggle()
        case .dismissToolbox:
            isPresented = false
        case .selectTool(let tool) where availableTools.contains(tool):
            selectedTool = tool
            isPresented = false
        case .restoreOriginal:
            selectedTool = .restoreOriginal
            isPresented = false
        default:
            break
        }
    }
}

public enum ExperienceToolboxPolicy {
    public static let descriptors: [ExperienceToolID: ExperienceToolDescriptor] = {
        let values: [ExperienceToolDescriptor] = [
            .init(id: .pointer, title: "Point", systemImageName: "cursorarrow.rays", kind: .navigation),
            .init(id: .orbit, title: "Orbit", systemImageName: "rotate.3d", kind: .navigation),
            .init(id: .focus, title: "Focus", systemImageName: "scope", kind: .navigation),
            .init(id: .annotation, title: "Notes", systemImageName: "note.text", kind: .explanation),
            .init(id: .layerVisibility, title: "Layers", systemImageName: "square.3.layers.3d", kind: .explanation),
            .init(id: .vascularFlyThrough, title: "Vessel journey", systemImageName: "point.forward.to.point.capsulepath", kind: .navigation, requiresConfirmation: true),
            .init(id: .deviceConceptPreview, title: "Device concept", systemImageName: "waveform.path.ecg.rectangle", kind: .scriptedEducationalState, requiresConfirmation: true),
            .init(id: .clotRemovalStatePreview, title: "Removal preview", systemImageName: "arrow.right.circle", kind: .scriptedEducationalState, requiresConfirmation: true),
            .init(id: .flowStateComparison, title: "Compare flow", systemImageName: "rectangle.split.2x1", kind: .scriptedEducationalState),
            .init(id: .openAccessStatePreview, title: "Access layer", systemImageName: "square.3.layers.3d.down.right", kind: .scriptedEducationalState, requiresConfirmation: true),
            .init(id: .openDuralStatePreview, title: "Protective layer", systemImageName: "shield.lefthalf.filled", kind: .scriptedEducationalState, requiresConfirmation: true),
            .init(id: .openConditionStatePreview, title: "Condition state", systemImageName: "circle.dashed.inset.filled", kind: .scriptedEducationalState, requiresConfirmation: true),
            .init(id: .openClosureStatePreview, title: "Closure state", systemImageName: "checkmark.circle", kind: .scriptedEducationalState, requiresConfirmation: true),
            .init(id: .restoreOriginal, title: "Restore", systemImageName: "arrow.counterclockwise", kind: .safety)
        ]
        return Dictionary(uniqueKeysWithValues: values.map { ($0.id, $0) })
    }()

    public static func availableTools(for state: ProcedureExperienceState) -> [ExperienceToolDescriptor] {
        let universal: [ExperienceToolID] = [.pointer, .orbit, .focus, .annotation, .restoreOriginal]
        var stepTools: [ExperienceToolID]

        switch state.currentStep {
        case .caseSelect:
            stepTools = []
        case .orientHead:
            stepTools = [.layerVisibility]
        case .explainStroke, .evtVascularPath:
            stepTools = [.layerVisibility, .vascularFlyThrough]
        case .evtOcclusion:
            stepTools = [.layerVisibility, .vascularFlyThrough]
        case .evtDeviceConcept:
            stepTools = [.deviceConceptPreview, .clotRemovalStatePreview]
        case .evtPostTreatmentComparison:
            stepTools = [.flowStateComparison]
        case .evtRecoveryOverview:
            stepTools = []
        case .openConfirmSite:
            stepTools = [.layerVisibility]
        case .openCranialAccess:
            stepTools = [.openAccessStatePreview]
        case .openDuralAccess:
            stepTools = [.openDuralStatePreview]
        case .openTreatReviewedCondition:
            stepTools = [.openConditionStatePreview]
        case .openReplaceAndFixBoneFlap:
            stepTools = [.openClosureStatePreview]
        case .openPostClosureReview:
            stepTools = [.openClosureStatePreview]
        }

        // Fail closed: ordinary EVT and overview can never surface an open-cranial tool.
        if state.currentStep.pathway != .openCranial
            || state.openCranialAuthorization?.isValidForOpenCranial != true {
            stepTools.removeAll { openCranialTools.contains($0) }
        }

        return (universal + stepTools).compactMap { descriptors[$0] }
    }

    public static func intent(
        for tool: ExperienceToolID,
        state: ProcedureExperienceState
    ) -> ExperienceToolIntent {
        let available = Set(availableTools(for: state).map(\.id))
        guard available.contains(tool) else { return .noOp }

        switch tool {
        case .pointer, .orbit, .focus:
            return .noOp
        case .annotation:
            return .toggleAnnotations
        case .layerVisibility:
            return .toggleLayerVisibility
        case .vascularFlyThrough:
            return .cameraPreset(.arteryLumenThreshold)
        case .deviceConceptPreview:
            return .procedureAction(.previewDeviceConcept)
        case .clotRemovalStatePreview:
            return .procedureAction(.previewClotRemovalState)
        case .flowStateComparison:
            return .procedureAction(.compareIllustrativeFlowStates)
        case .openAccessStatePreview:
            return .procedureAction(.revealCranialAccessLayer)
        case .openDuralStatePreview:
            return .procedureAction(.revealDuralAccessLayer)
        case .openConditionStatePreview:
            return .procedureAction(.previewReviewedConditionState)
        case .openClosureStatePreview:
            return .procedureAction(.previewClosureState)
        case .restoreOriginal:
            return .restoreOriginal
        }
    }

    public static let openCranialTools: Set<ExperienceToolID> = [
        .openAccessStatePreview,
        .openDuralStatePreview,
        .openConditionStatePreview,
        .openClosureStatePreview
    ]
}
