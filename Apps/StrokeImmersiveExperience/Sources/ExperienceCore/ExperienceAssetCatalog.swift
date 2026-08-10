import Foundation

public enum ExperienceAssetCategory: String, CaseIterable, Codable, Sendable, Hashable {
    case adaptivePresentation = "ADAPTIVE_PRESENTATION"
    case anatomyCNSMacro = "ANATOMY_CNS_MACRO"
    case anatomyHeadNeckSupport = "ANATOMY_HEAD_NECK_SUPPORT"
    case anatomyVascular = "ANATOMY_VASCULAR"
    case bloodFlowTeaching = "BLOOD_FLOW_TEACHING"
    case clinicalContext = "CLINICAL_CONTEXT"
    case compositeAssembly = "COMPOSITE_ASSEMBLY"
    case guidance = "GUIDANCE"
    case microConceptual = "MICRO_CONCEPTUAL"
    case openCranialAnatomyState = "OPEN_CRANIAL_ANATOMY_STATE"
    case pathologyMacro = "PATHOLOGY_MACRO"
    case spatialEnvironment = "SPATIAL_ENVIRONMENT"
    case toolsEndovascular = "TOOLS_ENDOVASCULAR"
    case toolsOpenCranial = "TOOLS_OPEN_CRANIAL"
}

public enum ExperienceAssetCompositionKind: String, Codable, Sendable, Hashable {
    case component
    case assembly
}

public struct ExperienceAssetRecord: Codable, Sendable, Hashable, Identifiable {
    public let assetID: String
    public let assemblyDomain: String?
    public let compositionKind: ExperienceAssetCompositionKind
    public let parameterPolicyCategory: ExperienceAssetCategory
    public let primaryCategory: ExperienceAssetCategory
    public let sourceAssetIndex: Int
    public let sourceManifest: String
    public let sourceManifestIndex: Int
    public let sourceUSDZ: String
    public let sourceUSDZBytes: Int
    public let sourceUSDZSHA256: String
    public let variantIDs: [String]

    public var id: String { assetID }

    private enum CodingKeys: String, CodingKey {
        case assetID = "asset_id"
        case assemblyDomain = "assembly_domain"
        case compositionKind = "composition_kind"
        case parameterPolicyCategory = "parameter_policy_category"
        case primaryCategory = "primary_category"
        case sourceAssetIndex = "source_asset_index"
        case sourceManifest = "source_manifest"
        case sourceManifestIndex = "source_manifest_index"
        case sourceUSDZ = "source_usdz"
        case sourceUSDZBytes = "source_usdz_bytes"
        case sourceUSDZSHA256 = "source_usdz_sha256"
        case variantIDs = "variant_ids"
    }
}

public struct VisualDetailVariantRecord: Codable, Sendable, Hashable, Identifiable {
    public let assetID: String
    public let bindsExactObservedSourceAsPresentation: Bool
    public let categoryID: ExperienceAssetCategory
    public let geometryMutationAllowed: Bool
    public let patientDisplayAuthorized: Bool
    public let presentationParameters: VisualDetailPresentationParameters
    public let preserveMedicalFactsAndWarnings: Bool
    public let preserveSilhouetteOrMeaning: Bool
    public let sourceAssetUnchanged: Bool
    public let sourceUSDZ: String
    public let sourceUSDZBytes: Int
    public let sourceUSDZSHA256: String
    public let tier: VisualDetailTier
    public let variantID: String
    public let virtualReversibleSidecar: Bool

    public var id: String { variantID }

    private enum CodingKeys: String, CodingKey {
        case assetID = "asset_id"
        case bindsExactObservedSourceAsPresentation = "binds_exact_observed_source_as_presentation"
        case categoryID = "category_id"
        case geometryMutationAllowed = "geometry_mutation_allowed"
        case patientDisplayAuthorized = "patient_display_authorized"
        case presentationParameters = "presentation_parameters"
        case preserveMedicalFactsAndWarnings = "preserve_medical_facts_and_warnings"
        case preserveSilhouetteOrMeaning = "preserve_silhouette_or_meaning"
        case sourceAssetUnchanged = "source_asset_unchanged"
        case sourceUSDZ = "source_usdz"
        case sourceUSDZBytes = "source_usdz_bytes"
        case sourceUSDZSHA256 = "source_usdz_sha256"
        case tier
        case variantID = "variant_id"
        case virtualReversibleSidecar = "virtual_reversible_sidecar"
    }
}

