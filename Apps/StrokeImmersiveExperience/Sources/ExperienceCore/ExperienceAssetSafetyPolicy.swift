import Foundation

public enum ExperienceContentUseContext: String, Codable, Sendable, Hashable {
    /// Local Simulator/device engineering work only. Every scene must retain its developer-preview disclosure.
    case developerPreview
    /// A clinician-facilitated review of developer-preview content; this is not a clinical approval state.
    case clinicianFacilitatedDeveloperPreview
    /// Fails closed while the release catalog marks its variants as unauthorized for patient display.
    case patientOrFamilyDisplay
}

public struct ExperienceAssetSafetyPolicy: Sendable {
    public init() {}

    public func validate(
        recipe: ExperienceSceneRecipe,
        catalog: ExperienceAssetCatalog,
        context: ExperienceContentUseContext = .developerPreview
    ) throws {
        let ids = recipe.assetBindings.map(\.assetID)
        let uniqueIDs = Set(ids)
        if ids.count != uniqueIDs.count {
            let duplicate = Dictionary(grouping: ids, by: { $0 })
                .first(where: { $0.value.count > 1 })?.key ?? "unknown"
            throw ExperienceSceneRecipeError.duplicateAsset(
                recipeID: recipe.id.rawValue,
                assetID: duplicate
            )
        }
        guard ids.count <= ExperienceSceneRecipe.maximumResidentAssets else {
            throw ExperienceSceneRecipeError.loadBudgetExceeded(
                recipeID: recipe.id.rawValue,
                count: ids.count,
                maximum: ExperienceSceneRecipe.maximumResidentAssets
            )
        }

        if let step = recipe.step, step.pathway != recipe.pathway {
            throw ExperienceSceneRecipeError.pathwayMismatch(recipeID: recipe.id.rawValue)
        }

        let records = try ids.map { id -> ExperienceAssetRecord in
            guard let record = catalog.asset(id: id) else {
                throw ExperienceSceneRecipeError.missingRequiredAsset(
                    recipeID: recipe.id.rawValue,
                    assetID: id
                )
            }
            return record
        }

        if context == .patientOrFamilyDisplay {
            for record in records {
                guard catalog.variant(assetID: record.assetID, tier: .full)?.patientDisplayAuthorized == true else {
                    throw ExperienceSceneRecipeError.incompatibleComposition(
                        recipeID: recipe.id.rawValue,
                        reason: "\(record.assetID) is not authorized for patient/family display"
                    )
                }
            }
        }

        if !recipe.id.rawValue.hasPrefix("CATALOG_") {
            try validatePathwayCategories(recipe: recipe, records: records)
        }
        try validateAssemblyExclusions(recipe: recipe, assetIDs: uniqueIDs)
        try validatePathologyFocus(recipe: recipe)
        try validateScaleDomains(recipe: recipe, records: records)
    }

    public func validate(
        recipe: ExperienceSceneRecipe,
        for state: ProcedureExperienceState,
        catalog: ExperienceAssetCatalog,
        context: ExperienceContentUseContext = .developerPreview
    ) throws {
        switch state.audience {
        case .patient, .family:
            guard context == .patientOrFamilyDisplay else {
                throw ExperienceSceneRecipeError.incompatibleComposition(
                    recipeID: recipe.id.rawValue,
                    reason: "patient/family state cannot use a developer-preview authorization context"
                )
            }
        case .clinicianFacilitated:
            guard context == .clinicianFacilitatedDeveloperPreview else {
                throw ExperienceSceneRecipeError.incompatibleComposition(
                    recipeID: recipe.id.rawValue,
                    reason: "clinician-facilitated state requires its matching developer-preview context"
                )
            }
        case .developer:
            guard context == .developerPreview else {
                throw ExperienceSceneRecipeError.incompatibleComposition(
                    recipeID: recipe.id.rawValue,
                    reason: "developer state requires the developer-preview context"
                )
            }
        }
        try validate(recipe: recipe, catalog: catalog, context: context)

        if recipe.pathway == .openCranial {
            guard state.selectedPathway == .openCranial,
                  state.openCranialAuthorization?.isValidForOpenCranial == true else {
                throw ExperienceSceneRecipeError.pathwayMismatch(recipeID: recipe.id.rawValue)
            }
        } else if recipe.pathway == .endovascular {
            guard state.selectedPathway == .endovascular else {
                throw ExperienceSceneRecipeError.pathwayMismatch(recipeID: recipe.id.rawValue)
            }
        }
    }

