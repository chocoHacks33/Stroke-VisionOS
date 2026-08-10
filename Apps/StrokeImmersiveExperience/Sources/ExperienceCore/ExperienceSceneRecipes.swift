import Foundation

public struct ExperienceSceneRecipeID: RawRepresentable, Codable, Sendable, Hashable, ExpressibleByStringLiteral {
    public let rawValue: String

    public init(rawValue: String) {
        self.rawValue = rawValue
    }

    public init(stringLiteral value: String) {
        rawValue = value
    }
}

public enum SceneAssetRole: String, Codable, Sendable, Hashable {
    case orientationShell
    case anatomyFocus
    case vascularFocus
    case pathologyFocus
    case qualitativeFlow
    case educationalTool
    case registeredState
    case clinicalContext
    case guidance
}

public struct SceneAssetBinding: Codable, Sendable, Hashable, Identifiable {
    public let assetID: String
    public let role: SceneAssetRole
    public let required: Bool
    public let initiallyVisible: Bool

    public var id: String { assetID }

    public init(
        _ assetID: String,
        role: SceneAssetRole,
        required: Bool = true,
        initiallyVisible: Bool = true
    ) {
        self.assetID = assetID
        self.role = role
        self.required = required
        self.initiallyVisible = initiallyVisible
    }
}

public struct ExperienceSceneRecipe: Codable, Sendable, Hashable, Identifiable {
    public static let maximumResidentAssets = 8

    public let id: ExperienceSceneRecipeID
    public let pathway: ExperiencePathwayID
    public let step: ExperienceProcedureStep?
    public let cameraPreset: ExperienceCameraPresetID
    public let assetBindings: [SceneAssetBinding]
    public let blackBackground: Bool
    public let userConfirmedEntry: Bool

    public init(
        id: ExperienceSceneRecipeID,
        pathway: ExperiencePathwayID,
        step: ExperienceProcedureStep?,
        cameraPreset: ExperienceCameraPresetID,
        assetBindings: [SceneAssetBinding],
        blackBackground: Bool = true,
        userConfirmedEntry: Bool = false
    ) {
        self.id = id
        self.pathway = pathway
        self.step = step
        self.cameraPreset = cameraPreset
        self.assetBindings = assetBindings
        self.blackBackground = blackBackground
        self.userConfirmedEntry = userConfirmedEntry
    }
}

public struct ResolvedSceneAssetBinding: Sendable, Hashable, Identifiable {
    public let binding: SceneAssetBinding
    public let asset: ResolvedExperienceAsset

    public var id: String { asset.id }
}

public struct ResolvedExperienceSceneRecipe: Sendable, Hashable, Identifiable {
    public let recipe: ExperienceSceneRecipe
    public let tier: VisualDetailTier
    public let assets: [ResolvedSceneAssetBinding]

    public var id: ExperienceSceneRecipeID { recipe.id }
}

public enum ExperienceSceneRecipeError: Error, LocalizedError, Sendable, Equatable {
    case duplicateAsset(recipeID: String, assetID: String)
    case loadBudgetExceeded(recipeID: String, count: Int, maximum: Int)
    case missingRequiredAsset(recipeID: String, assetID: String)
    case incompatibleComposition(recipeID: String, reason: String)
    case pathwayMismatch(recipeID: String)

    public var errorDescription: String? {
        switch self {
        case .duplicateAsset(let recipeID, let assetID):
            "Recipe \(recipeID) repeats asset \(assetID)."
        case .loadBudgetExceeded(let recipeID, let count, let maximum):
            "Recipe \(recipeID) requests \(count) assets; the limit is \(maximum)."
        case .missingRequiredAsset(let recipeID, let assetID):
            "Recipe \(recipeID) cannot resolve required asset \(assetID)."
        case .incompatibleComposition(let recipeID, let reason):
            "Recipe \(recipeID) contains an incompatible composition: \(reason)"
        case .pathwayMismatch(let recipeID):
            "Recipe \(recipeID) does not match the active pathway."
        }
    }
}

public struct ExperienceSceneRecipeLibrary: Sendable {
    public let recipesByStep: [ExperienceProcedureStep: ExperienceSceneRecipe]

    public init(recipesByStep: [ExperienceProcedureStep: ExperienceSceneRecipe] = Self.builtInByStep) {
        self.recipesByStep = recipesByStep
    }

    public func recipe(for step: ExperienceProcedureStep) -> ExperienceSceneRecipe? {
        recipesByStep[step]
    }