public struct ResolvedExperienceAsset: Sendable, Hashable, Identifiable {
    public let asset: ExperienceAssetRecord
    public let variant: VisualDetailVariantRecord

    public var id: String { variant.variantID }
    public var sourcePath: String { variant.sourceUSDZ }
    public var presentation: VisualDetailPresentationParameters { variant.presentationParameters }
}

public enum ExperienceAssetCatalogError: Error, LocalizedError, Sendable, Equatable {
    case unreadableCatalog(String)
    case releaseCountMismatch(declared: Int, decoded: Int)
    case variantCountMismatch(declared: Int, decoded: Int)
    case duplicateAssetID(String)
    case duplicateVariantID(String)
    case missingTier(assetID: String, tier: VisualDetailTier)
    case invalidVariant(assetID: String, reason: String)
    case unknownAsset(String)

    public var errorDescription: String? {
        switch self {
        case .unreadableCatalog(let detail):
            "The visual-detail catalog could not be read: \(detail)"
        case .releaseCountMismatch(let declared, let decoded):
            "Catalog declares \(declared) assets but decodes \(decoded)."
        case .variantCountMismatch(let declared, let decoded):
            "Catalog declares \(declared) variants but decodes \(decoded)."
        case .duplicateAssetID(let id):
            "Duplicate asset id: \(id)."
        case .duplicateVariantID(let id):
            "Duplicate variant id: \(id)."
        case .missingTier(let assetID, let tier):
            "Asset \(assetID) has no \(tier.rawValue) variant."
        case .invalidVariant(let assetID, let reason):
            "Variant for \(assetID) is invalid: \(reason)"
        case .unknownAsset(let id):
            "Unknown asset id: \(id)."
        }
    }
}

/// Immutable index over all 150 source assets and their 450 virtual detail bindings.
public struct ExperienceAssetCatalog: Sendable {
    public static let expectedReleaseAssetCount = 150
    public static let expectedVariantCount = 450

    public let catalogID: String
    public let sourceReleaseAssetCount: Int
    public let sourceReleaseManifestCount: Int
    public let tierOrder: [VisualDetailTier]
    public let assets: [ExperienceAssetRecord]
    public let variants: [VisualDetailVariantRecord]

    private let assetsByID: [String: ExperienceAssetRecord]
    private let variantsByID: [String: VisualDetailVariantRecord]

    public init(data: Data, requireCompleteRelease: Bool = true) throws {
        let document: CatalogDocument
        do {
            document = try JSONDecoder().decode(CatalogDocument.self, from: data)
        } catch {
            throw ExperienceAssetCatalogError.unreadableCatalog(String(describing: error))
        }

        if document.sourceReleaseAssetCount != document.assets.count {
            throw ExperienceAssetCatalogError.releaseCountMismatch(
                declared: document.sourceReleaseAssetCount,
                decoded: document.assets.count
            )
        }
        if document.virtualVariantCount != document.variants.count {
            throw ExperienceAssetCatalogError.variantCountMismatch(
                declared: document.virtualVariantCount,
                decoded: document.variants.count
            )
        }
        if requireCompleteRelease, document.assets.count != Self.expectedReleaseAssetCount {
            throw ExperienceAssetCatalogError.releaseCountMismatch(
                declared: Self.expectedReleaseAssetCount,
                decoded: document.assets.count
            )
        }
        if requireCompleteRelease, document.variants.count != Self.expectedVariantCount {
            throw ExperienceAssetCatalogError.variantCountMismatch(
                declared: Self.expectedVariantCount,
                decoded: document.variants.count
            )
        }

        var indexedAssets: [String: ExperienceAssetRecord] = [:]
        for asset in document.assets {
            guard indexedAssets.updateValue(asset, forKey: asset.assetID) == nil else {
                throw ExperienceAssetCatalogError.duplicateAssetID(asset.assetID)
            }
        }

        var indexedVariants: [String: VisualDetailVariantRecord] = [:]
        for variant in document.variants {
            guard indexedVariants.updateValue(variant, forKey: variant.variantID) == nil else {
                throw ExperienceAssetCatalogError.duplicateVariantID(variant.variantID)
            }
            guard indexedAssets[variant.assetID] != nil else {
                throw ExperienceAssetCatalogError.invalidVariant(
                    assetID: variant.assetID,
                    reason: "source asset is absent"
                )
            }
            guard !variant.geometryMutationAllowed, variant.sourceAssetUnchanged else {
                throw ExperienceAssetCatalogError.invalidVariant(
                    assetID: variant.assetID,
                    reason: "geometry mutation or a changed source was requested"
                )
            }
        }

        for asset in document.assets {
            for tier in VisualDetailTier.allCases {
                let variantID = "\(asset.assetID)::\(tier.rawValue)"
                guard let variant = indexedVariants[variantID] else {
                    throw ExperienceAssetCatalogError.missingTier(assetID: asset.assetID, tier: tier)
                }
                guard variant.sourceUSDZ == asset.sourceUSDZ,
                      variant.sourceUSDZBytes == asset.sourceUSDZBytes,
                      variant.sourceUSDZSHA256 == asset.sourceUSDZSHA256 else {
                    throw ExperienceAssetCatalogError.invalidVariant(
                        assetID: asset.assetID,
                        reason: "source path, byte count, or digest differs from the release asset"
                    )
                }
            }
        }

        catalogID = document.catalogID
        sourceReleaseAssetCount = document.sourceReleaseAssetCount
        sourceReleaseManifestCount = document.sourceReleaseManifestCount
        tierOrder = document.tierOrder
        assets = document.assets
        variants = document.variants
        assetsByID = indexedAssets
        variantsByID = indexedVariants
    }

