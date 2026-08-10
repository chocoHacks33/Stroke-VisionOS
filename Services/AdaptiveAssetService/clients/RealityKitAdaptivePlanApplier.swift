import CryptoKit
import Foundation
import RealityKit

#if os(macOS)
  import AppKit
  private typealias AdaptivePlatformColor = NSColor
#else
  import UIKit
  private typealias AdaptivePlatformColor = UIColor
#endif

public enum AdaptivePlanError: Error, LocalizedError {
  case invalidContract(String)
  case packageRevisionMismatch
  case entityPathMissing([Int])
  case modelComponentMissing([Int])
  case materialSlotMismatch([Int])

  public var errorDescription: String? {
    switch self {
    case .invalidContract(let detail):
      return "Invalid adaptive-plan contract: \(detail)"
    case .packageRevisionMismatch:
      return "The loaded USDZ revision does not match the adaptive plan."
    case .entityPathMissing(let path):
      return "RealityKit child-index path does not resolve: \(path)"
    case .modelComponentMissing(let path):
      return "Mapped material target has no ModelComponent: \(path)"
    case .materialSlotMismatch(let path):
      return "Mapped material-slot count changed for child-index path: \(path)"
    }
  }
}

public struct AdaptiveEditResponse: Decodable {
  public let applicationContract: AdaptiveApplicationContract
  public let applicationPlan: AdaptiveApplicationPlan
  public let recipe: AdaptiveRecipeContract
  public let sourceAsset: AdaptiveSourceAsset
}

public struct AdaptiveSourceAsset: Decodable {
  public let assetId: String
  public let packageBytes: Int
  public let packageSha256: String
}

public struct AdaptiveRecipeContract: Decodable {
  public let adaptationTier: String
  public let assetId: String
  public let audience: String
  public let catalogProfileRevision: String
  public let detail: AdaptiveRecipeDetail
  public let entityMappingRevision: String
  public let materials: AdaptiveRecipeMaterials
  public let motion: AdaptiveRecipeMotion
  public let policyVersion: String
}

public struct AdaptiveRecipeDetail: Decodable {
  public let hiddenLayerGroups: [String]
}

public struct AdaptiveRecipeMaterials: Decodable {
  public let emissionMultiplier: Float
  public let roughnessFloor: Float
  public let saturationMultiplier: Float
  public let specularMultiplier: Float
  public let tintRgba: [Float]
}

public struct AdaptiveRecipeMotion: Decodable {
  public let autoplay: Bool
  public let looping: Bool
  public let reviewedStaticFrameAvailable: Bool?
  public let speedMultiplier: Float
  public let staticPoseStrategy: String?
  public let preference: String
}

public struct AdaptiveApplicationContract: Decodable {
  public let developerPreviewAuthorized: Bool
  public let developerRuntimeApplicationAuthorized: Bool
  public let fallbackRequired: Bool
  public let mutatesSourceAsset: Bool
  public let patientDisplayAuthorized: Bool
  public let patientDisplayReviewRequired: Bool
  public let semanticMappingStatus: String
}

public enum AdaptiveExecutionContext: Equatable {
  case developerPreview
  case patientEducation
}

public struct AdaptivePackageRevision: Equatable {
  public let bytes: Int
  public let sha256: String
}

public struct AdaptiveExpectedPresentation {
  public let audience: String
  public let detailPreference: String
  public let familyParticipationAuthorized: Bool
  public let familyPrivacyConfirmed: Bool
  public let motionPreference: String

  public init(
    audience: String,
    detailPreference: String,
    motionPreference: String,
    familyParticipationAuthorized: Bool = false,
    familyPrivacyConfirmed: Bool = false
  ) {
    self.audience = audience
    self.detailPreference = detailPreference
    self.familyParticipationAuthorized = familyParticipationAuthorized
    self.familyPrivacyConfirmed = familyPrivacyConfirmed
    self.motionPreference = motionPreference
  }
}

public struct AdaptivePresentationUIReadiness {
  public let adaptationDisclosureVisible: Bool
  public let comfortControlsAvailable: Bool
  public let contentWarningPresented: Bool
  public let progressiveDisclosureAvailable: Bool

  public init(
    adaptationDisclosureVisible: Bool,
    comfortControlsAvailable: Bool,
    contentWarningPresented: Bool,
    progressiveDisclosureAvailable: Bool
  ) {
    self.adaptationDisclosureVisible = adaptationDisclosureVisible
    self.comfortControlsAvailable = comfortControlsAvailable
    self.contentWarningPresented = contentWarningPresented
    self.progressiveDisclosureAvailable = progressiveDisclosureAvailable
  }
}

@MainActor
public protocol AdaptiveAnimationStateManaging: AnyObject {
  /// Capture and suspend playback controllers owned by the integrating app.
  func prepareForAdaptivePresentation() throws

