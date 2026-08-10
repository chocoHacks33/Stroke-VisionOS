import Foundation

/// Semantic UI events understood by the project-owned feedback pack.
///
/// These cases intentionally exclude raw gaze, continuous head/hand motion,
/// anatomy movement, and clinical/patient state.
enum InteractionFeedbackEvent: String, CaseIterable, Sendable {
    case deliberateFocusEntry
    case controlCommit
    case confirmedStateChange
    case navigateBack
    case actionRequiresAttention
    case majorViewTransition
    case restoreComplete
}

/// An optional semantic request for a future supported companion/accessory.
///
/// This is not a visionOS headset-haptic API. Integration must default off,
/// require explicit user opt-in, and test actual adapter capability at runtime.
enum OptionalExternalHapticIntent: String, Sendable {
    case lightSelectionTransient
    case softConfirmationTransient
    case lightNavigationTransient
    case attentionTransient
}

struct InteractionFeedbackRecipe: Equatable, Sendable {
    let event: InteractionFeedbackEvent
    let resourceName: String
    let resourceExtension: String
    let defaultEnabled: Bool
    let gainTrimDecibels: Float
    let cooldown: Duration
    let priority: Int
    let interruptsLowerPriority: Bool
    let optionalExternalHapticIntent: OptionalExternalHapticIntent?

    /// Earcons are UI-owned and should not be attached to RealityKit anatomy.
    let usesSpatialAudio = false
}

enum InteractionFeedbackRecipes {
    /// Conservative initial master gain; the user-facing setting remains
    /// authoritative and must allow complete muting.
    static let defaultMasterGain: Float = 0.35
    static let maximumSimultaneousEarcons = 2

    static let all: [InteractionFeedbackRecipe] = [
        .init(
            event: .deliberateFocusEntry,
            resourceName: "focus",
            resourceExtension: "wav",
            defaultEnabled: false,
            gainTrimDecibels: -3,
            cooldown: .milliseconds(500),
            priority: 10,
            interruptsLowerPriority: false,
            optionalExternalHapticIntent: nil
        ),
        .init(
            event: .controlCommit,
            resourceName: "selection",
            resourceExtension: "wav",
            defaultEnabled: true,
            gainTrimDecibels: -3,
            cooldown: .milliseconds(90),
            priority: 30,
            interruptsLowerPriority: false,
            optionalExternalHapticIntent: .lightSelectionTransient
        ),
        .init(
            event: .confirmedStateChange,
            resourceName: "confirm",
            resourceExtension: "wav",
            defaultEnabled: true,
            gainTrimDecibels: -4,
            cooldown: .milliseconds(250),
            priority: 50,
            interruptsLowerPriority: true,
            optionalExternalHapticIntent: .softConfirmationTransient
        ),
        .init(
            event: .navigateBack,
            resourceName: "back",
            resourceExtension: "wav",
            defaultEnabled: true,
            gainTrimDecibels: -3,
            cooldown: .milliseconds(160),
            priority: 25,
            interruptsLowerPriority: false,
            optionalExternalHapticIntent: .lightNavigationTransient
        ),
        .init(
            event: .actionRequiresAttention,
            resourceName: "warning",
            resourceExtension: "wav",
            defaultEnabled: true,
            gainTrimDecibels: -5,
            cooldown: .seconds(1),
            priority: 80,
            interruptsLowerPriority: true,
            optionalExternalHapticIntent: .attentionTransient
        ),
        .init(
            event: .majorViewTransition,
            resourceName: "transition",
            resourceExtension: "wav",
            defaultEnabled: true,
            gainTrimDecibels: -5,
            cooldown: .milliseconds(600),
            priority: 20,
            interruptsLowerPriority: false,
            optionalExternalHapticIntent: nil
        ),
        .init(
            event: .restoreComplete,
            resourceName: "restore",
            resourceExtension: "wav",
            defaultEnabled: true,
            gainTrimDecibels: -4,
            cooldown: .milliseconds(500),
            priority: 45,
            interruptsLowerPriority: true,
            optionalExternalHapticIntent: .softConfirmationTransient
        )
    ]

    static func recipe(for event: InteractionFeedbackEvent) -> InteractionFeedbackRecipe {
        guard let recipe = all.first(where: { $0.event == event }) else {
            preconditionFailure("Every declared feedback event must have exactly one recipe")
        }
        return recipe
    }
}

/// Optional background texture with controls independent from earcon volume.
///
/// Ambience is a user preference, is off by default, and must not be driven by
/// an inferred emotional/anxiety state or described as treatment.
struct InteractionAmbienceRecipe: Equatable, Sendable {
    let resourceName: String
    let resourceExtension: String
    let defaultEnabled: Bool
    let defaultGain: Float
    let maximumGain: Float
    let fadeIn: Duration
    let fadeOut: Duration
    let duckUnderWarningDecibels: Float
    let loopsSeamlessly: Bool
    let usesIndependentVolumeControl: Bool

    /// A diffuse UI background must not move with or localize to anatomy.
    let isDiffuseNonDirectional = true
    let attachesToAnatomy = false
    let carriesTherapeuticClaim = false
}

enum InteractionAmbienceRecipes {
    static let softWaterRain = InteractionAmbienceRecipe(
        resourceName: "soft_water_rain_loop",
        resourceExtension: "wav",
        defaultEnabled: false,
        defaultGain: 0.25,
        maximumGain: 0.5,
        fadeIn: .milliseconds(1_500),
        fadeOut: .seconds(1),
        duckUnderWarningDecibels: -6,
        loopsSeamlessly: true,
        usesIndependentVolumeControl: true
    )
}

/// Integration boundary for optional companion haptics.
///
/// Implementations must never assume availability from platform or device type.
protocol ExternalHapticFeedbackAdapter: Sendable {
    var isAvailable: Bool { get async }
    func emit(_ intent: OptionalExternalHapticIntent) async throws
}
