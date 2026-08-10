import Foundation

public struct ExperienceVector3: Codable, Sendable, Hashable {
    public var x: Double
    public var y: Double
    public var z: Double

    public init(x: Double, y: Double, z: Double) {
        self.x = x
        self.y = y
        self.z = z
    }
}

public enum ExperienceCameraPresetID: String, CaseIterable, Codable, Sendable, Hashable {
    case consultationOverview
    case headOrientation
    case transparentHead
    case vascularRoute
    case occlusionCloseup
    case deviceConcept
    case illustrativeFlowComparison
    case arteryLumenThreshold
    case arteryLumenConcept
    case microcirculationConcept
    case openAccessOverview
    case openLayerFocus
    case closureComparison
    case recoveryOverview
}

public enum ExperienceCameraTransitionStyle: String, Codable, Sendable, Hashable {
    case dissolve
    case easeInOut
    case userConfirmedFlyThrough
    case immediateRestore
}

/// Normalized scene-space camera target. The host app owns final calibration and comfort bounds.
public struct ExperienceCameraPreset: Codable, Sendable, Hashable, Identifiable {
    public let id: ExperienceCameraPresetID
    public let position: ExperienceVector3
    public let lookAt: ExperienceVector3
    public let fieldOfViewDegrees: Double
    public let minimumDistance: Double
    public let maximumDistance: Double
    public let transitionDurationSeconds: Double
    public let transitionStyle: ExperienceCameraTransitionStyle
    public let conceptualScaleDisclosureRequired: Bool

    public init(
        id: ExperienceCameraPresetID,
        position: ExperienceVector3,
        lookAt: ExperienceVector3,
        fieldOfViewDegrees: Double,
        minimumDistance: Double,
        maximumDistance: Double,
        transitionDurationSeconds: Double,
        transitionStyle: ExperienceCameraTransitionStyle,
        conceptualScaleDisclosureRequired: Bool = false
    ) {
        self.id = id
        self.position = position
        self.lookAt = lookAt
        self.fieldOfViewDegrees = fieldOfViewDegrees
        self.minimumDistance = minimumDistance
        self.maximumDistance = maximumDistance
        self.transitionDurationSeconds = transitionDurationSeconds
        self.transitionStyle = transitionStyle
        self.conceptualScaleDisclosureRequired = conceptualScaleDisclosureRequired
    }
}