  /// Recreate the app-owned playback state captured during preparation.
  func restoreAfterAdaptivePresentation()
}

public enum AdaptiveAnimationBaseline {
  /// Valid only immediately after loading, before the app starts any playback.
  case pristineLoadedRoot

  /// Required when the app already owns active or paused playback controllers.
  case appManaged(any AdaptiveAnimationStateManaging)
}

public enum AdaptiveFallbackPresentation {
  case notRequired
  case appPresented(String)
}

public struct AdaptiveApplicationPlan: Decodable {
  public let schemaVersion: String
  public let mappingStatus: String
  public let sourcePackageSha256: String
  public let visibilityOperations: [AdaptiveVisibilityOperation]
  public let materialOperations: [AdaptiveMaterialOperation]
  public let animationOperations: [AdaptiveAnimationOperation]
  public let sourceAssetUnchanged: Bool
  public let patientDisplayAuthorized: Bool
  public let unresolvedRequestedChanges: Bool
  public let fallbackIfUnresolved: String
  public let contentWarningRequired: Bool
  public let progressiveDisclosureRequired: Bool
}

public struct AdaptiveVisibilityOperation: Decodable {
  public let operation: String
  public let value: Bool
  public let childIndexPath: [Int]
}

public struct AdaptiveMaterialOperation: Decodable {
  public let operation: String
  public let childIndexPath: [Int]
  public let materialSlots: Int
  public let saturationMultiplier: Float?
  public let roughnessFloor: Float?
  public let specularMultiplier: Float?
  public let tintRgba: [Float]?
  public let emissionMultiplier: Float?
  public let preserveSourceAlpha: Bool
  public let unsupportedMaterialBehavior: String
  public let patientDisplayAuthorized: Bool
}

public struct AdaptiveAnimationOperation: Decodable {
  public let operation: String
  public let childIndexPath: [Int]
  public let animationResourceCount: Int
  public let autoplay: Bool
  public let looping: Bool
  public let speedMultiplier: Float
  public let staticPoseStrategy: String
  public let reviewedStaticFrameAvailable: Bool
}

public struct AdaptiveApplyReport: Codable {
  public let visibilityOperationsApplied: Int
  public let materialEntitiesApplied: Int
  public let materialSlotsTransformed: Int
  public let unsupportedMaterialSlotsPreserved: Int
  public let animationResourcesConfigured: Int
  public let sourceAssetUnchanged: Bool
  public let patientDisplayAuthorized: Bool
}

private struct AdaptiveBindingDocument: Decodable {
  let schemaVersion: String
  let assets: [AdaptiveBindingAsset]
}

private struct AdaptiveProfileDocument: Decodable {
  let schemaVersion: String
  let profiles: [AdaptiveProfileRecord]
}

private struct AdaptiveProfileRecord: Decodable {
  let assetId: String
  let allowedActions: AdaptiveAllowedActions
  let presentationIntensity: String
}

private struct AdaptiveAllowedActions: Decodable {
  let material: [String]
  let motion: [String]
  let visibility: [String]
}

private struct AdaptiveBindingAsset: Decodable {
  let assetId: String
  let packageBytes: Int
  let packageSha256: String
  let bindings: [AdaptiveModelBinding]
  let animationBindings: [AdaptiveAnimationBinding]
}

private struct AdaptiveModelBinding: Decodable {
  let automaticVisibilityChangeAllowed: Bool
  let childIndexPath: [Int]
  let entityName: String
  let materialSlots: Int
  let semanticGroups: [String]
}

private struct AdaptiveAnimationBinding: Decodable {
  let animationResourceCount: Int
  let childIndexPath: [Int]
}

/// Verifies endpoint operations against code-signed binding/profile resources
/// bundled with the integrating app.
public final class AdaptiveLocalPlanAuthorization {
  private struct AuthorizedAsset {
    let packageBytes: Int
    let packageSha256: String
    let modelBindings: [String: AdaptiveModelBinding]
    let animationBindings: [String: AdaptiveAnimationBinding]
    let materialActions: Set<String>
    let motionActions: Set<String>
    let presentationIntensity: String
    let visibilityActions: Set<String>
  }

  private let bindingRevision: String
  private let profileRevision: String
  private let assets: [String: AuthorizedAsset]

