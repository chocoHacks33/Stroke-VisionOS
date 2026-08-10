import Foundation

private enum SmokeTestFailure: Error, CustomStringConvertible {
    case assertion(String)

    var description: String {
        switch self {
        case .assertion(let message): "SMOKE TEST FAILED: \(message)"
        }
    }
}

@main
private enum ExperienceCoreSmokeMain {
    static func main() throws {
        guard CommandLine.arguments.count == 2 else {
            throw SmokeTestFailure.assertion("pass the repository root as the only argument")
        }
        let root = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
        let catalogURL = root.appendingPathComponent(
            "RealityKitContent/InterfaceMedia/visual_detail_variants_v1/visual_detail_variant_catalog_v1.json"
        )
        let catalog = try ExperienceAssetCatalog(contentsOf: catalogURL)
        try expect(catalog.assets.count == 150, "catalog must expose all 150 assets")
        try expect(catalog.variants.count == 450, "catalog must expose all 450 tier bindings")

        var pagedIDs: Set<String> = []
        for offset in stride(from: 0, to: catalog.assets.count, by: 8) {
            let page = catalog.page(offset: offset, limit: 8)
            try expect(page.count <= 8, "catalog page exceeded eight items")
            pagedIDs.formUnion(page.map(\.assetID))
        }
        try expect(pagedIDs.count == 150, "paged library must retain all 150 asset ids")

        for asset in catalog.assets {
            let minimal = try catalog.resolve(assetID: asset.assetID, tier: .minimal)
            let reduced = try catalog.resolve(assetID: asset.assetID, tier: .reduced80)
            let full = try catalog.resolve(assetID: asset.assetID, tier: .full)
            try expect(minimal.sourcePath == reduced.sourcePath && reduced.sourcePath == full.sourcePath,
                       "tier sidecars must resolve the same source geometry for \(asset.assetID)")
            try expect(minimal.presentation.semanticDensityTarget <= reduced.presentation.semanticDensityTarget,
                       "minimal semantic density exceeded reduced80 for \(asset.assetID)")
            try expect(reduced.presentation.semanticDensityTarget <= full.presentation.semanticDensityTarget,
                       "reduced80 semantic density exceeded full for \(asset.assetID)")
            try expect(!minimal.variant.geometryMutationAllowed && !reduced.variant.geometryMutationAllowed
                       && !full.variant.geometryMutationAllowed,
                       "geometry mutation was enabled for \(asset.assetID)")
        }

        let selector = VisualDetailTierSelector()
        try expect(selector.select(detailAmount: 0.39, previous: .minimal) == .minimal,
                   "minimal hysteresis boundary changed")
        try expect(selector.select(detailAmount: 0.40, previous: .minimal) == .reduced80,
                   "minimal-to-reduced boundary changed")
        try expect(selector.select(detailAmount: 0.85, previous: .full) == .full,
                   "full hysteresis should retain full above leave threshold")
        try expect(selector.select(detailAmount: 0.82, previous: .full) == .reduced80,
                   "full-to-reduced boundary changed")

        let policy = ExperienceAssetSafetyPolicy()
        let library = ExperienceSceneRecipeLibrary()
        for recipe in library.recipesByStep.values {
            try expect(recipe.assetBindings.count <= ExperienceSceneRecipe.maximumResidentAssets,
                       "\(recipe.id.rawValue) exceeds the residency limit")
            try policy.validate(recipe: recipe, catalog: catalog)
            _ = try library.resolve(recipe, tier: .minimal, catalog: catalog)
            _ = try library.resolve(recipe, tier: .reduced80, catalog: catalog)
            _ = try library.resolve(recipe, tier: .full, catalog: catalog)
        }
        try policy.validate(recipe: ExperienceSceneRecipeLibrary.arteryLumenRecipe, catalog: catalog)
        try policy.validate(recipe: ExperienceSceneRecipeLibrary.microcirculationRecipe, catalog: catalog)

        let deviceRecipe = try require(library.recipe(for: .evtDeviceConcept), "missing EVT device recipe")
        try expect(deviceRecipe.assetBindings.count == 1,
                   "EVT device vignette must have one detached focus")
        try expect(deviceRecipe.assetBindings.first?.assetID == "stent_retriever_educational_v2",
                   "EVT device vignette must not mix vessel, clot, and comparison-layout domains")
        let openConfirmRecipe = try require(library.recipe(for: .openConfirmSite), "missing open-confirm recipe")
        try expect(openConfirmRecipe.assetBindings.filter { $0.role == .pathologyFocus }.count <= 1,
                   "open-confirm Layers toggle could reveal competing pathology states")
        for recipe in library.recipesByStep.values {
            let ids = Set(recipe.assetBindings.map(\.assetID))
            try expect(!ids.contains("spatial_step_markers"),
                       "step markers are SwiftUI-owned and must not affect model fitting")
            try expect(!ids.contains("round_spatial_display_dais_v1"),
                       "the UI-owned dais must not affect model fitting")
            try expect(!ids.contains("microscope_microinstrument_tray_open_neurosurgery_v3"),
                       "detached tool trays must not be co-loaded with registered head scenes")
        }
        let evtVascularRecipe = try require(library.recipe(for: .evtVascularPath), "missing EVT vascular recipe")
        try expect(!evtVascularRecipe.assetBindings.map(\.assetID).contains("catheter_body_to_brain_route"),
                   "legacy conceptual body route must remain a detached catalog item")
        let evtRecoveryRecipe = try require(library.recipe(for: .evtRecoveryOverview), "missing EVT recovery recipe")
        try expect(evtRecoveryRecipe.assetBindings.map(\.assetID) == ["patient_supine_generic"],
                   "EVT recovery must use one registered-safe context focus")

        try expectRejected(
            .init(id: "BAD_ASSEMBLY_OVERLAP", pathway: .endovascular, step: nil,
                  cameraPreset: .deviceConcept, assetBindings: [
                    .init("artery_cutaway_complete_v2", role: .registeredState),
                    .init("artery_wall_cutaway_v2", role: .anatomyFocus)
                  ]),
            catalog: catalog,
            policy: policy,
            reason: "assembly plus constituent must fail"
        )
        try expectRejected(
            .init(id: "BAD_OPEN_IN_EVT", pathway: .endovascular, step: nil,
                  cameraPreset: .headOrientation, assetBindings: [
                    .init("scalp_access_closure_registered_conceptual_v1", role: .registeredState)
                  ]),
            catalog: catalog,
            policy: policy,
            reason: "open state in EVT must fail"
        )
        try expectRejected(
            .init(id: "BAD_DRESSING_IN_EVT", pathway: .endovascular, step: nil,
                  cameraPreset: .recoveryOverview, assetBindings: [
                    .init("postoperative_head_dressing", role: .clinicalContext)
                  ]),
            catalog: catalog,
            policy: policy,
            reason: "EVT dressing must fail"
        )
        try expectRejected(
            .init(id: "BAD_DOUBLE_PATHOLOGY", pathway: .openCranial, step: nil,
                  cameraPreset: .openLayerFocus, assetBindings: [
                    .init("intracerebral_hematoma_registered_conceptual_v1", role: .pathologyFocus),
                    .init("cerebral_edema_registered_conceptual_v1", role: .pathologyFocus)
                  ]),
            catalog: catalog,
            policy: policy,
            reason: "two visible pathology focuses must fail"
        )
        try expectRejected(
            .init(id: "BAD_HEAD_MICRO_MIX", pathway: .endovascular, step: nil,
                  cameraPreset: .occlusionCloseup, assetBindings: [
                    .init("ischemic_tissue_zones_conceptual_v3", role: .pathologyFocus)
                  ]),
            catalog: catalog,
            policy: policy,
            reason: "micro asset in head scene must fail"
        )

        var patientMachine = ProcedureExperienceStateMachine(audience: .patient)
        patientMachine.beginEndovascularEducationalPathway()
        let orientationRecipe = try require(library.recipe(for: .orientHead), "missing orientation recipe")
        do {
            _ = try library.resolve(
                orientationRecipe,
                state: patientMachine.state,
                catalog: catalog,
                context: .developerPreview
            )
            throw SmokeTestFailure.assertion("patient state accepted a developer-preview context")
        } catch is ExperienceSceneRecipeError {
            // Expected.
        }
        let invalidPatientGate = ReviewedPathwayAuthorization(
            pathway: .openCranial,
            reviewedScenarioID: "developer-placeholder",
            reviewedContentRevision: "unapproved",
            audience: .patient
        )
        do {
            try patientMachine.beginOpenCranialEducationalPathway(authorization: invalidPatientGate)
            throw SmokeTestFailure.assertion("patient audience bypassed the open-cranial gate")
        } catch is ProcedureExperienceError {
            // Expected.
        }

        var developerMachine = ProcedureExperienceStateMachine(audience: .developer)
        developerMachine.beginEndovascularEducationalPathway()
        _ = try library.resolve(
            orientationRecipe,
            state: developerMachine.state,
            catalog: catalog,
            context: .developerPreview
        )
        let evtTools = Set(ExperienceToolboxPolicy.availableTools(for: developerMachine.state).map(\.id))
        try expect(evtTools.isDisjoint(with: ExperienceToolboxPolicy.openCranialTools),
                   "EVT toolbox exposed an open-cranial tool")

        let validDeveloperGate = ReviewedPathwayAuthorization(
            pathway: .openCranial,
            reviewedScenarioID: "local-developer-preview",
            reviewedContentRevision: "catalog-6127cf3",
            audience: .developer
        )
        try developerMachine.beginOpenCranialEducationalPathway(authorization: validDeveloperGate)
        try developerMachine.next()
        let openTools = Set(ExperienceToolboxPolicy.availableTools(for: developerMachine.state).map(\.id))
        try expect(openTools.contains(.openAccessStatePreview), "authorized open branch lacks state-preview tool")

        let annotations = ExperienceAnnotationCatalog()
        try expect(annotations.notes(for: .evtOcclusion, tier: .full).isEmpty,
                   "placeholder copy must fail closed without developer authorization")
        let previewNotes = annotations.notes(
            for: .evtOcclusion,
            tier: .full,
            authorization: .developerPreviewPlaceholders
        )
        try expect(!previewNotes.isEmpty, "developer placeholder authorization did not expose notes")
        try expect(previewNotes.allSatisfy { $0.annotation.anchorRequestID == nil },
                   "placeholder notes must remain detached from null anchor contracts")

        let orientRecipe = try require(library.recipe(for: .orientHead), "missing orientation recipe")
        let minimalScene = try library.resolve(orientRecipe, tier: .minimal, catalog: catalog)
        let resident = Dictionary(uniqueKeysWithValues: minimalScene.assets.map { ($0.asset.asset.assetID, VisualDetailTier.minimal) })
        let fullScene = try library.resolve(orientRecipe, tier: .full, catalog: catalog)
        let plan = ExperienceAssetResidencyPlanner.plan(current: resident, next: fullScene)
        try expect(plan.loadAssets.isEmpty && plan.unloadAssetIDs.isEmpty,
                   "tier change should not reload unchanged geometry")
        try expect(plan.reconfigureAssets.count == fullScene.assets.count,
                   "tier change must reapply every active sidecar")

        print("ExperienceCore smoke tests passed: 150 assets, 450 variants, \(library.recipesByStep.count) step recipes.")
    }

    private static func expect(_ condition: @autoclosure () -> Bool, _ message: String) throws {
        if !condition() { throw SmokeTestFailure.assertion(message) }
    }

    private static func require<T>(_ value: T?, _ message: String) throws -> T {
        guard let value else { throw SmokeTestFailure.assertion(message) }
        return value
    }

    private static func expectRejected(
        _ recipe: ExperienceSceneRecipe,
        catalog: ExperienceAssetCatalog,
        policy: ExperienceAssetSafetyPolicy,
        reason: String
    ) throws {
        do {
            try policy.validate(recipe: recipe, catalog: catalog)
            throw SmokeTestFailure.assertion(reason)
        } catch is ExperienceSceneRecipeError {
            // Expected.
        }
    }
}
