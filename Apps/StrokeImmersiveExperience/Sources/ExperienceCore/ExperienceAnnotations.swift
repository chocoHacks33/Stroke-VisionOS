import Foundation

public enum ExperienceNoteKind: String, Codable, Sendable, Hashable {
    case orientation
    case anatomy
    case flow
    case pathology
    case interventionConcept
    case disclosure
    case recovery
}

public enum ExperienceNoteFrameStyle: String, Codable, Sendable, Hashable {
    case compactCallout
    case guidedGlassCard
    case scholarPanel
}

public struct ExperienceNoteCopy: Codable, Sendable, Hashable {
    public let title: String
    public let body: String

    public init(title: String, body: String) {
        self.title = title
        self.body = body
    }
}

public struct ExperienceTieredCopy: Codable, Sendable, Hashable {
    public let minimal: ExperienceNoteCopy
    public let reduced80: ExperienceNoteCopy
    public let full: ExperienceNoteCopy

    public init(
        minimal: ExperienceNoteCopy,
        reduced80: ExperienceNoteCopy,
        full: ExperienceNoteCopy
    ) {
        self.minimal = minimal
        self.reduced80 = reduced80
        self.full = full
    }

    public subscript(tier: VisualDetailTier) -> ExperienceNoteCopy {
        switch tier {
        case .minimal: minimal
        case .reduced80: reduced80
        case .full: full
        }
    }
}

public struct ExperienceAnnotation: Codable, Sendable, Hashable, Identifiable {
    public let id: String
    public let steps: Set<ExperienceProcedureStep>
    public let anchorRequestID: String?
    public let kind: ExperienceNoteKind
    public let priority: Int
    public let copy: ExperienceTieredCopy
    public let requiresConceptualDisclosure: Bool

    public init(
        id: String,
        steps: Set<ExperienceProcedureStep>,
        anchorRequestID: String?,
        kind: ExperienceNoteKind,
        priority: Int,
        copy: ExperienceTieredCopy,
        requiresConceptualDisclosure: Bool = false
    ) {
        self.id = id
        self.steps = steps
        self.anchorRequestID = anchorRequestID
        self.kind = kind
        self.priority = priority
        self.copy = copy
        self.requiresConceptualDisclosure = requiresConceptualDisclosure
    }
}

public struct ResolvedExperienceAnnotation: Sendable, Hashable, Identifiable {
    public let annotation: ExperienceAnnotation
    public let displayCopy: ExperienceNoteCopy

    public var id: String { annotation.id }
}

public struct ExperienceNotePresentationProfile: Sendable, Hashable {
    public let maximumVisibleNotes: Int
    public let maximumBodyLines: Int
    public let frameStyle: ExperienceNoteFrameStyle
    public let technicalTermsNeedInlineExplanation: Bool

    public init(
        maximumVisibleNotes: Int,
        maximumBodyLines: Int,
        frameStyle: ExperienceNoteFrameStyle,
        technicalTermsNeedInlineExplanation: Bool
    ) {
        self.maximumVisibleNotes = maximumVisibleNotes
        self.maximumBodyLines = maximumBodyLines
        self.frameStyle = frameStyle
        self.technicalTermsNeedInlineExplanation = technicalTermsNeedInlineExplanation
    }

    public static func profile(for tier: VisualDetailTier) -> Self {
        switch tier {
        case .minimal:
            .init(maximumVisibleNotes: 2, maximumBodyLines: 2,
                  frameStyle: .compactCallout, technicalTermsNeedInlineExplanation: true)
        case .reduced80:
            .init(maximumVisibleNotes: 4, maximumBodyLines: 4,
                  frameStyle: .guidedGlassCard, technicalTermsNeedInlineExplanation: true)
        case .full:
            .init(maximumVisibleNotes: 7, maximumBodyLines: 7,
                  frameStyle: .scholarPanel, technicalTermsNeedInlineExplanation: false)
        }
    }
}

public enum ExperienceAnnotationAuthorization: String, Codable, Sendable, Hashable {
    case suppressed
    /// Allows local placeholder frames in an explicitly labelled engineering build only.
    case developerPreviewPlaceholders
}

public struct ExperienceAnnotationCatalog: Sendable {
    public let annotations: [ExperienceAnnotation]

