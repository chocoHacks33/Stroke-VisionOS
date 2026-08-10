import Foundation

/// A user-selected visual-detail level. This is deliberately not an anxiety diagnosis.
public enum VisualDetailTier: String, CaseIterable, Codable, Sendable, Hashable {
    case minimal
    case reduced80
    case full

    public var normalizedDetailAmount: Double {
        switch self {
        case .minimal: 0.25
        case .reduced80: 0.80
        case .full: 1.00
        }
    }

    public var accessibilityLabel: String {
        switch self {
        case .minimal: "Minimal visual detail"
        case .reduced80: "Reduced visual detail"
        case .full: "Full visual detail"
        }
    }
}

/// Converts an explicit 0...1 detail slider into a stable tier while preventing rapid
/// asset swaps near a boundary. No gaze, pupil, motion, or other biometric input belongs here.
public struct VisualDetailTierSelector: Sendable, Hashable {
    public struct Thresholds: Sendable, Hashable {
        public var enterReduced: Double
        public var leaveReduced: Double
        public var enterFull: Double
        public var leaveFull: Double

        public init(
            enterReduced: Double = 0.40,
            leaveReduced: Double = 0.28,
            enterFull: Double = 0.90,
            leaveFull: Double = 0.82
        ) {
            self.enterReduced = enterReduced
            self.leaveReduced = leaveReduced
            self.enterFull = enterFull
            self.leaveFull = leaveFull
        }
    }

    public var thresholds: Thresholds

    public init(thresholds: Thresholds = .init()) {
        self.thresholds = thresholds
    }

    public func select(detailAmount rawValue: Double, previous: VisualDetailTier) -> VisualDetailTier {
        let value = min(max(rawValue, 0), 1)

        switch previous {
        case .minimal:
            if value >= thresholds.enterFull { return .full }
            if value >= thresholds.enterReduced { return .reduced80 }
            return .minimal
        case .reduced80:
            if value >= thresholds.enterFull { return .full }
            if value <= thresholds.leaveReduced { return .minimal }
            return .reduced80
        case .full:
            if value <= thresholds.leaveReduced { return .minimal }
            if value <= thresholds.leaveFull { return .reduced80 }
            return .full
        }
    }
}

/// Runtime sidecar values from the 150-asset/450-variant catalog. Geometry is never mutated.
public struct VisualDetailPresentationParameters: Codable, Sendable, Hashable {
    public let labelDensityRatio: Double
    public let motionMode: String
    public let motionSpeedMultiplier: Double
    public let particleOrFlowCountRatio: Double
    public let particleOrFlowMode: String
    public let saturationMultiplier: Double
    public let secondaryDetailVisibilityRatio: Double
    public let semanticDensityTarget: Double
    public let specularMultiplier: Double
    public let textureResolutionScale: Double

    public init(
        labelDensityRatio: Double,
        motionMode: String,
        motionSpeedMultiplier: Double,
        particleOrFlowCountRatio: Double,
        particleOrFlowMode: String,
        saturationMultiplier: Double,
        secondaryDetailVisibilityRatio: Double,
        semanticDensityTarget: Double,
        specularMultiplier: Double,
        textureResolutionScale: Double
    ) {
        self.labelDensityRatio = labelDensityRatio
        self.motionMode = motionMode
        self.motionSpeedMultiplier = motionSpeedMultiplier
        self.particleOrFlowCountRatio = particleOrFlowCountRatio
        self.particleOrFlowMode = particleOrFlowMode
        self.saturationMultiplier = saturationMultiplier
        self.secondaryDetailVisibilityRatio = secondaryDetailVisibilityRatio
        self.semanticDensityTarget = semanticDensityTarget
        self.specularMultiplier = specularMultiplier
        self.textureResolutionScale = textureResolutionScale
    }

    private enum CodingKeys: String, CodingKey {
        case labelDensityRatio = "label_density_ratio"
        case motionMode = "motion_mode"
        case motionSpeedMultiplier = "motion_speed_multiplier"
        case particleOrFlowCountRatio = "particle_or_flow_count_ratio"
        case particleOrFlowMode = "particle_or_flow_mode"
        case saturationMultiplier = "saturation_multiplier"
        case secondaryDetailVisibilityRatio = "secondary_detail_visibility_ratio"
        case semanticDensityTarget = "semantic_density_target"
        case specularMultiplier = "specular_multiplier"
        case textureResolutionScale = "texture_resolution_scale"
    }
}