  public init(bindingsURL: URL, profilesURL: URL) throws {
    let bindingsData = try Data(contentsOf: bindingsURL)
    let profilesData = try Data(contentsOf: profilesURL)
    bindingRevision = Self.sha256(bindingsData)
    profileRevision = Self.sha256(profilesData)

    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    let document = try decoder.decode(AdaptiveBindingDocument.self, from: bindingsData)
    let profileDocument = try decoder.decode(AdaptiveProfileDocument.self, from: profilesData)
    guard document.schemaVersion == "1.0" else {
      throw AdaptivePlanError.invalidContract("unsupported local binding schema")
    }
    guard profileDocument.schemaVersion == "1.0.0" else {
      throw AdaptivePlanError.invalidContract("unsupported local profile schema")
    }

    var profiles: [String: AdaptiveProfileRecord] = [:]
    for profile in profileDocument.profiles {
      guard profiles[profile.assetId] == nil else {
        throw AdaptivePlanError.invalidContract("duplicate local adaptation profile")
      }
      profiles[profile.assetId] = profile
    }

    var authorizedAssets: [String: AuthorizedAsset] = [:]
    for record in document.assets {
      guard authorizedAssets[record.assetId] == nil else {
        throw AdaptivePlanError.invalidContract("duplicate local asset binding")
      }
      guard let profile = profiles[record.assetId] else {
        throw AdaptivePlanError.invalidContract("local binding has no adaptation profile")
      }
      var modelBindings: [String: AdaptiveModelBinding] = [:]
      for binding in record.bindings {
        let key = Self.pathKey(binding.childIndexPath)
        guard modelBindings[key] == nil else {
          throw AdaptivePlanError.invalidContract("duplicate local model selector")
        }
        modelBindings[key] = binding
      }
      var animationBindings: [String: AdaptiveAnimationBinding] = [:]
      for binding in record.animationBindings {
        let key = Self.pathKey(binding.childIndexPath)
        guard animationBindings[key] == nil else {
          throw AdaptivePlanError.invalidContract("duplicate local animation selector")
        }
        animationBindings[key] = binding
      }
      authorizedAssets[record.assetId] = AuthorizedAsset(
        packageBytes: record.packageBytes,
        packageSha256: record.packageSha256,
        modelBindings: modelBindings,
        animationBindings: animationBindings,
        materialActions: Set(profile.allowedActions.material),
        motionActions: Set(profile.allowedActions.motion),
        presentationIntensity: profile.presentationIntensity,
        visibilityActions: Set(profile.allowedActions.visibility)
      )
    }
    guard Set(authorizedAssets.keys) == Set(profiles.keys) else {
      throw AdaptivePlanError.invalidContract("local profile and binding coverage differs")
    }
    assets = authorizedAssets
  }