    public func canCoexist(assetID: String, with activeAssetIDs: Set<String>) -> Bool {
        guard !activeAssetIDs.contains(assetID) else { return false }
        let candidateLeaves = Self.containedLeafAssetIDs[assetID] ?? [assetID]
        for activeID in activeAssetIDs {
            guard Self.containedLeafAssetIDs[assetID] != nil
                    || Self.containedLeafAssetIDs[activeID] != nil else { continue }
            let activeLeaves = Self.containedLeafAssetIDs[activeID] ?? [activeID]
            if !candidateLeaves.isDisjoint(with: activeLeaves) {
                return false
            }
        }
        return true
    }

    private func validatePathwayCategories(
        recipe: ExperienceSceneRecipe,
        records: [ExperienceAssetRecord]
    ) throws {
        let categories = Set(records.map(\.primaryCategory))

        switch recipe.pathway {
        case .overview:
            if !categories.isDisjoint(with: [.toolsOpenCranial, .openCranialAnatomyState]) {
                throw incompatible(recipe, "open-cranial states/tools cannot appear in the overview")
            }
        case .endovascular:
            if !categories.isDisjoint(with: [.toolsOpenCranial, .openCranialAnatomyState]) {
                throw incompatible(recipe, "ordinary EVT cannot load scalp, bone, dura, or open-cranial tools")
            }
            if records.contains(where: { $0.assetID == "postoperative_head_dressing" }) {
                throw incompatible(recipe, "the postoperative head dressing is not part of the EVT branch")
            }
            if records.contains(where: { Self.hemorrhageOrEdemaAssets.contains($0.assetID) }) {
                throw incompatible(recipe, "hemorrhage/edema assets cannot be mixed into the EVT branch")
            }
        case .openCranial:
            if categories.contains(.toolsEndovascular)
                || records.contains(where: { Self.ischemicAssets.contains($0.assetID) }) {
                throw incompatible(recipe, "endovascular tools or ischemic clot assets cannot be mixed into this open branch")
            }
        }
    }

    private func validateAssemblyExclusions(
        recipe: ExperienceSceneRecipe,
        assetIDs: Set<String>
    ) throws {
        let ids = assetIDs.sorted()
        for firstIndex in ids.indices {
            for secondIndex in ids.indices where secondIndex > firstIndex {
                let first = ids[firstIndex]
                let second = ids[secondIndex]
                guard Self.containedLeafAssetIDs[first] != nil
                        || Self.containedLeafAssetIDs[second] != nil else { continue }
                let firstLeaves = Self.containedLeafAssetIDs[first] ?? [first]
                let secondLeaves = Self.containedLeafAssetIDs[second] ?? [second]
                if !firstLeaves.isDisjoint(with: secondLeaves) {
                    throw incompatible(
                        recipe,
                        "\(first) and \(second) have overlapping registered/contained geometry"
                    )
                }
            }
        }
    }

    private func validatePathologyFocus(recipe: ExperienceSceneRecipe) throws {
        let pathologyBindings = recipe.assetBindings.filter { $0.role == .pathologyFocus }
        if pathologyBindings.count > 1 {
            throw incompatible(recipe, "only one pathology teaching focus may be resident at a time")
        }
    }

    private func validateScaleDomains(
        recipe: ExperienceSceneRecipe,
        records: [ExperienceAssetRecord]
    ) throws {
        let categories = Set(records.map(\.primaryCategory))
        if recipe.cameraPreset != .microcirculationConcept,
           categories.contains(.microConceptual) {
            throw incompatible(recipe, "micro-conceptual assets require a detached microcirculation vignette")
        }
        if recipe.cameraPreset == .arteryLumenConcept,
           categories.contains(.pathologyMacro) {
            throw incompatible(recipe, "macro pathology cannot be placed inside the detached artery-lumen vignette")
        }
        if recipe.cameraPreset == .microcirculationConcept,
           recipe.assetBindings.count > 1 {
            throw incompatible(recipe, "microcirculation focuses are loaded one at a time")
        }
        if recipe.cameraPreset == .deviceConcept,
           recipe.assetBindings.count != 1 {
            throw incompatible(recipe, "a detached device concept must contain exactly one focus asset")
        }
    }