    public init(contentsOf url: URL, requireCompleteRelease: Bool = true) throws {
        let data: Data
        do {
            data = try Data(contentsOf: url, options: [.mappedIfSafe])
        } catch {
            throw ExperienceAssetCatalogError.unreadableCatalog(String(describing: error))
        }
        try self.init(data: data, requireCompleteRelease: requireCompleteRelease)
    }

    public func asset(id: String) -> ExperienceAssetRecord? {
        assetsByID[id]
    }

    public func variant(assetID: String, tier: VisualDetailTier) -> VisualDetailVariantRecord? {
        variantsByID["\(assetID)::\(tier.rawValue)"]
    }

    public func resolve(assetID: String, tier: VisualDetailTier) throws -> ResolvedExperienceAsset {
        guard let asset = assetsByID[assetID] else {
            throw ExperienceAssetCatalogError.unknownAsset(assetID)
        }
        guard let variant = variant(assetID: assetID, tier: tier) else {
            throw ExperienceAssetCatalogError.missingTier(assetID: assetID, tier: tier)
        }
        return ResolvedExperienceAsset(asset: asset, variant: variant)
    }

    public func assets(in category: ExperienceAssetCategory) -> [ExperienceAssetRecord] {
        assets.filter { $0.primaryCategory == category }
    }

    /// Paged access keeps the full library discoverable without ever constructing a 150-entity scene.
    public func page(
        category: ExperienceAssetCategory? = nil,
        offset: Int,
        limit: Int = 8
    ) -> [ExperienceAssetRecord] {
        let candidates = category.map(assets(in:)) ?? assets
        let safeOffset = min(max(0, offset), candidates.count)
        let safeLimit = min(max(1, limit), 8)
        return Array(candidates.dropFirst(safeOffset).prefix(safeLimit))
    }

    private struct CatalogDocument: Decodable {
        let catalogID: String
        let sourceReleaseAssetCount: Int
        let sourceReleaseManifestCount: Int
        let tierOrder: [VisualDetailTier]
        let virtualVariantCount: Int
        let assets: [ExperienceAssetRecord]
        let variants: [VisualDetailVariantRecord]

        private enum CodingKeys: String, CodingKey {
            case catalogID = "catalog_id"
            case sourceReleaseAssetCount = "source_release_asset_count"
            case sourceReleaseManifestCount = "source_release_manifest_count"
            case tierOrder = "tier_order"
            case virtualVariantCount = "virtual_variant_count"
            case assets
            case variants
        }
    }
}

public struct ExperienceAssetResourceLocator: Sendable {
    public let searchRoots: [URL]

    public init(searchRoots: [URL]) {
        self.searchRoots = searchRoots
    }

    /// Resolves the catalog's repository-relative path. Returns nil rather than substituting an
    /// unrelated model, so an unresolved binding fails closed.
    public func resolve(_ asset: ResolvedExperienceAsset) -> URL? {
        for root in searchRoots {
            let candidate = root.appendingPathComponent(asset.sourcePath)
            var isDirectory: ObjCBool = false
            if FileManager.default.fileExists(atPath: candidate.path, isDirectory: &isDirectory), !isDirectory.boolValue {
                return candidate
            }
        }
        return nil
    }
}