  @MainActor
  public func authorize(
    _ response: AdaptiveEditResponse,
    observedPackage: AdaptivePackageRevision,
    loadedRoot: Entity
  ) throws {
    let recipe = response.recipe
    guard recipe.policyVersion == "presentation-preference-v2",
      recipe.assetId == response.sourceAsset.assetId,
      recipe.entityMappingRevision == bindingRevision,
      recipe.catalogProfileRevision == profileRevision,
      Self.recipeValuesAreCanonical(recipe)
    else {
      throw AdaptivePlanError.invalidContract("local policy/profile revision does not match")
    }

    let source = response.sourceAsset
    guard let asset = assets[source.assetId],
      source.packageBytes == observedPackage.bytes,
      source.packageSha256 == observedPackage.sha256,
      asset.packageBytes == observedPackage.bytes,
      asset.packageSha256 == observedPackage.sha256,
      response.applicationPlan.sourcePackageSha256 == observedPackage.sha256
    else {
      throw AdaptivePlanError.packageRevisionMismatch
    }

    try Self.validateLoadedTopology(asset, root: loadedRoot)

    var visibilityPaths = Set<String>()
    let hiddenGroups = Set(recipe.detail.hiddenLayerGroups)
    let visibilityChangeAllowed = asset.visibilityActions.contains(
      "hide_graphic_subcomponents_if_semantically_mapped")
    let expectedUnresolved = asset.modelBindings.values.contains { binding in
      !hiddenGroups.isDisjoint(with: binding.semanticGroups)
        && (!binding.automaticVisibilityChangeAllowed || !visibilityChangeAllowed)
    }
    let expectedFallback: String
    switch recipe.adaptationTier {
    case "clinical_detail":
      expectedFallback = "source_asset_with_legend"
    case "standard", "simplified":
      expectedFallback = "static_orientation_card"
    case "overview":
      expectedFallback = "plain_language_2d_summary"
    default:
      throw AdaptivePlanError.invalidContract("unsupported adaptation tier")
    }
    guard response.applicationPlan.unresolvedRequestedChanges == expectedUnresolved,
      response.applicationContract.fallbackRequired == expectedUnresolved,
      response.applicationPlan.fallbackIfUnresolved == expectedFallback
    else {
      throw AdaptivePlanError.invalidContract("fallback contract is not locally authorized")
    }
    let reducedDetailTier = ["overview", "simplified"].contains(recipe.adaptationTier)
    let expectedContentWarning =
      ["moderate", "high"].contains(asset.presentationIntensity)
      && reducedDetailTier
    let expectedProgressiveDisclosure =
      asset.visibilityActions.contains(
        "progressive_disclosure") && reducedDetailTier
    guard response.applicationPlan.contentWarningRequired == expectedContentWarning,
      response.applicationPlan.progressiveDisclosureRequired == expectedProgressiveDisclosure
    else {
      throw AdaptivePlanError.invalidContract("presentation UI contract is not locally authorized")
    }
    let expectedVisibilityPaths = Set(
      asset.modelBindings.compactMap { key, binding in
        visibilityChangeAllowed && binding.automaticVisibilityChangeAllowed
          && !hiddenGroups.isDisjoint(with: binding.semanticGroups)
          ? key : nil
      })
    for operation in response.applicationPlan.visibilityOperations {
      let key = Self.pathKey(operation.childIndexPath)
      guard visibilityPaths.insert(key).inserted,
        let binding = asset.modelBindings[key],
        binding.automaticVisibilityChangeAllowed,
        operation.value == false,
        !hiddenGroups.isDisjoint(with: binding.semanticGroups)
      else {
        throw AdaptivePlanError.invalidContract("visibility selector is not locally authorized")
      }
    }
    guard visibilityPaths == expectedVisibilityPaths else {
      throw AdaptivePlanError.invalidContract("visibility operation set is not canonical")
    }

    var materialPaths = Set<String>()
    let protectedMaterialGroups: Set<String> = ["labels", "pathology_primary"]
    let expectedMaterialPaths = Set(
      asset.modelBindings.compactMap { key, binding in
        recipe.adaptationTier != "clinical_detail" && binding.materialSlots > 0
          && protectedMaterialGroups.isDisjoint(with: binding.semanticGroups)
          ? key : nil
      })
    for operation in response.applicationPlan.materialOperations {
      let key = Self.pathKey(operation.childIndexPath)
      guard materialPaths.insert(key).inserted,
        let binding = asset.modelBindings[key],
        binding.materialSlots == operation.materialSlots,
        protectedMaterialGroups.isDisjoint(with: binding.semanticGroups),
        Self.materialValuesAreAuthorized(
          operation,
          recipe: recipe.materials,
          actions: asset.materialActions)
      else {
        throw AdaptivePlanError.invalidContract("material operation is not locally authorized")
      }
    }
    guard materialPaths == expectedMaterialPaths else {
      throw AdaptivePlanError.invalidContract("material operation set is not canonical")
    }

    var animationPaths = Set<String>()
    let expectedAnimationPaths = Set(asset.animationBindings.keys)
    for operation in response.applicationPlan.animationOperations {
      let key = Self.pathKey(operation.childIndexPath)
      guard animationPaths.insert(key).inserted,
        let binding = asset.animationBindings[key],
        binding.animationResourceCount == operation.animationResourceCount,
        Self.animationValuesAreAuthorized(
          operation,
          recipe: recipe.motion,
          actions: asset.motionActions)
      else {
        throw AdaptivePlanError.invalidContract("animation operation is not locally authorized")
      }
    }
    guard animationPaths == expectedAnimationPaths else {
      throw AdaptivePlanError.invalidContract("animation operation set is not canonical")
    }
  }

  private static func materialValuesAreAuthorized(
    _ operation: AdaptiveMaterialOperation,
    recipe: AdaptiveRecipeMaterials,
    actions: Set<String>
  ) -> Bool {
    let expectedSaturation: Float? =
      actions.contains(
        "reduce_saturation_preserving_source_access") ? recipe.saturationMultiplier : nil
    let expectedRoughness: Float? =
      actions.contains("increase_roughness")
      ? recipe.roughnessFloor : nil
    let expectedSpecular: Float? =
      actions.contains("reduce_specular")
      ? recipe.specularMultiplier : nil
    let expectedTint: [Float]? =
      actions.contains("apply_bounded_developer_preview_tint")
      ? recipe.tintRgba : nil
    let expectedEmission: Float? =
      actions.contains("reduce_emission")
      ? recipe.emissionMultiplier : nil

    guard operation.materialSlots > 0,
      unitValueMatches(operation.saturationMultiplier, expected: expectedSaturation),
      unitValueMatches(operation.roughnessFloor, expected: expectedRoughness),
      unitValueMatches(operation.specularMultiplier, expected: expectedSpecular),
      operation.tintRgba == expectedTint,
      unitValueMatches(operation.emissionMultiplier, expected: expectedEmission),
      operation.tintRgba?.allSatisfy({ $0.isFinite && (0...1).contains($0) }) ?? true
    else {
      return false
    }
    return operation.tintRgba == nil || operation.tintRgba?.count == 4
  }