public enum ExperienceCameraPresetLibrary {
    public static let all: [ExperienceCameraPresetID: ExperienceCameraPreset] = {
        let origin = ExperienceVector3(x: 0, y: 1.45, z: 0)
        let values: [ExperienceCameraPreset] = [
            .init(id: .consultationOverview, position: .init(x: 0, y: 1.5, z: 2.2), lookAt: origin,
                  fieldOfViewDegrees: 48, minimumDistance: 1.2, maximumDistance: 3.0,
                  transitionDurationSeconds: 0.8, transitionStyle: .dissolve),
            .init(id: .headOrientation, position: .init(x: 0.15, y: 1.48, z: 1.15), lookAt: origin,
                  fieldOfViewDegrees: 44, minimumDistance: 0.65, maximumDistance: 1.8,
                  transitionDurationSeconds: 0.8, transitionStyle: .easeInOut),
            .init(id: .transparentHead, position: .init(x: 0.2, y: 1.5, z: 0.95), lookAt: origin,
                  fieldOfViewDegrees: 42, minimumDistance: 0.55, maximumDistance: 1.5,
                  transitionDurationSeconds: 0.7, transitionStyle: .easeInOut),
            .init(id: .vascularRoute, position: .init(x: -0.2, y: 1.42, z: 0.78), lookAt: origin,
                  fieldOfViewDegrees: 40, minimumDistance: 0.38, maximumDistance: 1.2,
                  transitionDurationSeconds: 1.0, transitionStyle: .easeInOut),
            .init(id: .occlusionCloseup, position: .init(x: -0.14, y: 1.53, z: 0.43), lookAt: origin,
                  fieldOfViewDegrees: 36, minimumDistance: 0.24, maximumDistance: 0.8,
                  transitionDurationSeconds: 0.9, transitionStyle: .easeInOut),
            .init(id: .deviceConcept, position: .init(x: -0.1, y: 1.52, z: 0.36), lookAt: origin,
                  fieldOfViewDegrees: 34, minimumDistance: 0.22, maximumDistance: 0.72,
                  transitionDurationSeconds: 0.8, transitionStyle: .easeInOut,
                  conceptualScaleDisclosureRequired: true),
            .init(id: .illustrativeFlowComparison, position: .init(x: 0.05, y: 1.48, z: 0.7), lookAt: origin,
                  fieldOfViewDegrees: 42, minimumDistance: 0.4, maximumDistance: 1.1,
                  transitionDurationSeconds: 0.8, transitionStyle: .dissolve),
            .init(id: .arteryLumenThreshold, position: .init(x: 0, y: 1.47, z: 0.28), lookAt: origin,
                  fieldOfViewDegrees: 50, minimumDistance: 0.18, maximumDistance: 0.5,
                  transitionDurationSeconds: 1.2, transitionStyle: .userConfirmedFlyThrough,
                  conceptualScaleDisclosureRequired: true),
            .init(id: .arteryLumenConcept, position: .init(x: 0, y: 1.47, z: 0.08), lookAt: origin,
                  fieldOfViewDegrees: 58, minimumDistance: 0.04, maximumDistance: 0.3,
                  transitionDurationSeconds: 1.4, transitionStyle: .userConfirmedFlyThrough,
                  conceptualScaleDisclosureRequired: true),
            .init(id: .microcirculationConcept, position: .init(x: 0.02, y: 1.47, z: 0.03), lookAt: origin,
                  fieldOfViewDegrees: 60, minimumDistance: 0.03, maximumDistance: 0.2,
                  transitionDurationSeconds: 1.2, transitionStyle: .dissolve,
                  conceptualScaleDisclosureRequired: true),
            .init(id: .openAccessOverview, position: .init(x: 0.25, y: 1.58, z: 0.8), lookAt: origin,
                  fieldOfViewDegrees: 42, minimumDistance: 0.45, maximumDistance: 1.2,
                  transitionDurationSeconds: 0.8, transitionStyle: .easeInOut),
            .init(id: .openLayerFocus, position: .init(x: 0.18, y: 1.6, z: 0.48), lookAt: origin,
                  fieldOfViewDegrees: 38, minimumDistance: 0.28, maximumDistance: 0.85,
                  transitionDurationSeconds: 0.8, transitionStyle: .dissolve,
                  conceptualScaleDisclosureRequired: true),
            .init(id: .closureComparison, position: .init(x: 0.2, y: 1.56, z: 0.72), lookAt: origin,
                  fieldOfViewDegrees: 40, minimumDistance: 0.42, maximumDistance: 1.0,
                  transitionDurationSeconds: 0.8, transitionStyle: .dissolve),
            .init(id: .recoveryOverview, position: .init(x: 0, y: 1.48, z: 1.3), lookAt: origin,
                  fieldOfViewDegrees: 46, minimumDistance: 0.8, maximumDistance: 2.0,
                  transitionDurationSeconds: 0.9, transitionStyle: .easeInOut)
        ]
        return Dictionary(uniqueKeysWithValues: values.map { ($0.id, $0) })
    }()

    public static let defaultForStep: [ExperienceProcedureStep: ExperienceCameraPresetID] = [
        .caseSelect: .consultationOverview,
        .orientHead: .headOrientation,
        .explainStroke: .transparentHead,
        .evtVascularPath: .vascularRoute,
        .evtOcclusion: .occlusionCloseup,
        .evtDeviceConcept: .deviceConcept,
        .evtPostTreatmentComparison: .illustrativeFlowComparison,
        .evtRecoveryOverview: .recoveryOverview,
        .openConfirmSite: .openAccessOverview,
        .openCranialAccess: .openLayerFocus,
        .openDuralAccess: .openLayerFocus,
        .openTreatReviewedCondition: .openLayerFocus,
        .openReplaceAndFixBoneFlap: .closureComparison,
        .openPostClosureReview: .recoveryOverview
    ]

    /// Optional, user-confirmed conceptual fly-through. It is never an anatomical navigation claim.
    public static let vascularFlyThrough: [ExperienceCameraPresetID] = [
        .vascularRoute,
        .occlusionCloseup,
        .arteryLumenThreshold,
        .arteryLumenConcept,
        .microcirculationConcept
    ]
}