    public func resolve(
        _ recipe: ExperienceSceneRecipe,
        tier: VisualDetailTier,
        catalog: ExperienceAssetCatalog,
        safetyPolicy: ExperienceAssetSafetyPolicy = .init(),
        context: ExperienceContentUseContext = .developerPreview
    ) throws -> ResolvedExperienceSceneRecipe {
        try safetyPolicy.validate(recipe: recipe, catalog: catalog, context: context)

        var resolved: [ResolvedSceneAssetBinding] = []
        for binding in recipe.assetBindings {
            do {
                let asset = try catalog.resolve(assetID: binding.assetID, tier: tier)
                resolved.append(.init(binding: binding, asset: asset))
            } catch {
                if binding.required {
                    throw ExperienceSceneRecipeError.missingRequiredAsset(
                        recipeID: recipe.id.rawValue,
                        assetID: binding.assetID
                    )
                }
            }
        }

        return ResolvedExperienceSceneRecipe(recipe: recipe, tier: tier, assets: resolved)
    }

    public func resolve(
        _ recipe: ExperienceSceneRecipe,
        state: ProcedureExperienceState,
        catalog: ExperienceAssetCatalog,
        safetyPolicy: ExperienceAssetSafetyPolicy = .init(),
        context: ExperienceContentUseContext = .developerPreview
    ) throws -> ResolvedExperienceSceneRecipe {
        try safetyPolicy.validate(recipe: recipe, for: state, catalog: catalog, context: context)
        return try resolve(
            recipe,
            tier: state.detailTier,
            catalog: catalog,
            safetyPolicy: safetyPolicy,
            context: context
        )
    }

    /// Turns any page of the 150-entry catalog into a bounded inspection scene.
    public func catalogPageRecipe(
        catalog: ExperienceAssetCatalog,
        category: ExperienceAssetCategory? = nil,
        offset: Int
    ) -> ExperienceSceneRecipe {
        let maximum = Self.singleFocusCategories.contains(category)
            ? 1
            : ExperienceSceneRecipe.maximumResidentAssets
        let candidates = catalog.page(category: category, offset: offset, limit: maximum)
        let policy = ExperienceAssetSafetyPolicy()
        var selected: [ExperienceAssetRecord] = []
        var selectedIDs: Set<String> = []
        for candidate in candidates where policy.canCoexist(assetID: candidate.assetID, with: selectedIDs) {
            selected.append(candidate)
            selectedIDs.insert(candidate.assetID)
        }
        let categoryLabel = category?.rawValue ?? "ALL"
        return .init(
            id: .init(rawValue: "CATALOG_\(categoryLabel)_\(max(0, offset))"),
            pathway: .overview,
            step: nil,
            cameraPreset: .consultationOverview,
            assetBindings: selected.map { SceneAssetBinding($0.assetID, role: role(for: $0.primaryCategory)) }
        )
    }

    private static let singleFocusCategories: Set<ExperienceAssetCategory?> = [
        nil,
        .some(.pathologyMacro),
        .some(.microConceptual)
    ]

    private func role(for category: ExperienceAssetCategory) -> SceneAssetRole {
        switch category {
        case .anatomyCNSMacro, .anatomyHeadNeckSupport, .adaptivePresentation:
            .anatomyFocus
        case .anatomyVascular:
            .vascularFocus
        case .bloodFlowTeaching, .microConceptual:
            .qualitativeFlow
        case .pathologyMacro:
            .pathologyFocus
        case .toolsEndovascular, .toolsOpenCranial:
            .educationalTool
        case .openCranialAnatomyState, .compositeAssembly:
            .registeredState
        case .clinicalContext, .spatialEnvironment:
            .clinicalContext
        case .guidance:
            .guidance
        }
    }