  private static func recipeValuesAreCanonical(_ recipe: AdaptiveRecipeContract) -> Bool {
    let hidden: Set<String>
    let tint: [Float]
    let saturation: Float
    let roughness: Float
    let specular: Float
    let emission: Float
    let baseAutoplay: Bool
    let baseSpeed: Float
    let baseLooping: Bool

    switch recipe.adaptationTier {
    case "clinical_detail":
      hidden = []
      tint = [0.96, 0.98, 1, 1]
      saturation = 1
      roughness = 0.35
      specular = 1
      emission = 1
      baseAutoplay = true
      baseSpeed = 1
      baseLooping = true
    case "standard":
      hidden = ["micro_detail"]
      tint = [0.91, 0.95, 0.98, 1]
      saturation = 0.84
      roughness = 0.42
      specular = 0.85
      emission = 0.82
      baseAutoplay = true
      baseSpeed = 0.75
      baseLooping = false
    case "simplified":
      hidden = ["anatomy_secondary", "micro_detail", "incision_detail", "blood_cells"]
      tint = [0.85, 0.92, 0.95, 1]
      saturation = 0.68
      roughness = 0.5
      specular = 0.7
      emission = 0.64
      baseAutoplay = false
      baseSpeed = 0.5
      baseLooping = false
    case "overview":
      hidden = [
        "anatomy_secondary", "micro_detail", "incision_detail", "blood_cells",
        "blood_volume", "surgical_field",
      ]
      tint = [0.8, 0.9, 0.93, 1]
      saturation = 0.52
      roughness = 0.58
      specular = 0.55
      emission = 0.48
      baseAutoplay = false
      baseSpeed = 0.3
      baseLooping = false
    default:
      return false
    }

    let expectedAutoplay: Bool
    let expectedSpeed: Float
    let expectedLooping: Bool
    switch recipe.motion.preference {
    case "system_default":
      expectedAutoplay = baseAutoplay
      expectedSpeed = baseSpeed
      expectedLooping = baseLooping
      guard recipe.motion.staticPoseStrategy == nil,
        recipe.motion.reviewedStaticFrameAvailable == nil
      else {
        return false
      }
    case "reduced":
      expectedAutoplay = false
      expectedSpeed = min(baseSpeed, 0.5)
      expectedLooping = false
      guard recipe.motion.staticPoseStrategy == nil,
        recipe.motion.reviewedStaticFrameAvailable == nil
      else {
        return false
      }
    case "static":
      expectedAutoplay = false
      expectedSpeed = 0
      expectedLooping = false
      guard recipe.motion.staticPoseStrategy == "initial_authored_pose",
        recipe.motion.reviewedStaticFrameAvailable == false
      else {
        return false
      }
    default:
      return false
    }

    let recipeHidden = Set(recipe.detail.hiddenLayerGroups)
    return recipeHidden.count == recipe.detail.hiddenLayerGroups.count
      && recipeHidden == hidden
      && recipe.materials.tintRgba == tint
      && recipe.materials.saturationMultiplier == saturation
      && recipe.materials.roughnessFloor == roughness
      && recipe.materials.specularMultiplier == specular
      && recipe.materials.emissionMultiplier == emission
      && recipe.motion.autoplay == expectedAutoplay
      && recipe.motion.speedMultiplier == expectedSpeed
      && recipe.motion.looping == expectedLooping
  }

  private static func animationValuesAreAuthorized(
    _ operation: AdaptiveAnimationOperation,
    recipe: AdaptiveRecipeMotion,
    actions: Set<String>
  ) -> Bool {
    let expectedAutoplay = actions.contains("disable_autoplay") ? recipe.autoplay : true
    let expectedLooping = actions.contains("disable_looping") ? recipe.looping : false
    let expectedSpeed = actions.contains("reduce_speed") ? recipe.speedMultiplier : 1
    let expectedStaticPose =
      recipe.preference == "static"
        && actions.contains("pause_at_initial_authored_pose")
      ? "initial_authored_pose" : "not_requested"
    return operation.animationResourceCount >= 0
      && operation.speedMultiplier.isFinite
      && (0...1).contains(operation.speedMultiplier)
      && operation.autoplay == expectedAutoplay
      && operation.looping == expectedLooping
      && operation.speedMultiplier == expectedSpeed
      && operation.staticPoseStrategy == expectedStaticPose
      && operation.reviewedStaticFrameAvailable == false
  }

  private static func unitValueMatches(_ value: Float?, expected: Float?) -> Bool {
    switch (value, expected) {
    case (nil, nil):
      return true
    case (.some(let value), .some(let expected)):
      return value.isFinite && (0...1).contains(value) && value == expected
    default:
      return false
    }
  }

  private static func pathKey(_ path: [Int]) -> String {
    path.map(String.init).joined(separator: ".")
  }

  @MainActor
  private static func validateLoadedTopology(_ asset: AuthorizedAsset, root: Entity) throws {
    for binding in asset.modelBindings.values {
      let entity = try resolve(root: root, path: binding.childIndexPath)
      guard entity.name == binding.entityName,
        let model = entity.components[ModelComponent.self],
        model.materials.count == binding.materialSlots
      else {
        throw AdaptivePlanError.invalidContract("loaded model topology no longer matches bindings")
      }
    }
    for binding in asset.animationBindings.values {
      let entity = try resolve(root: root, path: binding.childIndexPath)
      guard entity.availableAnimations.count == binding.animationResourceCount else {
        throw AdaptivePlanError.invalidContract(
          "loaded animation topology no longer matches bindings")
      }
    }
  }

