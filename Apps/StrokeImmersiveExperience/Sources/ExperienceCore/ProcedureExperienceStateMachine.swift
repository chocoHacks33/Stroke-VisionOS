import Foundation

public enum ExperienceAudience: String, Codable, Sendable, Hashable {
    case patient
    case family
    case clinicianFacilitated
    case developer
}

public enum ExperiencePathwayID: String, Codable, Sendable, Hashable {
    case overview = "OVERVIEW"
    case endovascular = "EVT"
    case openCranial = "OPEN_CRANIOTOMY"
}

public enum ExperienceProcedureStep: String, CaseIterable, Codable, Sendable, Hashable {
    case caseSelect = "CASE_SELECT"
    case orientHead = "ORIENT_HEAD"
    case explainStroke = "EXPLAIN_STROKE"

    case evtVascularPath = "EVT_REVIEW_VASCULAR_PATH"
    case evtOcclusion = "EVT_REVIEW_OCCLUSION"
    case evtDeviceConcept = "EVT_REVIEW_CONDITIONAL_DEVICE_CONCEPT"
    case evtPostTreatmentComparison = "EVT_REVIEW_POST_TREATMENT_COMPARISON"
    case evtRecoveryOverview = "EVT_RECOVERY_OVERVIEW"

    case openConfirmSite = "OPEN_CONFIRM_SITE"
    case openCranialAccess = "OPEN_ESTABLISH_CRANIAL_ACCESS"
    case openDuralAccess = "OPEN_ESTABLISH_DURAL_ACCESS"
    case openTreatReviewedCondition = "OPEN_TREAT_REVIEWED_CONDITION"
    case openReplaceAndFixBoneFlap = "OPEN_REPLACE_AND_FIX_BONE_FLAP"
    case openPostClosureReview = "OPEN_POST_CLOSURE_REVIEW"

    public var pathway: ExperiencePathwayID {
        switch self {
        case .caseSelect, .orientHead, .explainStroke:
            .overview
        case .evtVascularPath, .evtOcclusion, .evtDeviceConcept,
             .evtPostTreatmentComparison, .evtRecoveryOverview:
            .endovascular
        case .openConfirmSite, .openCranialAccess, .openDuralAccess,
             .openTreatReviewedCondition, .openReplaceAndFixBoneFlap,
             .openPostClosureReview:
            .openCranial
        }
    }
}

public enum ExperienceProcedureAction: String, CaseIterable, Codable, Sendable, Hashable {
    case inspectOrientation
    case inspectVascularPath
    case focusOcclusion
    case previewDeviceConcept
    case previewClotRemovalState
    case compareIllustrativeFlowStates
    case revealCranialAccessLayer
    case revealDuralAccessLayer
    case previewReviewedConditionState
    case previewClosureState
    case compareClosureStates
    case inspectRecoveryContext
}

/// Evidence that the separately reviewed, non-graphic open-cranial branch was deliberately chosen.
/// The app must create this only after its clinician-facilitated gate is completed.
public struct ReviewedPathwayAuthorization: Codable, Sendable, Hashable {
    public let pathway: ExperiencePathwayID
    public let reviewedScenarioID: String
    public let reviewedContentRevision: String
    public let audience: ExperienceAudience

    public init(
        pathway: ExperiencePathwayID,
        reviewedScenarioID: String,
        reviewedContentRevision: String,
        audience: ExperienceAudience
    ) {
        self.pathway = pathway
        self.reviewedScenarioID = reviewedScenarioID
        self.reviewedContentRevision = reviewedContentRevision
        self.audience = audience
    }

    public var isValidForOpenCranial: Bool {
        pathway == .openCranial
            && !reviewedScenarioID.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            && !reviewedContentRevision.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            && (audience == .clinicianFacilitated || audience == .developer)
    }
}

public struct ProcedureExperienceState: Codable, Sendable, Hashable {
    public var audience: ExperienceAudience
    public var selectedPathway: ExperiencePathwayID
    public var currentStep: ExperienceProcedureStep
    public var detailTier: VisualDetailTier
    public var isPaused: Bool
    public var completedActions: Set<ExperienceProcedureAction>
    public var openCranialAuthorization: ReviewedPathwayAuthorization?