    private func incompatible(_ recipe: ExperienceSceneRecipe, _ reason: String) -> ExperienceSceneRecipeError {
        .incompatibleComposition(recipeID: recipe.id.rawValue, reason: reason)
    }

    public static let ischemicAssets: Set<String> = [
        "ischemic_lvo_clot",
        "ischemic_mca_clot_v2",
        "ischemic_tissue_zones_conceptual_v3"
    ]

    public static let hemorrhageOrEdemaAssets: Set<String> = [
        "ich_hematoma",
        "edema_swelling",
        "intracerebral_hematoma_registered_conceptual_v1",
        "cerebral_edema_registered_conceptual_v1"
    ]

    /// An assembly is rendered instead of its constituent models, never on top of them.
    public static let containedLeafAssetIDs: [String: Set<String>] = [
        "thrombectomy_registered_hero_v2": [
            "brain_anatomy_realistic_v2", "brain_deep_structures_v2",
            "brain_ventricles_v2", "skull_semantic_realistic_v2",
            "eyes_context_realistic_v2", "cerebral_arteries_realistic_v2",
            "ischemic_mca_clot_v2"
        ],
        "meningeal_partitions_atlas_v2": [
            "falx_cerebri_atlas_v2", "tentorium_cerebelli_atlas_v2"
        ],
        "layered_head_cutaway_registered_v2": [
            "external_head_scalp_cutaway_v2", "dura_mater_cutaway_conceptual_v2",
            "falx_cerebri_atlas_v2", "tentorium_cerebelli_atlas_v2",
            "brain_anatomy_realistic_v2"
        ],
        "dural_sinuses_jugulars_realistic_v2": [
            "dural_venous_sinuses_realistic_v2", "internal_jugular_veins_realistic_v2"
        ],
        "head_neck_veins_expanded_realistic_v2": [
            "dural_venous_sinuses_realistic_v2", "internal_jugular_veins_realistic_v2",
            "head_neck_veins_supplemental_v2"
        ],
        "cranial_vascular_registered_assembly_v2": [
            "dural_venous_sinuses_realistic_v2", "internal_jugular_veins_realistic_v2",
            "head_neck_veins_supplemental_v2",
            "neck_access_arteries_realistic_v2"
        ],
        "artery_cutaway_complete_v2": [
            "artery_wall_cutaway_v2", "artery_interior_bloodflow_v2"
        ],
        "cerebral_bloodflow_teaching_set_v2": [
            "artery_wall_cutaway_v2", "artery_interior_bloodflow_v2",
            "circle_of_willis_flow_overlay_v2", "red_blood_cells_closeup_v2",
            "microcirculation_arterial_venous_v2"
        ],
        "thrombectomy_device_set_educational_v2": [
            "guidewire_educational_v2", "microcatheter_educational_v2",
            "aspiration_catheter_educational_v2", "stent_retriever_educational_v2"
        ],
        "neural_detail_registered_review_assembly_v3": [
            "brain_anatomy_realistic_v2", "brain_deep_structures_v2", "brain_ventricles_v2",
            "frontal_cortex_parcellation_v3", "parietal_cortex_parcellation_v3",
            "temporal_cortex_parcellation_v3", "occipital_cortex_parcellation_v3",
            "insular_opercular_cortex_v3", "cingulate_parahippocampal_cortex_v3",
            "cerebellar_substructures_v3", "brainstem_substructures_v3",
            "basal_ganglia_deep_nuclei_v3", "thalamic_hypothalamic_nuclei_v3",
            "hippocampal_amygdala_limbic_nuclei_v3", "ventricular_spaces_v3",
            "major_white_matter_regions_v3", "commissural_sensory_pathways_v3"
        ],
        "cranial_nerves_complete_assembly_v3": [
            "cranial_nerve_olfactory_i_bilateral_v3", "cranial_nerve_optic_ii_bilateral_v3",
            "cranial_nerves_ocular_motor_iii_iv_vi_v3", "cranial_nerve_trigeminal_v_expanded_v3",
            "cranial_nerve_facial_vii_bilateral_v3", "cranial_nerve_vestibulocochlear_viii_v3",
            "cranial_nerves_glossopharyngeal_ix_vagus_x_v3",
            "cranial_nerve_accessory_xi_bilateral_v3", "cranial_nerve_hypoglossal_xii_bilateral_v3"
        ],
        "intracranial_micro_teaching_set_v3": [
            "blood_brain_barrier_neurovascular_unit_conceptual_v3",
            "capillary_endothelium_tight_junctions_conceptual_v3",
            "formed_blood_elements_magnified_v3",
            "platelet_fibrin_thrombus_microstructure_conceptual_v3",
            "multipolar_neuron_detailed_conceptual_v3",
            "astrocyte_capillary_endfeet_conceptual_v3",
            "oligodendrocyte_myelinated_axons_conceptual_v3",
            "myelinated_axon_node_of_ranvier_conceptual_v3",
            "chemical_synapse_closeup_conceptual_v3",
            "choroid_plexus_csf_interface_conceptual_v3",
            "ischemic_tissue_zones_conceptual_v3"
        ],
        "vascular_access_setup_review_assembly_v3": [
            "vascular_access_needle_educational_v3", "vascular_access_wire_educational_v3",
            "introducer_sheath_dilator_set_educational_v3",
            "puncture_site_hemostasis_options_educational_v3"
        ],
        "endovascular_tools_workflow_review_assembly_v3": [
            "vascular_access_needle_educational_v3", "vascular_access_wire_educational_v3",
            "introducer_sheath_dilator_set_educational_v3",
            "guide_catheter_hemostatic_valve_educational_v3",
            "aspiration_pump_canister_tubing_educational_v3",
            "contrast_manifold_syringe_flush_educational_v3",
            "torque_device_y_connector_accessories_educational_v3",
            "puncture_site_hemostasis_options_educational_v3",
            "sterile_endovascular_instrument_tray_educational_v3",
            "angiography_suite_controls_educational_v3"
        ],
        "cranial_access_tools_review_assembly_open_neurosurgery_v3": [
            "surface_marking_ruler_set_open_neurosurgery_v3",
            "scalpel_dissector_set_open_neurosurgery_v3",
            "scalp_retractor_hemostat_set_open_neurosurgery_v3",
            "perforator_craniotome_system_open_neurosurgery_v3",
            "bone_flap_fixation_set_open_neurosurgery_v3"
        ],
        "intradural_closure_tools_review_assembly_open_neurosurgery_v3": [
            "dural_scissors_hooks_forceps_set_open_neurosurgery_v3",
            "bipolar_forceps_irrigation_set_open_neurosurgery_v3",
            "suction_microdissector_set_open_neurosurgery_v3",
            "brain_spatula_retractor_set_open_neurosurgery_v3",
            "microscope_microinstrument_tray_open_neurosurgery_v3",
            "dural_closure_suture_patch_set_open_neurosurgery_v3"
        ],
        "spatial_care_consultation_environment_assembly_v1": [
            "calm_consultation_room_shell_v1", "curved_feature_wall_architecture_v1",
            "modular_lounge_seating_set_v1", "consultation_armchair_pair_v1",
            "round_spatial_display_dais_v1", "low_table_side_table_set_v1",
            "clinical_credenza_storage_v1", "calm_botanical_planter_set_v1",
            "ambient_lighting_fixture_set_v1"
        ],
        "brain_orientation_calm_educational_v1": [
            "brain_structures_generic", "brain_anatomy_realistic_v2"
        ],
        "scalp_access_closure_registered_conceptual_v1": [
            "head_skin_generic", "external_head_scalp_realistic_v2",
            "external_head_scalp_cutaway_v2", "scalp_incision_flap", "scalp_closure_sutures"
        ],
        "cranial_bone_access_closure_registered_conceptual_v1": [
            "skull_cranium_generic", "skull_semantic_realistic_v2", "craniotomy_bone_flap"
        ],
        "dural_access_closure_registered_conceptual_v1": [
            "dura_mater_conceptual_v2", "dura_mater_cutaway_conceptual_v2", "dural_patch"
        ],
        "intracerebral_hematoma_registered_conceptual_v1": [
            "ich_hematoma"
        ],
        "cerebral_edema_registered_conceptual_v1": [
            "edema_swelling"
        ]
    ]

    /// Backwards-compatible public name for consumers that only need the replacement map.
    public static var assemblyComponentExclusions: [String: Set<String>] { containedLeafAssetIDs }
}