  @MainActor
  private static func resolve(root: Entity, path: [Int]) throws -> Entity {
    var entity = root
    for index in path {
      guard index >= 0, index < entity.children.count else {
        throw AdaptivePlanError.entityPathMissing(path)
      }
      entity = entity.children[index]
    }
    return entity
  }

  private static func sha256(_ data: Data) -> String {
    SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
  }
}

@MainActor
public final class RealityKitAdaptivePlanSession {
  private struct VisibilitySnapshot {
    let entity: Entity
    let isEnabled: Bool
  }

  private struct MaterialSnapshot {
    let entity: Entity
    let component: ModelComponent
  }

  private let root: Entity
  private let packageRevision: AdaptivePackageRevision
  private var visibilitySnapshots: [String: VisibilitySnapshot] = [:]
  private var materialSnapshots: [String: MaterialSnapshot] = [:]
  private var createdPlaybackControllers: [AnimationPlaybackController] = []
  private var appAnimationStateManager: (any AdaptiveAnimationStateManaging)?

  private init(root: Entity, packageRevision: AdaptivePackageRevision) {
    self.root = root
    self.packageRevision = packageRevision
  }

  public var rootEntity: Entity {
    root
  }

  public static func load(contentsOf packageURL: URL) throws -> RealityKitAdaptivePlanSession {
    let revisionBeforeLoad = try revision(of: packageURL)
    let root = try Entity.load(contentsOf: packageURL)
    let revisionAfterLoad = try revision(of: packageURL)
    guard revisionBeforeLoad == revisionAfterLoad else {
      throw AdaptivePlanError.packageRevisionMismatch
    }
    return RealityKitAdaptivePlanSession(
      root: root,
      packageRevision: revisionAfterLoad
    )
  }

  public static func decodeResponse(_ data: Data) throws -> AdaptiveEditResponse {
    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    return try decoder.decode(AdaptiveEditResponse.self, from: data)
  }

  public nonisolated static func revision(of packageURL: URL) throws -> AdaptivePackageRevision {
    let data = try Data(contentsOf: packageURL, options: .mappedIfSafe)
    let digest = SHA256.hash(data: data)
    return AdaptivePackageRevision(
      bytes: data.count,
      sha256: digest.map { String(format: "%02x", $0) }.joined()
    )
  }