    public init(
        audience: ExperienceAudience,
        selectedPathway: ExperiencePathwayID = .overview,
        currentStep: ExperienceProcedureStep = .caseSelect,
        detailTier: VisualDetailTier = .minimal,
        isPaused: Bool = false,
        completedActions: Set<ExperienceProcedureAction> = [],
        openCranialAuthorization: ReviewedPathwayAuthorization? = nil
    ) {
        self.audience = audience
        self.selectedPathway = selectedPathway
        self.currentStep = currentStep
        self.detailTier = detailTier
        self.isPaused = isPaused
        self.completedActions = completedActions
        self.openCranialAuthorization = openCranialAuthorization
    }
}

public enum ProcedureExperienceError: Error, LocalizedError, Sendable, Equatable {
    case invalidTransition(from: ExperienceProcedureStep, to: ExperienceProcedureStep)
    case pathwayNotSelected
    case reviewedAuthorizationRequired
    case authorizationMismatch
    case actionUnavailable(action: ExperienceProcedureAction, step: ExperienceProcedureStep)

    public var errorDescription: String? {
        switch self {
        case .invalidTransition(let from, let to):
            "Transition from \(from.rawValue) to \(to.rawValue) is unavailable."
        case .pathwayNotSelected:
            "Select a catalogued developer-preview pathway before continuing."
        case .reviewedAuthorizationRequired:
            "The open-cranial developer-preview branch requires an explicit clinician/developer gate."
        case .authorizationMismatch:
            "The authorization does not match the requested pathway or audience."
        case .actionUnavailable(let action, let step):
            "Action \(action.rawValue) is unavailable in \(step.rawValue)."
        }
    }
}

/// Explicit, user-paced lesson navigation. There is intentionally no timer or auto-advance path.
public struct ProcedureExperienceStateMachine: Sendable {
    public private(set) var state: ProcedureExperienceState

    public init(audience: ExperienceAudience, initialTier: VisualDetailTier = .minimal) {
        state = ProcedureExperienceState(audience: audience, detailTier: initialTier)
    }

    public mutating func setDetailTier(_ tier: VisualDetailTier) {
        state.detailTier = tier
    }

    public mutating func beginEndovascularEducationalPathway() {
        state.selectedPathway = .endovascular
        state.currentStep = .orientHead
        state.openCranialAuthorization = nil
        state.completedActions.removeAll()
        state.isPaused = false
    }

    public mutating func beginOpenCranialEducationalPathway(
        authorization: ReviewedPathwayAuthorization
    ) throws {
        guard authorization.isValidForOpenCranial else {
            throw ProcedureExperienceError.reviewedAuthorizationRequired
        }
        guard authorization.audience == state.audience else {
            throw ProcedureExperienceError.authorizationMismatch
        }
        state.selectedPathway = .openCranial
        state.currentStep = .openConfirmSite
        state.openCranialAuthorization = authorization
        state.completedActions.removeAll()
        state.isPaused = false
    }

    public mutating func next() throws {
        let nextStep: ExperienceProcedureStep?
        switch state.currentStep {
        case .caseSelect:
            nextStep = .orientHead
        case .orientHead:
            nextStep = .explainStroke
        case .explainStroke:
            switch state.selectedPathway {
            case .endovascular: nextStep = .evtVascularPath
            case .openCranial:
                guard state.openCranialAuthorization?.isValidForOpenCranial == true else {
                    throw ProcedureExperienceError.reviewedAuthorizationRequired
                }
                nextStep = .openConfirmSite
            case .overview:
                throw ProcedureExperienceError.pathwayNotSelected
            }
        case .evtVascularPath: nextStep = .evtOcclusion
        case .evtOcclusion: nextStep = .evtDeviceConcept
        case .evtDeviceConcept: nextStep = .evtPostTreatmentComparison
        case .evtPostTreatmentComparison: nextStep = .evtRecoveryOverview
        case .evtRecoveryOverview: nextStep = nil
        case .openConfirmSite: nextStep = .openCranialAccess
        case .openCranialAccess: nextStep = .openDuralAccess
        case .openDuralAccess: nextStep = .openTreatReviewedCondition
        case .openTreatReviewedCondition: nextStep = .openReplaceAndFixBoneFlap
        case .openReplaceAndFixBoneFlap: nextStep = .openPostClosureReview
        case .openPostClosureReview: nextStep = nil
        }

        guard let nextStep else { return }
        try move(to: nextStep)
    }