    public static let builtInByStep: [ExperienceProcedureStep: ExperienceSceneRecipe] = [
        .caseSelect: .init(
            id: "CASE_SELECT_BLACK_SPACE",
            pathway: .overview,
            step: .caseSelect,
            cameraPreset: .consultationOverview,
            assetBindings: [
                .init("brain_orientation_calm_educational_v1", role: .anatomyFocus)
            ]
        ),
        .orientHead: .init(
            id: "ORIENT_LAYERED_HEAD",
            pathway: .overview,
            step: .orientHead,
            cameraPreset: .headOrientation,
            assetBindings: [
                .init("external_head_scalp_realistic_v2", role: .orientationShell),
                .init("skull_semantic_realistic_v2", role: .orientationShell, initiallyVisible: false),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus, initiallyVisible: false),
                .init("cerebral_arteries_realistic_v2", role: .vascularFocus, initiallyVisible: false)
            ]
        ),
        .explainStroke: .init(
            id: "EXPLAIN_STROKE_CUTAWAY",
            pathway: .overview,
            step: .explainStroke,
            cameraPreset: .transparentHead,
            assetBindings: [
                .init("external_head_scalp_cutaway_v2", role: .orientationShell),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus),
                .init("cerebral_arteries_realistic_v2", role: .vascularFocus),
                .init("ischemic_mca_clot_v2", role: .pathologyFocus),
                .init("circle_of_willis_flow_overlay_v2", role: .qualitativeFlow)
            ]
        ),
        .evtVascularPath: .init(
            id: "EVT_VASCULAR_PATH",
            pathway: .endovascular,
            step: .evtVascularPath,
            cameraPreset: .vascularRoute,
            assetBindings: [
                .init("external_head_scalp_cutaway_v2", role: .orientationShell),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus),
                .init("neck_access_arteries_realistic_v2", role: .vascularFocus),
                .init("cerebral_arteries_realistic_v2", role: .vascularFocus),
                .init("circle_of_willis_flow_overlay_v2", role: .qualitativeFlow)
            ]
        ),
        .evtOcclusion: .init(
            id: "EVT_OCCLUSION_FOCUS",
            pathway: .endovascular,
            step: .evtOcclusion,
            cameraPreset: .occlusionCloseup,
            assetBindings: [
                .init("external_head_scalp_cutaway_v2", role: .orientationShell),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus),
                .init("cerebral_arteries_realistic_v2", role: .vascularFocus),
                .init("ischemic_mca_clot_v2", role: .pathologyFocus),
                .init("circle_of_willis_flow_overlay_v2", role: .qualitativeFlow)
            ]
        ),
        .evtDeviceConcept: .init(
            id: "EVT_DETACHED_DEVICE_CONCEPT",
            pathway: .endovascular,
            step: .evtDeviceConcept,
            cameraPreset: .deviceConcept,
            assetBindings: [
                .init("stent_retriever_educational_v2", role: .educationalTool)
            ],
            userConfirmedEntry: true
        ),
        .evtPostTreatmentComparison: .init(
            id: "EVT_FLOW_STATE_COMPARISON",
            pathway: .endovascular,
            step: .evtPostTreatmentComparison,
            cameraPreset: .illustrativeFlowComparison,
            assetBindings: [
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus),
                .init("cerebral_arteries_realistic_v2", role: .vascularFocus),
                .init("ischemic_mca_clot_v2", role: .pathologyFocus, initiallyVisible: false),
                .init("cerebral_bloodflow_animation_v2", role: .qualitativeFlow)
            ]
        ),
        .evtRecoveryOverview: .init(
            id: "EVT_RECOVERY_CONTEXT",
            pathway: .endovascular,
            step: .evtRecoveryOverview,
            cameraPreset: .recoveryOverview,
            assetBindings: [
                .init("patient_supine_generic", role: .clinicalContext)
            ]
        ),
        .openConfirmSite: .init(
            id: "OPEN_CONFIRM_SITE_NON_GRAPHIC",
            pathway: .openCranial,
            step: .openConfirmSite,
            cameraPreset: .openAccessOverview,
            assetBindings: [
                .init("external_head_scalp_realistic_v2", role: .orientationShell),
                .init("skull_semantic_realistic_v2", role: .orientationShell, initiallyVisible: false),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus, initiallyVisible: false),
                .init("intracerebral_hematoma_registered_conceptual_v1", role: .pathologyFocus, initiallyVisible: false)
            ],
            userConfirmedEntry: true
        ),
        .openCranialAccess: .init(
            id: "OPEN_CRANIAL_ACCESS_STATE_SWAP",
            pathway: .openCranial,
            step: .openCranialAccess,
            cameraPreset: .openLayerFocus,
            assetBindings: [
                .init("scalp_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("cranial_bone_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus),
                .init("intracerebral_hematoma_registered_conceptual_v1", role: .pathologyFocus)
            ],
            userConfirmedEntry: true
        ),
        .openDuralAccess: .init(
            id: "OPEN_DURAL_ACCESS_STATE_SWAP",
            pathway: .openCranial,
            step: .openDuralAccess,
            cameraPreset: .openLayerFocus,
            assetBindings: [
                .init("scalp_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("cranial_bone_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("dural_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus),
                .init("intracerebral_hematoma_registered_conceptual_v1", role: .pathologyFocus)
            ],
            userConfirmedEntry: true
        ),
        .openTreatReviewedCondition: .init(
            id: "OPEN_REVIEWED_CONDITION_STATE_SWAP",
            pathway: .openCranial,
            step: .openTreatReviewedCondition,
            cameraPreset: .openLayerFocus,
            assetBindings: [
                .init("dural_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus),
                .init("intracerebral_hematoma_registered_conceptual_v1", role: .pathologyFocus)
            ],
            userConfirmedEntry: true
        ),
        .openReplaceAndFixBoneFlap: .init(
            id: "OPEN_CLOSURE_STATE_SWAP",
            pathway: .openCranial,
            step: .openReplaceAndFixBoneFlap,
            cameraPreset: .closureComparison,
            assetBindings: [
                .init("dural_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("cranial_bone_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("scalp_access_closure_registered_conceptual_v1", role: .registeredState),
                .init("brain_anatomy_realistic_v2", role: .anatomyFocus)
            ],
            userConfirmedEntry: true
        ),
        .openPostClosureReview: .init(
            id: "OPEN_POST_CLOSURE_CONTEXT",
            pathway: .openCranial,
            step: .openPostClosureReview,
            cameraPreset: .recoveryOverview,
            assetBindings: [
                .init("patient_supine_generic", role: .clinicalContext)
            ]
        )
    ]

    public static let arteryLumenRecipe = ExperienceSceneRecipe(
        id: "CONCEPTUAL_ARTERY_LUMEN",
        pathway: .endovascular,
        step: nil,
        cameraPreset: .arteryLumenConcept,
        assetBindings: [
            .init("artery_wall_cutaway_v2", role: .anatomyFocus),
            .init("artery_interior_bloodflow_v2", role: .qualitativeFlow),
            .init("red_blood_cells_closeup_v2", role: .qualitativeFlow)
        ],
        userConfirmedEntry: true
    )

    public static let microcirculationRecipe = ExperienceSceneRecipe(
        id: "CONCEPTUAL_MICROCIRCULATION",
        pathway: .endovascular,
        step: nil,
        cameraPreset: .microcirculationConcept,
        assetBindings: [
            .init("microcirculation_arterial_venous_v2", role: .qualitativeFlow)
        ],
        userConfirmedEntry: true
    )
}

public struct ResidentExperienceAsset: Sendable, Hashable {
    public let assetID: String
    public let tier: VisualDetailTier

    public init(assetID: String, tier: VisualDetailTier) {
        self.assetID = assetID
        self.tier = tier
    }
}

public struct SceneResidencyPlan: Sendable, Hashable {
    public let unloadAssetIDs: [String]
    public let loadAssets: [ResolvedSceneAssetBinding]
    public let reconfigureAssets: [ResolvedSceneAssetBinding]
    public let retainedAssetIDs: [String]

    public init(
        unloadAssetIDs: [String],
        loadAssets: [ResolvedSceneAssetBinding],
        reconfigureAssets: [ResolvedSceneAssetBinding],
        retainedAssetIDs: [String]
    ) {
        self.unloadAssetIDs = unloadAssetIDs
        self.loadAssets = loadAssets
        self.reconfigureAssets = reconfigureAssets
        self.retainedAssetIDs = retainedAssetIDs
    }
}

public enum ExperienceAssetResidencyPlanner {
    /// Generates a diff so the host loads only the next bounded scene and reapplies sidecars on a
    /// tier change without re-reading unchanged USDZ geometry.
    public static func plan(
        current: [String: VisualDetailTier],
        next: ResolvedExperienceSceneRecipe
    ) -> SceneResidencyPlan {
        let nextByID = Dictionary(uniqueKeysWithValues: next.assets.map { ($0.asset.asset.assetID, $0) })
        let currentIDs = Set(current.keys)
        let nextIDs = Set(nextByID.keys)

        let unload = currentIDs.subtracting(nextIDs).sorted()
        let load = nextIDs.subtracting(currentIDs).sorted().compactMap { nextByID[$0] }
        let reconfigure = currentIDs.intersection(nextIDs).sorted().compactMap { id -> ResolvedSceneAssetBinding? in
            guard current[id] != next.tier else { return nil }
            return nextByID[id]
        }
        let retained = currentIDs.intersection(nextIDs).subtracting(Set(reconfigure.map { $0.asset.asset.assetID })).sorted()

        return .init(
            unloadAssetIDs: unload,
            loadAssets: load,
            reconfigureAssets: reconfigure,
            retainedAssetIDs: retained
        )
    }
}