  public func apply(
    _ response: AdaptiveEditResponse,
    executionContext: AdaptiveExecutionContext,
    authorization: AdaptiveLocalPlanAuthorization,
    animationBaseline: AdaptiveAnimationBaseline,
    fallbackPresentation: AdaptiveFallbackPresentation,
    expectedPresentation: AdaptiveExpectedPresentation,
    uiReadiness: AdaptivePresentationUIReadiness
  ) throws -> AdaptiveApplyReport {
    // A context transition or replacement request must never leave a prior
    // developer-preview presentation active when the new request is rejected.
    restoreOriginalPresentation()
    var completed = false
    defer {
      if !completed {
        restoreOriginalPresentation()
      }
    }

    let contract = response.applicationContract
    guard executionContext == .developerPreview,
      contract.developerPreviewAuthorized,
      contract.developerRuntimeApplicationAuthorized,
      contract.mutatesSourceAsset == false,
      contract.patientDisplayAuthorized == false,
      contract.patientDisplayReviewRequired,
      contract.semanticMappingStatus == "exact_revision_bound"
    else {
      throw AdaptivePlanError.invalidContract(
        "only an authorized developer-preview context may execute this plan")
    }

    try authorization.authorize(
      response,
      observedPackage: packageRevision,
      loadedRoot: root)

    guard ["patient", "family"].contains(expectedPresentation.audience),
      response.recipe.audience == expectedPresentation.audience,
      response.recipe.adaptationTier == expectedPresentation.detailPreference,
      response.recipe.motion.preference == expectedPresentation.motionPreference,
      expectedPresentation.audience != "family"
        || (expectedPresentation.familyParticipationAuthorized
          && expectedPresentation.familyPrivacyConfirmed)
    else {
      throw AdaptivePlanError.invalidContract(
        "response does not match the app's requested presentation")
    }

    guard uiReadiness.adaptationDisclosureVisible,
      uiReadiness.comfortControlsAvailable,
      !response.applicationPlan.contentWarningRequired || uiReadiness.contentWarningPresented,
      !response.applicationPlan.progressiveDisclosureRequired
        || uiReadiness.progressiveDisclosureAvailable
    else {
      throw AdaptivePlanError.invalidContract("required presentation UI is not ready")
    }

    let plan = response.applicationPlan
    guard plan.schemaVersion == "1.0", plan.mappingStatus == "exact_revision_bound" else {
      throw AdaptivePlanError.invalidContract("unsupported schema or mapping status")
    }
    guard plan.sourcePackageSha256 == packageRevision.sha256 else {
      throw AdaptivePlanError.packageRevisionMismatch
    }
    guard plan.sourceAssetUnchanged, plan.patientDisplayAuthorized == false else {
      throw AdaptivePlanError.invalidContract("source mutation or patient display was authorized")
    }
    guard contract.fallbackRequired == plan.unresolvedRequestedChanges else {
      throw AdaptivePlanError.invalidContract("fallback state is inconsistent")
    }
    switch fallbackPresentation {
    case .notRequired:
      guard !contract.fallbackRequired else {
        throw AdaptivePlanError.invalidContract("required fallback was not presented by the app")
      }
    case .appPresented(let fallback):
      guard contract.fallbackRequired, fallback == plan.fallbackIfUnresolved else {
        throw AdaptivePlanError.invalidContract("presented fallback does not match the plan")
      }
    }

    if !plan.animationOperations.isEmpty {
      switch animationBaseline {
      case .pristineLoadedRoot:
        break
      case .appManaged(let manager):
        appAnimationStateManager = manager
        try manager.prepareForAdaptivePresentation()
      }
    }

    var visibilityApplied = 0
    var materialEntitiesApplied = 0
    var materialSlotsTransformed = 0
    var unsupportedMaterialSlotsPreserved = 0
    var animationResourcesConfigured = 0

    for operation in plan.visibilityOperations {
      guard operation.operation == "set_enabled" else {
        throw AdaptivePlanError.invalidContract("unsupported visibility operation")
      }
      let entity = try resolve(operation.childIndexPath)
      snapshotVisibility(entity, at: operation.childIndexPath)
      entity.isEnabled = operation.value
      visibilityApplied += 1
    }

    for operation in plan.materialOperations {
      guard operation.operation == "transform_existing_model_materials",
        operation.preserveSourceAlpha,
        operation.patientDisplayAuthorized == false,
        operation.unsupportedMaterialBehavior == "preserve_source_material"
      else {
        throw AdaptivePlanError.invalidContract("unsafe material operation")
      }
      let entity = try resolve(operation.childIndexPath)
      guard var component = entity.components[ModelComponent.self] else {
        throw AdaptivePlanError.modelComponentMissing(operation.childIndexPath)
      }
      guard component.materials.count == operation.materialSlots else {
        throw AdaptivePlanError.materialSlotMismatch(operation.childIndexPath)
      }
      snapshotMaterials(entity, component: component, at: operation.childIndexPath)

      var transformed: [any Material] = []
      transformed.reserveCapacity(component.materials.count)
      for material in component.materials {
        let result = transform(material: material, operation: operation)
        transformed.append(result.material)
        if result.changed {
          materialSlotsTransformed += 1
        } else {
          unsupportedMaterialSlotsPreserved += 1
        }
      }
      component.materials = transformed
      entity.components.set(component)
      materialEntitiesApplied += 1
    }

    for operation in plan.animationOperations {
      guard operation.operation == "configure_animation_playback",
        operation.reviewedStaticFrameAvailable == false,
        operation.staticPoseStrategy == "not_requested"
          || operation.staticPoseStrategy == "initial_authored_pose"
      else {
        throw AdaptivePlanError.invalidContract("unsafe animation operation")
      }
      let entity = try resolve(operation.childIndexPath)
      guard entity.availableAnimations.count == operation.animationResourceCount else {
        throw AdaptivePlanError.invalidContract("animation resource count changed")
      }
      entity.stopAllAnimations(recursive: false)
      for authoredAnimation in entity.availableAnimations {
        let resource =
          operation.looping
          ? authoredAnimation.repeat()
          : authoredAnimation
        let controller = entity.playAnimation(
          resource,
          transitionDuration: 0,
          startsPaused: !operation.autoplay
        )
        controller.speed = operation.speedMultiplier
        if operation.staticPoseStrategy == "initial_authored_pose" {
          controller.time = 0
          controller.pause()
        }
        createdPlaybackControllers.append(controller)
        animationResourcesConfigured += 1
      }
    }

    let report = AdaptiveApplyReport(
      visibilityOperationsApplied: visibilityApplied,
      materialEntitiesApplied: materialEntitiesApplied,
      materialSlotsTransformed: materialSlotsTransformed,
      unsupportedMaterialSlotsPreserved: unsupportedMaterialSlotsPreserved,
      animationResourcesConfigured: animationResourcesConfigured,
      sourceAssetUnchanged: true,
      patientDisplayAuthorized: false
    )
    completed = true
    return report
  }