    public mutating func previous() throws {
        let previousStep: ExperienceProcedureStep?
        switch state.currentStep {
        case .caseSelect: previousStep = nil
        case .orientHead: previousStep = .caseSelect
        case .explainStroke: previousStep = .orientHead
        case .evtVascularPath: previousStep = .explainStroke
        case .evtOcclusion: previousStep = .evtVascularPath
        case .evtDeviceConcept: previousStep = .evtOcclusion
        case .evtPostTreatmentComparison: previousStep = .evtDeviceConcept
        case .evtRecoveryOverview: previousStep = .evtPostTreatmentComparison
        case .openConfirmSite: previousStep = .explainStroke
        case .openCranialAccess: previousStep = .openConfirmSite
        case .openDuralAccess: previousStep = .openCranialAccess
        case .openTreatReviewedCondition: previousStep = .openDuralAccess
        case .openReplaceAndFixBoneFlap: previousStep = .openTreatReviewedCondition
        case .openPostClosureReview: previousStep = .openReplaceAndFixBoneFlap
        }

        guard let previousStep else { return }
        try move(to: previousStep)
    }

    public mutating func pause() {
        state.isPaused = true
    }

    public mutating func resume() {
        state.isPaused = false
    }

    public mutating func restoreOverview() {
        let audience = state.audience
        let tier = state.detailTier
        state = ProcedureExperienceState(audience: audience, detailTier: tier)
    }

    public mutating func perform(_ action: ExperienceProcedureAction) throws {
        guard Self.allowedActions[state.currentStep, default: []].contains(action) else {
            throw ProcedureExperienceError.actionUnavailable(action: action, step: state.currentStep)
        }
        state.completedActions.insert(action)
    }

    public func progress() -> (current: Int, total: Int) {
        let sequence = Self.sequence(for: state.selectedPathway)
        guard let index = sequence.firstIndex(of: state.currentStep) else { return (0, sequence.count) }
        return (index + 1, sequence.count)
    }

    public static func sequence(for pathway: ExperiencePathwayID) -> [ExperienceProcedureStep] {
        switch pathway {
        case .overview:
            [.caseSelect, .orientHead, .explainStroke]
        case .endovascular:
            [.orientHead, .explainStroke, .evtVascularPath, .evtOcclusion,
             .evtDeviceConcept, .evtPostTreatmentComparison, .evtRecoveryOverview]
        case .openCranial:
            [.openConfirmSite, .openCranialAccess, .openDuralAccess,
             .openTreatReviewedCondition, .openReplaceAndFixBoneFlap, .openPostClosureReview]
        }
    }

    public static let allowedActions: [ExperienceProcedureStep: Set<ExperienceProcedureAction>] = [
        .orientHead: [.inspectOrientation],
        .explainStroke: [.inspectVascularPath, .focusOcclusion],
        .evtVascularPath: [.inspectVascularPath],
        .evtOcclusion: [.focusOcclusion],
        .evtDeviceConcept: [.previewDeviceConcept, .previewClotRemovalState],
        .evtPostTreatmentComparison: [.compareIllustrativeFlowStates],
        .evtRecoveryOverview: [.inspectRecoveryContext],
        .openConfirmSite: [.inspectOrientation],
        .openCranialAccess: [.revealCranialAccessLayer],
        .openDuralAccess: [.revealDuralAccessLayer],
        .openTreatReviewedCondition: [.previewReviewedConditionState],
        .openReplaceAndFixBoneFlap: [.previewClosureState],
        .openPostClosureReview: [.compareClosureStates, .inspectRecoveryContext]
    ]

    private mutating func move(to destination: ExperienceProcedureStep) throws {
        let sequence = Self.sequence(for: state.selectedPathway)
        let fromIndex = sequence.firstIndex(of: state.currentStep)
        let toIndex = sequence.firstIndex(of: destination)
        guard let fromIndex, let toIndex, abs(fromIndex - toIndex) == 1 else {
            throw ProcedureExperienceError.invalidTransition(from: state.currentStep, to: destination)
        }
        if destination.pathway == .openCranial,
           state.openCranialAuthorization?.isValidForOpenCranial != true {
            throw ProcedureExperienceError.reviewedAuthorizationRequired
        }
        state.currentStep = destination
        state.isPaused = false
    }
}