    public init(annotations: [ExperienceAnnotation] = Self.builtInAnnotations) {
        self.annotations = annotations
    }

    public func notes(
        for step: ExperienceProcedureStep,
        tier: VisualDetailTier,
        authorization: ExperienceAnnotationAuthorization = .suppressed
    ) -> [ResolvedExperienceAnnotation] {
        guard authorization == .developerPreviewPlaceholders else { return [] }
        let profile = ExperienceNotePresentationProfile.profile(for: tier)
        return annotations
            .filter { $0.steps.contains(step) }
            .sorted {
                if $0.priority == $1.priority { return $0.id < $1.id }
                return $0.priority > $1.priority
            }
            .prefix(profile.maximumVisibleNotes)
            .map { ResolvedExperienceAnnotation(annotation: $0, displayCopy: $0.copy[tier]) }
    }

    public static let builtInAnnotations: [ExperienceAnnotation] = [
        annotation(
            "generic_model_disclosure",
            steps: Set(ExperienceProcedureStep.allCases),
            anchor: nil,
            kind: .disclosure,
            priority: 100,
            minimal: ("Educational view", "Generic model — not personal medical guidance."),
            reduced: ("Educational model", "This is generic anatomy for a guided conversation, not a patient-specific plan."),
            full: ("Generic educational model", "Illustrative anatomy, scale, flow, devices, and state changes are not patient-specific and must not be used for planning, training, or outcome prediction.")
        ),
        annotation(
            "brain_orientation",
            steps: [.orientHead, .openConfirmSite],
            anchor: nil,
            kind: .orientation,
            priority: 90,
            minimal: ("Find your bearings", "Front, back, left, and right stay visible."),
            reduced: ("Orient the head", "Use the fixed direction markers before exploring deeper layers."),
            full: ("Orientation reference", "Maintain the generic model's laterality and orientation markers through every layer or camera transition.")
        ),
        annotation(
            "arterial_tree",
            steps: [.explainStroke, .evtVascularPath],
            anchor: nil,
            kind: .anatomy,
            priority: 85,
            minimal: ("Blood route", "The highlighted path carries blood toward the brain."),
            reduced: ("Arterial route", "The highlight traces one illustrative route from the neck toward the selected brain vessel."),
            full: ("Illustrative arterial pathway", "The selected origin-to-focus route is emphasized while unrelated branches are suppressed. Direction and laterality remain visible.")
        ),
        annotation(
            "qualitative_flow",
            steps: [.explainStroke, .evtVascularPath, .evtPostTreatmentComparison],
            anchor: nil,
            kind: .flow,
            priority: 80,
            minimal: ("Flow cue", "Moving dots show direction only."),
            reduced: ("Illustrative blood flow", "Particles show a simplified direction of travel, not measured speed or pressure."),
            full: ("Qualitative flow disclosure", "Particle density, color, and motion are explanatory cues only; they do not encode patient flow rate, pressure, perfusion, or treatment result.")
        ),
        annotation(
            "occlusion_focus",
            steps: [.explainStroke, .evtOcclusion],
            anchor: nil,
            kind: .pathology,
            priority: 88,
            minimal: ("Blocked area", "The bright marker shows the teaching focus."),
            reduced: ("Illustrative occlusion", "The marker identifies a generic vessel blockage and its affected route."),
            full: ("Generic occlusion focus", "The clot and vessel relationship is conceptual, nonquantitative, and not derived from patient imaging. Affected-tissue cues remain illustrative.")
        ),
        annotation(
            "device_preview",
            steps: [.evtDeviceConcept],
            anchor: nil,
            kind: .interventionConcept,
            priority: 86,
            minimal: ("Treatment idea", "Watch a short, non-graphic before-and-after preview."),
            reduced: ("Device concept", "A pre-authored developer-preview animation shows the idea of reaching and removing a clot. It is not a how-to."),
            full: ("Scripted device concept", "Only the catalogued pre-authored developer-preview state may play. Scale and motion are conceptual; free manipulation, force simulation, procedural parameters, and operational guidance are disabled.")
        ),
        annotation(
            "flow_comparison",
            steps: [.evtPostTreatmentComparison],
            anchor: nil,
            kind: .flow,
            priority: 86,
            minimal: ("Compare", "Switch between two illustrative states."),
            reduced: ("Before and after", "Compare a blocked teaching state with an illustrative restored-flow state."),
            full: ("Illustrative state comparison", "This comparison explains a treatment concept only. It is not evidence of reperfusion, clinical success, recovery, or an expected patient outcome.")
        ),
        annotation(
            "recovery_context",
            steps: [.evtRecoveryOverview, .openPostClosureReview],
            anchor: nil,
            kind: .recovery,
            priority: 82,
            minimal: ("After care", "Recovery and monitoring continue after treatment."),
            reduced: ("Recovery context", "The care team continues observation, communication, and rehabilitation planning."),
            full: ("Post-treatment context", "The scene introduces generic monitoring and rehabilitation context without predicting an individual timeline, function, complication risk, or outcome.")
        ),
        annotation(
            "open_branch_warning",
            steps: [.openConfirmSite, .openCranialAccess, .openDuralAccess,
                    .openTreatReviewedCondition, .openReplaceAndFixBoneFlap, .openPostClosureReview],
            anchor: nil,
            kind: .disclosure,
            priority: 99,
            minimal: ("Separate pathway", "Non-graphic, clinician-guided open-surgery overview."),
            reduced: ("Open-surgery developer preview", "This separately selected pathway uses non-graphic layer swaps, not realistic cutting."),
            full: ("Clinician-facilitated developer-preview branch", "This branch is separate from routine endovascular thrombectomy. It uses catalogued non-graphic visibility states only and provides no operative sequence, tissue mechanics, or surgical instruction.")
        ),
        annotation(
            "open_access_layer",
            steps: [.openCranialAccess],
            anchor: nil,
            kind: .interventionConcept,
            priority: 84,
            minimal: ("Outer layer", "Reveal a simplified access state."),
            reduced: ("Cranial access concept", "A calm dissolve reveals the catalogued developer-preview skull-access layer."),
            full: ("Developer-preview cranial-access state", "The pre-authored state is revealed as a reversible layer change. There is no incision path, drilling interaction, force model, tissue response, or technique instruction.")
        ),
        annotation(
            "open_dural_layer",
            steps: [.openDuralAccess],
            anchor: nil,
            kind: .interventionConcept,
            priority: 84,
            minimal: ("Protective layer", "Reveal the simplified covering."),
            reduced: ("Protective covering", "A non-graphic state change identifies the dura around the brain."),
            full: ("Developer-preview dural-access state", "A reversible visibility swap identifies the protective covering. The presentation omits cutting, deformation, bleeding, force, and procedural technique.")
        ),
        annotation(
            "open_condition",
            steps: [.openTreatReviewedCondition],
            anchor: nil,
            kind: .pathology,
            priority: 84,
            minimal: ("Treatment focus", "See a simplified condition state."),
            reduced: ("Developer-preview treatment concept", "The focus changes between pre-authored teaching states."),
            full: ("Conceptual treatment-state preview", "This noninteractive state swap explains the selected complication at a high level. It does not demonstrate manipulation, evacuation, hemostasis, tissue handling, or operative decisions.")
        ),
        annotation(
            "open_closure",
            steps: [.openReplaceAndFixBoneFlap],
            anchor: nil,
            kind: .interventionConcept,
            priority: 84,
            minimal: ("Closure", "Return the layers to the catalogued developer-preview closure view."),
            reduced: ("Closure concept", "A pre-authored state shows the covering and bone flap returned."),
            full: ("Developer-preview closure comparison", "The host app may reveal only the catalogued closed state for this craniotomy scenario. It must not be reused for decompressive craniectomy and is not a suturing or fixation simulation.")
        )
    ]

    private static func annotation(
        _ id: String,
        steps: Set<ExperienceProcedureStep>,
        anchor: String?,
        kind: ExperienceNoteKind,
        priority: Int,
        minimal: (String, String),
        reduced: (String, String),
        full: (String, String)
    ) -> ExperienceAnnotation {
        ExperienceAnnotation(
            id: id,
            steps: steps,
            anchorRequestID: anchor,
            kind: kind,
            priority: priority,
            copy: .init(
                minimal: .init(title: minimal.0, body: minimal.1),
                reduced80: .init(title: reduced.0, body: reduced.1),
                full: .init(title: full.0, body: full.1)
            ),
            requiresConceptualDisclosure: kind == .flow || kind == .interventionConcept || kind == .pathology
        )
    }
}