  public func restoreOriginalPresentation() {
    for controller in createdPlaybackControllers {
      controller.stop()
    }
    createdPlaybackControllers.removeAll()

    for snapshot in materialSnapshots.values {
      snapshot.entity.components.set(snapshot.component)
    }
    materialSnapshots.removeAll()

    for snapshot in visibilitySnapshots.values {
      snapshot.entity.isEnabled = snapshot.isEnabled
    }
    visibilitySnapshots.removeAll()

    appAnimationStateManager?.restoreAfterAdaptivePresentation()
    appAnimationStateManager = nil
  }

  public func pauseAdaptiveAnimations() {
    for controller in createdPlaybackControllers {
      controller.pause()
    }
  }

  public func resumeAdaptiveAnimations() {
    for controller in createdPlaybackControllers {
      controller.resume()
    }
  }

  private func resolve(_ childIndexPath: [Int]) throws -> Entity {
    var entity = root
    for index in childIndexPath {
      guard index >= 0, index < entity.children.count else {
        throw AdaptivePlanError.entityPathMissing(childIndexPath)
      }
      entity = entity.children[index]
    }
    return entity
  }

  private func pathKey(_ path: [Int]) -> String {
    path.map(String.init).joined(separator: ".")
  }

  private func snapshotVisibility(_ entity: Entity, at path: [Int]) {
    let key = pathKey(path)
    if visibilitySnapshots[key] == nil {
      visibilitySnapshots[key] = VisibilitySnapshot(entity: entity, isEnabled: entity.isEnabled)
    }
  }

  private func snapshotMaterials(
    _ entity: Entity,
    component: ModelComponent,
    at path: [Int]
  ) {
    let key = pathKey(path)
    if materialSnapshots[key] == nil {
      materialSnapshots[key] = MaterialSnapshot(entity: entity, component: component)
    }
  }

  private func transform(
    material: any Material,
    operation: AdaptiveMaterialOperation
  ) -> (material: any Material, changed: Bool) {
    if var pbr = material as? PhysicallyBasedMaterial {
      var baseColor = pbr.baseColor
      baseColor.tint = adjustedColor(baseColor.tint, operation: operation)
      pbr.baseColor = baseColor
      if let floor = operation.roughnessFloor {
        pbr.roughness.scale = max(pbr.roughness.scale, floor)
      }
      if let multiplier = operation.specularMultiplier {
        pbr.specular.scale *= multiplier
      }
      if let multiplier = operation.emissionMultiplier {
        pbr.emissiveIntensity *= multiplier
      }
      return (pbr, true)
    }

    if var simple = material as? SimpleMaterial {
      var color = simple.color
      color.tint = adjustedColor(color.tint, operation: operation)
      simple.color = color
      if let floor = operation.roughnessFloor,
        case .float(let sourceRoughness) = simple.roughness
      {
        simple.roughness = .float(max(sourceRoughness, floor))
      }
      return (simple, true)
    }

    if var unlit = material as? UnlitMaterial {
      var color = unlit.color
      color.tint = adjustedColor(color.tint, operation: operation)
      unlit.color = color
      return (unlit, true)
    }

    return (material, false)
  }

  private func adjustedColor(
    _ source: AdaptivePlatformColor,
    operation: AdaptiveMaterialOperation
  ) -> AdaptivePlatformColor {
    let rgba = colorComponents(source)
    let saturation = CGFloat(max(0, min(1, operation.saturationMultiplier ?? 1)))
    let luminance = 0.2126 * rgba.red + 0.7152 * rgba.green + 0.0722 * rgba.blue
    var red = luminance + (rgba.red - luminance) * saturation
    var green = luminance + (rgba.green - luminance) * saturation
    var blue = luminance + (rgba.blue - luminance) * saturation
    if let tint = operation.tintRgba, tint.count == 4 {
      red *= max(0, min(1, CGFloat(tint[0])))
      green *= max(0, min(1, CGFloat(tint[1])))
      blue *= max(0, min(1, CGFloat(tint[2])))
    }
    return AdaptivePlatformColor(
      red: max(0, min(1, red)),
      green: max(0, min(1, green)),
      blue: max(0, min(1, blue)),
      alpha: rgba.alpha
    )
  }

  private func colorComponents(
    _ color: AdaptivePlatformColor
  ) -> (red: CGFloat, green: CGFloat, blue: CGFloat, alpha: CGFloat) {
    var red: CGFloat = 1
    var green: CGFloat = 1
    var blue: CGFloat = 1
    var alpha: CGFloat = 1
    #if os(macOS)
      let converted = color.usingColorSpace(.sRGB) ?? color
      converted.getRed(&red, green: &green, blue: &blue, alpha: &alpha)
    #else
      color.getRed(&red, green: &green, blue: &blue, alpha: &alpha)
    #endif
    return (red, green, blue, alpha)
  }
}
