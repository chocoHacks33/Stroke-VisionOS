#!/usr/bin/env python3
"""Build the deterministic visual-detail virtual-variant resource pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PACK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACK_ROOT.parents[2]
MODULE_ID = "visual_detail_variants_v1"
TIERS = ("minimal", "reduced80", "full")

SOURCE_MANIFESTS = (
    "RealityKitContent/Assets/vision_pro_stroke_kit/asset_manifest.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_head_details_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_cranial_vascular_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_bloodflow_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_devices_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_neural_detail_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_cranial_detail_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_intracranial_micro_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_endovascular_tools_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_open_cranial_tools_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_adaptive_visuals_v1.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_spatial_care_environment_v1.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_figma_page2_surgical_states_v1.json",
)

CATEGORY_ORDER = (
    "ANATOMY_CNS_MACRO",
    "ANATOMY_HEAD_NECK_SUPPORT",
    "ANATOMY_VASCULAR",
    "PATHOLOGY_MACRO",
    "BLOOD_FLOW_TEACHING",
    "MICRO_CONCEPTUAL",
    "TOOLS_ENDOVASCULAR",
    "TOOLS_OPEN_CRANIAL",
    "OPEN_CRANIAL_ANATOMY_STATE",
    "CLINICAL_CONTEXT",
    "SPATIAL_ENVIRONMENT",
    "GUIDANCE",
    "ADAPTIVE_PRESENTATION",
    "COMPOSITE_ASSEMBLY",
)

CATEGORY_MEMBER_TEXT = {
    "ANATOMY_CNS_MACRO": """
        basal_ganglia_deep_nuclei_v3 brain_anatomy_realistic_v2
        brain_deep_structures_v2 brain_structures_generic brain_ventricles_v2
        brainstem_substructures_v3 cerebellar_substructures_v3
        cingulate_parahippocampal_cortex_v3 commissural_sensory_pathways_v3
        frontal_cortex_parcellation_v3 hippocampal_amygdala_limbic_nuclei_v3
        insular_opercular_cortex_v3 major_white_matter_regions_v3
        occipital_cortex_parcellation_v3 parietal_cortex_parcellation_v3
        temporal_cortex_parcellation_v3 thalamic_hypothalamic_nuclei_v3
        ventricular_spaces_v3
    """,
    "ANATOMY_HEAD_NECK_SUPPORT": """
        cranial_nerve_accessory_xi_bilateral_v3
        cranial_nerve_facial_vii_bilateral_v3
        cranial_nerve_hypoglossal_xii_bilateral_v3
        cranial_nerve_olfactory_i_bilateral_v3
        cranial_nerve_optic_ii_bilateral_v3
        cranial_nerve_trigeminal_v_expanded_v3
        cranial_nerve_vestibulocochlear_viii_v3
        cranial_nerves_glossopharyngeal_ix_vagus_x_v3
        cranial_nerves_ocular_motor_iii_iv_vi_v3 dura_mater_conceptual_v2
        dura_mater_cutaway_conceptual_v2 external_head_scalp_cutaway_v2
        external_head_scalp_realistic_v2 extraocular_muscles_orbital_support_v3
        eyes_context_realistic_v2 falx_cerebri_atlas_v2
        head_neck_orientation_muscles_v3 head_skin_generic
        muscles_of_mastication_bilateral_v3 nasal_cavity_paranasal_spaces_v3
        pharyngeal_upper_airway_context_v3
        pituitary_adenohypophysis_neurohypophysis_v3 skull_cranium_generic
        skull_semantic_realistic_v2 tentorium_cerebelli_atlas_v2
    """,
    "ANATOMY_VASCULAR": """
        cerebral_arteries_generic cerebral_arteries_realistic_v2
        dural_venous_sinuses_realistic_v2 head_neck_veins_supplemental_v2
        internal_jugular_veins_realistic_v2 neck_access_arteries_realistic_v2
    """,
    "PATHOLOGY_MACRO": """
        cerebral_edema_registered_conceptual_v1 edema_swelling ich_hematoma
        intracerebral_hematoma_registered_conceptual_v1 ischemic_lvo_clot
        ischemic_mca_clot_v2
    """,
    "BLOOD_FLOW_TEACHING": """
        angiography_contrast_flow artery_interior_bloodflow_v2
        artery_wall_cutaway_v2 cerebral_bloodflow_animation_v2
        circle_of_willis_flow_overlay_v2 microcirculation_arterial_venous_v2
        red_blood_cells_closeup_v2
    """,
    "MICRO_CONCEPTUAL": """
        astrocyte_capillary_endfeet_conceptual_v3
        blood_brain_barrier_neurovascular_unit_conceptual_v3
        capillary_endothelium_tight_junctions_conceptual_v3
        chemical_synapse_closeup_conceptual_v3
        choroid_plexus_csf_interface_conceptual_v3
        formed_blood_elements_magnified_v3 ischemic_tissue_zones_conceptual_v3
        multipolar_neuron_detailed_conceptual_v3
        myelinated_axon_node_of_ranvier_conceptual_v3
        oligodendrocyte_myelinated_axons_conceptual_v3
        platelet_fibrin_thrombus_microstructure_conceptual_v3
    """,
    "TOOLS_ENDOVASCULAR": """
        angiography_suite_controls_educational_v3 arterial_access_site
        aspiration_catheter aspiration_catheter_educational_v2
        aspiration_pump_canister_tubing_educational_v3
        catheter_body_to_brain_route contrast_manifold_syringe_flush_educational_v3
        guide_catheter_hemostatic_valve_educational_v3 guidewire_educational_v2
        guidewire_microcatheter_set introducer_sheath_dilator_set_educational_v3
        microcatheter_educational_v2 puncture_site_hemostasis_options_educational_v3
        stent_retriever stent_retriever_educational_v2
        sterile_endovascular_instrument_tray_educational_v3
        torque_device_y_connector_accessories_educational_v3
        vascular_access_needle_educational_v3 vascular_access_wire_educational_v3
    """,
    "TOOLS_OPEN_CRANIAL": """
        bipolar_forceps_irrigation_set_open_neurosurgery_v3
        bone_flap_fixation_set_open_neurosurgery_v3
        brain_spatula_retractor_set_open_neurosurgery_v3
        conditional_csf_access_instrument_set_open_neurosurgery_v3
        cranial_drill_generic dural_closure_suture_patch_set_open_neurosurgery_v3
        dural_scissors_hooks_forceps_set_open_neurosurgery_v3
        microscope_microinstrument_tray_open_neurosurgery_v3
        minimally_invasive_evacuator_port optional_evd_system
        perforator_craniotome_system_open_neurosurgery_v3
        scalp_retractor_hemostat_set_open_neurosurgery_v3
        scalpel_dissector_set_open_neurosurgery_v3 suction_and_forceps
        suction_microdissector_set_open_neurosurgery_v3
        surface_marking_ruler_set_open_neurosurgery_v3
    """,
    "OPEN_CRANIAL_ANATOMY_STATE": """
        cranial_bone_access_closure_registered_conceptual_v1 craniotomy_bone_flap
        dural_access_closure_registered_conceptual_v1 dural_patch
        scalp_access_closure_registered_conceptual_v1 scalp_closure_sutures
        scalp_incision_flap
    """,
    "CLINICAL_CONTEXT": """
        angiography_c_arm angiography_operating_table clinical_team_generic
        iv_pole_and_bag patient_supine_generic postoperative_head_dressing
        vital_sign_monitor
    """,
    "SPATIAL_ENVIRONMENT": """
        ambient_lighting_fixture_set_v1 calm_botanical_planter_set_v1
        calm_consultation_room_shell_v1 clinical_credenza_storage_v1
        consultation_armchair_pair_v1 curved_feature_wall_architecture_v1
        low_table_side_table_set_v1 modular_lounge_seating_set_v1
        round_spatial_display_dais_v1
    """,
    "GUIDANCE": "spatial_step_markers",
    "ADAPTIVE_PRESENTATION": "brain_orientation_calm_educational_v1",
    "COMPOSITE_ASSEMBLY": """
        artery_cutaway_complete_v2 cerebral_bloodflow_teaching_set_v2
        cranial_access_tools_review_assembly_open_neurosurgery_v3
        cranial_nerves_complete_assembly_v3 cranial_vascular_registered_assembly_v2
        dural_sinuses_jugulars_realistic_v2
        endovascular_tools_workflow_review_assembly_v3
        head_neck_veins_expanded_realistic_v2
        intracranial_micro_teaching_set_v3
        intradural_closure_tools_review_assembly_open_neurosurgery_v3
        layered_head_cutaway_registered_v2 meningeal_partitions_atlas_v2
        neural_detail_registered_review_assembly_v3
        spatial_care_consultation_environment_assembly_v1
        thrombectomy_device_set_educational_v2 thrombectomy_registered_hero_v2
        vascular_access_setup_review_assembly_v3
    """,
}
CATEGORY_MEMBERS = {
    category: tuple(CATEGORY_MEMBER_TEXT[category].split()) for category in CATEGORY_ORDER
}

ASSEMBLY_DOMAINS = {
    "thrombectomy_registered_hero_v2": "MIXED_REGISTERED_HEAD",
    "neural_detail_registered_review_assembly_v3": "ANATOMY_CNS_MACRO",
    "meningeal_partitions_atlas_v2": "ANATOMY_HEAD_NECK_SUPPORT",
    "layered_head_cutaway_registered_v2": "ANATOMY_HEAD_NECK_SUPPORT",
    "cranial_nerves_complete_assembly_v3": "ANATOMY_HEAD_NECK_SUPPORT",
    "dural_sinuses_jugulars_realistic_v2": "ANATOMY_VASCULAR",
    "head_neck_veins_expanded_realistic_v2": "ANATOMY_VASCULAR",
    "cranial_vascular_registered_assembly_v2": "ANATOMY_VASCULAR",
    "artery_cutaway_complete_v2": "BLOOD_FLOW_TEACHING",
    "cerebral_bloodflow_teaching_set_v2": "BLOOD_FLOW_TEACHING",
    "intracranial_micro_teaching_set_v3": "MICRO_CONCEPTUAL",
    "thrombectomy_device_set_educational_v2": "TOOLS_ENDOVASCULAR",
    "vascular_access_setup_review_assembly_v3": "TOOLS_ENDOVASCULAR",
    "endovascular_tools_workflow_review_assembly_v3": "TOOLS_ENDOVASCULAR",
    "cranial_access_tools_review_assembly_open_neurosurgery_v3": "TOOLS_OPEN_CRANIAL",
    "intradural_closure_tools_review_assembly_open_neurosurgery_v3": "TOOLS_OPEN_CRANIAL",
    "spatial_care_consultation_environment_assembly_v1": "SPATIAL_ENVIRONMENT",
}

GLOBAL_MUST_PRESERVE = (
    "recognizable silhouette or a separately reviewed meaning-equivalent proxy",
    "selected learning objective and all material medical facts",
    "laterality, registration, pathology type, pathway, and closure branch",
    "conceptual, nonquantitative, magnification, uncertainty, and scale warnings",
    "accessible text equivalent and immediate restore-original control",
)
GLOBAL_PROHIBITED = (
    "destructive source USDZ edits or unreviewed generated replacement geometry",
    "anxiety, emotion, gaze, pupil, joint-motion, biometric, or sensor inference",
    "changing clinical pathway, laterality, registration, lesion meaning, or outcome",
    "hiding material facts or treating visual reduction as clinical recommendation",
    "patient display while patient_display_authorized is false",
)


def category_policy(
    category: str,
    preserve: list[str],
    reduced: list[str],
    minimal: list[str],
) -> dict[str, Any]:
    return {
        "category_id": category,
        "asset_count": len(CATEGORY_MEMBERS[category]),
        "must_preserve": preserve,
        "tiers": {
            "minimal": {
                "semantic_density": "smallest_reviewed_complete_explanation",
                "strategy": minimal,
                "virtual_reversible_sidecar": True,
            },
            "reduced80": {
                "semantic_density_target": 0.8,
                "strategy": reduced,
                "virtual_reversible_sidecar": True,
            },
            "full": {
                "source_asset_unchanged": True,
                "strategy": ["Bind the exact observed source USDZ bytes and SHA-256 without geometry or material mutation."],
            },
        },
    }


CATEGORY_POLICIES = {
    "ANATOMY_CNS_MACRO": category_policy(
        "ANATOMY_CNS_MACRO",
        ["CNS silhouette and orientation", "selected structure identity", "laterality and atlas/generic warning"],
        ["Show broad landmarks plus the selected focus.", "Hide secondary parcels and labels with opaque swaps; avoid stacked transparency."],
        ["Show a brain/cerebellum/brainstem silhouette plus one required structure.", "Keep deep or pathway anatomy only when it is the active learning objective."],
    ),
    "ANATOMY_HEAD_NECK_SUPPORT": category_policy(
        "ANATOMY_HEAD_NECK_SUPPORT",
        ["head/skull/meningeal silhouette", "selected support structure and bilateral identity", "registered relationship"],
        ["Show one support family at a time.", "Prefer major nerve trunks or an opaque cutaway; hide nonessential distal detail."],
        ["Show the closed exterior or one orientation shell plus the selected support structure.", "If a cranial nerve is the objective, retain that nerve and its text equivalent."],
    ),
    "ANATOMY_VASCULAR": category_policy(
        "ANATOMY_VASCULAR",
        ["arterial versus venous class", "selected route and direction", "laterality and conceptual color warning"],
        ["Retain the selected major route and cull irrelevant branches.", "Reduce labels and material glow without changing route identity."],
        ["Show one static origin-to-focus route or selected vessel silhouette.", "Keep arterial/venous and laterality text visible."],
    ),
    "PATHOLOGY_MACRO": category_policy(
        "PATHOLOGY_MACRO",
        ["pathology type", "registered focus and laterality", "conceptual/nonquantitative and uncertainty warning"],
        ["Use a muted solid cue and remove graphic surface detail or particles.", "Retain the reviewed focus and pathology disclosure."],
        ["Use a non-graphic halo or region marker plus the pathology type.", "Do not imply measured extent, severity, pressure, target, or outcome."],
    ),
    "BLOOD_FLOW_TEACHING": category_policy(
        "BLOOD_FLOW_TEACHING",
        ["qualitative direction", "baseline/restricted/restored state", "non-CFD and nonquantitative warning"],
        ["Reduce cell, arrow, pulse, glow, and label density while retaining direction.", "Slow or disable motion according to explicit motion preference."],
        ["Use a static directional path with two or three markers and a text equivalent.", "Hide blood cells and animation; never expose pressure, velocity, perfusion, or CFD values."],
    ),
    "MICRO_CONCEPTUAL": category_policy(
        "MICRO_CONCEPTUAL",
        ["representative mechanism", "separate microscopic presentation root", "persistent magnification/conceptual/non-patient warning"],
        ["Reduce repeated cells, filaments, particles, and labels.", "Retain the canonical elements required to explain the selected relation."],
        ["Show one representative element and one schematic relationship.", "Never overlay or scale-match the vignette to the head."],
    ),
    "TOOLS_ENDOVASCULAR": category_policy(
        "TOOLS_ENDOVASCULAR",
        ["tool category and conditional status", "EVT pathway gate", "non-device-specific and non-training warning"],
        ["Show the active tool category plus at most one necessary connector or context item.", "Hide trays, accessories, duplicate variants, and unselected techniques."],
        ["Use a detached simplified silhouette or reviewed proxy plus category text.", "Show no anatomy contact, route motion, sizing, compatibility, or technique cue."],
    ),
    "TOOLS_OPEN_CRANIAL": category_policy(
        "TOOLS_OPEN_CRANIAL",
        ["tool category and conditional status", "open-neurosurgery/EVD gates", "non-device-specific and non-training warning"],
        ["Show only the active category and mute sharp visual detail.", "Keep tools detached unless an exact reviewed placement exists; hide tissue contact."],
        ["Use a detached outline/proxy or native category card.", "Show no exposed-tissue contact, trajectory, force, energy, pressure, or technique."],
    ),
    "OPEN_CRANIAL_ANATOMY_STATE": category_policy(
        "OPEN_CRANIAL_ANATOMY_STATE",
        ["open versus closed state", "craniotomy-replace versus craniectomy-leave-off", "open-neurosurgery gate and non-graphic warning"],
        ["Show one opaque muted access or closure state at a time.", "Use static or slowed host-owned flap motion and no tissue physics."],
        ["Use a closed-head cue or schematic cap/outline rather than graphic tissue.", "Preserve branch-correct closure and reject every asset in ordinary EVT."],
    ),
    "CLINICAL_CONTEXT": category_policy(
        "CLINICAL_CONTEXT",
        ["only context required by the lesson", "privacy, modesty, and fictional/generic status", "no operational monitor/equipment meaning"],
        ["Remove unrelated staff and equipment and use blank abstract displays.", "Retain at most the context required for orientation."],
        ["Use no people/equipment unless essential; otherwise use a neutral reviewed silhouette.", "Never display readings, patient identity, or equipment-operation cues."],
    ),
    "SPATIAL_ENVIRONMENT": category_policy(
        "SPATIAL_ENVIRONMENT",
        ["system passthrough/Simulator remains default", "safe-space and non-therapeutic warnings", "assembly/component exclusion"],
        ["Keep architecture, dais, and only essential seating; omit decor first.", "Use static geometry and app-owned lighting."],
        ["Load zero optional environment assets and use the system environment.", "Do not substitute virtual surfaces for physical boundaries or support."],
    ),
    "GUIDANCE": category_policy(
        "GUIDANCE",
        ["current step and accessible equivalent", "Reset/Home and Exit/Return", "progress means navigation only"],
        ["Show current and next markers only; prefer native attachments."],
        ["Unload authored marker geometry and show a native current-step label/control."],
    ),
    "ADAPTIVE_PRESENTATION": category_policy(
        "ADAPTIVE_PRESENTATION",
        ["orientation silhouette", "replacement-not-overlay rule", "review and display authorization"],
        ["Keep source geometry unchanged and reduce only labels/motion through an app sidecar.", "Never co-load with the detailed source or pathology/tools."],
        ["Show no 3D asset or a separately reviewed silhouette proxy.", "Never decimate or rewrite the source asset in place."],
    ),
    "COMPOSITE_ASSEMBLY": category_policy(
        "COMPOSITE_ASSEMBLY",
        ["assembly domain and recursive leaf meaning", "assembly/component exclusion", "source registration and warnings"],
        ["Unload the assembly and substitute a curated set of leaf components governed by their domain policy.", "Do not partially decimate or ambiguously hide an assembly in place."],
        ["Unload the assembly and load at most one essential leaf or no geometry.", "Environment assemblies reduce to the system environment."],
    ),
}


def presentation_parameters(
    semantic_density_target: float,
    texture_resolution_scale: float,
    secondary_detail_visibility_ratio: float,
    label_density_ratio: float,
    saturation_multiplier: float,
    specular_multiplier: float,
    motion_mode: str,
    motion_speed_multiplier: float,
    particle_or_flow_mode: str,
    particle_or_flow_count_ratio: float,
) -> dict[str, Any]:
    return {
        "semantic_density_target": semantic_density_target,
        "texture_resolution_scale": texture_resolution_scale,
        "secondary_detail_visibility_ratio": secondary_detail_visibility_ratio,
        "label_density_ratio": label_density_ratio,
        "saturation_multiplier": saturation_multiplier,
        "specular_multiplier": specular_multiplier,
        "motion_mode": motion_mode,
        "motion_speed_multiplier": motion_speed_multiplier,
        "particle_or_flow_mode": particle_or_flow_mode,
        "particle_or_flow_count_ratio": particle_or_flow_count_ratio,
    }


FULL_SOURCE_PARAMETERS = presentation_parameters(
    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, "source_authored", 1.0, "source_authored", 1.0
)


def tier_parameter_profile(
    minimal: dict[str, Any], reduced80: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    return {
        "minimal": minimal,
        "reduced80": reduced80,
        "full": dict(FULL_SOURCE_PARAMETERS),
    }


CATEGORY_PARAMETER_PROFILES = {
    "ANATOMY_CNS_MACRO": tier_parameter_profile(
        presentation_parameters(0.35, 0.50, 0.20, 0.25, 0.75, 0.45, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.80, 0.75, 0.70, 0.90, 0.80, "slowed", 0.70, "none", 0.0),
    ),
    "ANATOMY_HEAD_NECK_SUPPORT": tier_parameter_profile(
        presentation_parameters(0.35, 0.50, 0.20, 0.25, 0.72, 0.42, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.80, 0.72, 0.68, 0.88, 0.78, "slowed", 0.65, "none", 0.0),
    ),
    "ANATOMY_VASCULAR": tier_parameter_profile(
        presentation_parameters(0.30, 0.50, 0.25, 0.30, 0.80, 0.50, "static", 0.0, "sparse_static_direction_markers", 0.15),
        presentation_parameters(0.80, 0.80, 0.75, 0.70, 0.90, 0.80, "slowed", 0.65, "reduced_direction_markers", 0.65),
    ),
    "PATHOLOGY_MACRO": tier_parameter_profile(
        presentation_parameters(0.30, 0.45, 0.15, 0.35, 0.62, 0.30, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.78, 0.65, 0.72, 0.80, 0.62, "static", 0.0, "none", 0.0),
    ),
    "BLOOD_FLOW_TEACHING": tier_parameter_profile(
        presentation_parameters(0.30, 0.45, 0.15, 0.30, 0.72, 0.35, "static", 0.0, "sparse_static_direction_markers", 0.15),
        presentation_parameters(0.80, 0.80, 0.70, 0.70, 0.88, 0.72, "slowed", 0.60, "reduced_cells_and_flow", 0.70),
    ),
    "MICRO_CONCEPTUAL": tier_parameter_profile(
        presentation_parameters(0.25, 0.45, 0.15, 0.30, 0.75, 0.35, "static", 0.0, "representative_static_elements", 0.10),
        presentation_parameters(0.80, 0.80, 0.70, 0.70, 0.90, 0.75, "slowed", 0.60, "reduced_representative_elements", 0.65),
    ),
    "TOOLS_ENDOVASCULAR": tier_parameter_profile(
        presentation_parameters(0.30, 0.48, 0.12, 0.35, 0.72, 0.38, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.80, 0.70, 0.72, 0.88, 0.72, "slowed", 0.60, "none", 0.0),
    ),
    "TOOLS_OPEN_CRANIAL": tier_parameter_profile(
        presentation_parameters(0.25, 0.42, 0.10, 0.35, 0.65, 0.30, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.76, 0.62, 0.70, 0.84, 0.65, "slowed", 0.55, "none", 0.0),
    ),
    "OPEN_CRANIAL_ANATOMY_STATE": tier_parameter_profile(
        presentation_parameters(0.20, 0.35, 0.10, 0.35, 0.55, 0.25, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.75, 0.65, 0.70, 0.78, 0.60, "slowed", 0.50, "none", 0.0),
    ),
    "CLINICAL_CONTEXT": tier_parameter_profile(
        presentation_parameters(0.15, 0.40, 0.05, 0.10, 0.70, 0.35, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.75, 0.60, 0.40, 0.85, 0.70, "static", 0.0, "none", 0.0),
    ),
    "SPATIAL_ENVIRONMENT": tier_parameter_profile(
        presentation_parameters(0.00, 0.25, 0.00, 0.00, 0.80, 0.40, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.75, 0.55, 0.30, 0.90, 0.70, "static", 0.0, "none", 0.0),
    ),
    "GUIDANCE": tier_parameter_profile(
        presentation_parameters(0.30, 0.50, 0.00, 0.50, 0.85, 0.40, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.80, 0.50, 0.75, 0.95, 0.70, "static", 0.0, "none", 0.0),
    ),
    "ADAPTIVE_PRESENTATION": tier_parameter_profile(
        presentation_parameters(0.10, 0.35, 0.00, 0.30, 0.75, 0.30, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.80, 0.60, 0.65, 0.90, 0.70, "slowed", 0.65, "none", 0.0),
    ),
    "COMPOSITE_ASSEMBLY": tier_parameter_profile(
        presentation_parameters(0.20, 0.40, 0.10, 0.25, 0.75, 0.40, "static", 0.0, "none", 0.0),
        presentation_parameters(0.80, 0.75, 0.65, 0.65, 0.88, 0.70, "slowed", 0.60, "none", 0.0),
    ),
}

for _category in CATEGORY_ORDER:
    for _tier in TIERS:
        CATEGORY_POLICIES[_category]["tiers"][_tier]["geometry_mutation_allowed"] = False
        CATEGORY_POLICIES[_category]["tiers"][_tier]["presentation_parameters"] = CATEGORY_PARAMETER_PROFILES[_category][_tier]

EXPECTED_PACK_RESOURCES = (
    "README.md",
    "VISUAL_DETAIL_ASSET_CATEGORIES.txt",
    "build_visual_detail_variants_v1.py",
    "validate_visual_detail_variants_v1.py",
    "visual_detail_category_policy_schema_v1.json",
    "visual_detail_category_policy_v1.json",
    "visual_detail_selector_v1.js",
    "visual_detail_variant_catalog_v1.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_release_assets() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for manifest_index, relative_manifest in enumerate(SOURCE_MANIFESTS):
        manifest_path = REPO_ROOT / relative_manifest
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for asset_index, asset in enumerate(manifest["assets"]):
            source_path = (manifest_path.parent / asset["usdz"]).resolve()
            records.append(
                {
                    "asset_id": asset["id"],
                    "source_manifest": relative_manifest,
                    "source_manifest_index": manifest_index,
                    "source_asset_index": asset_index,
                    "source_usdz": source_path.relative_to(REPO_ROOT).as_posix(),
                    "source_usdz_bytes": source_path.stat().st_size,
                    "source_usdz_sha256": sha256_file(source_path),
                }
            )
    return records


def validate_taxonomy(release_assets: list[dict[str, Any]]) -> dict[str, str]:
    category_for: dict[str, str] = {}
    for category in CATEGORY_ORDER:
        for asset_id in CATEGORY_MEMBERS[category]:
            if asset_id in category_for:
                raise ValueError(f"Duplicate taxonomy membership: {asset_id}")
            category_for[asset_id] = category
    release_ids = [record["asset_id"] for record in release_assets]
    if len(release_ids) != 150 or len(set(release_ids)) != 150:
        raise ValueError("Expected exactly 150 unique release assets")
    if set(release_ids) != set(category_for):
        raise ValueError(
            f"Taxonomy mismatch; missing={sorted(set(release_ids)-set(category_for))}, "
            f"extra={sorted(set(category_for)-set(release_ids))}"
        )
    if set(ASSEMBLY_DOMAINS) != set(CATEGORY_MEMBERS["COMPOSITE_ASSEMBLY"]):
        raise ValueError("Assembly-domain overrides must cover all and only composite assemblies")
    return category_for


def build_policy_document() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "module_id": MODULE_ID,
        "policy_id": "visual_detail_category_policy_v1",
        "patient_display_authorized": False,
        "tier_order": list(TIERS),
        "tier_semantics": {
            "minimal": {"semantic_density": "smallest_reviewed_complete_explanation"},
            "reduced80": {
                "semantic_density_target": 0.8,
                "meaning": "Retain approximately 80% of approved semantic information; this is not a polygon target.",
            },
            "full": {"source_asset_unchanged": True},
        },
        "global_must_preserve": list(GLOBAL_MUST_PRESERVE),
        "global_prohibited": list(GLOBAL_PROHIBITED),
        "presentation_parameter_contract": {
            "numeric_range": [0.0, 1.0],
            "reduced80_semantic_density_target": 0.8,
            "numeric_monotonic_order": "minimal <= reduced80 <= full",
            "motion_modes": ["static", "slowed", "source_authored"],
            "particle_or_flow_modes": [
                "none", "sparse_static_direction_markers", "reduced_direction_markers",
                "reduced_cells_and_flow", "representative_static_elements",
                "reduced_representative_elements", "source_authored",
            ],
            "units": {
                "motion_speed_multiplier": "ratio_of_source_authored_speed",
                "particle_or_flow_count_ratio": "ratio_of_source_authored_count_or_reviewed_equivalent",
                "semantic_density_target": "ratio_of_approved_explanatory_information_not_polygon_count",
            },
        },
        "category_count": len(CATEGORY_ORDER),
        "categories": [CATEGORY_POLICIES[category] for category in CATEGORY_ORDER],
        "assembly_domain_overrides": dict(sorted(ASSEMBLY_DOMAINS.items())),
    }


def build_policy_schema() -> dict[str, Any]:
    parameter_keys = [
        "semantic_density_target", "texture_resolution_scale",
        "secondary_detail_visibility_ratio", "label_density_ratio",
        "saturation_multiplier", "specular_multiplier", "motion_mode",
        "motion_speed_multiplier", "particle_or_flow_mode",
        "particle_or_flow_count_ratio",
    ]
    presentation_parameter_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": parameter_keys,
        "properties": {
            "semantic_density_target": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "texture_resolution_scale": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "secondary_detail_visibility_ratio": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "label_density_ratio": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "saturation_multiplier": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "specular_multiplier": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "motion_mode": {"enum": ["static", "slowed", "source_authored"]},
            "motion_speed_multiplier": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "particle_or_flow_mode": {
                "enum": [
                    "none", "sparse_static_direction_markers", "reduced_direction_markers",
                    "reduced_cells_and_flow", "representative_static_elements",
                    "reduced_representative_elements", "source_authored",
                ]
            },
            "particle_or_flow_count_ratio": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        },
    }
    tier_schema = {
        "type": "object",
        "required": ["geometry_mutation_allowed", "presentation_parameters"],
        "properties": {
            "geometry_mutation_allowed": {"const": False},
            "presentation_parameters": presentation_parameter_schema,
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "visual_detail_category_policy_schema_v1.json",
        "title": "Visual detail category policy v1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version", "module_id", "policy_id", "patient_display_authorized",
            "tier_order", "tier_semantics", "global_must_preserve", "global_prohibited",
            "presentation_parameter_contract", "category_count", "categories",
            "assembly_domain_overrides",
        ],
        "properties": {
            "schema_version": {"const": "1.0.0"},
            "module_id": {"const": MODULE_ID},
            "policy_id": {"const": "visual_detail_category_policy_v1"},
            "patient_display_authorized": {"const": False},
            "tier_order": {"const": list(TIERS)},
            "tier_semantics": {"type": "object"},
            "global_must_preserve": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "global_prohibited": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "presentation_parameter_contract": {"type": "object"},
            "category_count": {"const": 14},
            "categories": {
                "type": "array", "minItems": 14, "maxItems": 14,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["category_id", "asset_count", "must_preserve", "tiers"],
                    "properties": {
                        "category_id": {"enum": list(CATEGORY_ORDER)},
                        "asset_count": {"type": "integer", "minimum": 1},
                        "must_preserve": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                        "tiers": {
                            "type": "object", "additionalProperties": False,
                            "required": list(TIERS),
                            "properties": {tier: tier_schema for tier in TIERS},
                        },
                    },
                },
            },
            "assembly_domain_overrides": {"type": "object", "minProperties": 17, "maxProperties": 17},
        },
    }


def build_catalog(release_assets: list[dict[str, Any]], category_for: dict[str, str]) -> dict[str, Any]:
    assets: list[dict[str, Any]] = []
    variants: list[dict[str, Any]] = []
    for record in release_assets:
        asset_id = record["asset_id"]
        category = category_for[asset_id]
        assembly_domain = ASSEMBLY_DOMAINS.get(asset_id)
        parameter_policy_category = (
            assembly_domain if assembly_domain in CATEGORY_POLICIES else category
        )
        asset_variants = []
        for tier in TIERS:
            variant = {
                "variant_id": f"{asset_id}::{tier}",
                "asset_id": asset_id,
                "tier": tier,
                "category_id": category,
                "source_usdz": record["source_usdz"],
                "source_usdz_bytes": record["source_usdz_bytes"],
                "source_usdz_sha256": record["source_usdz_sha256"],
                "patient_display_authorized": False,
                "preserve_silhouette_or_meaning": True,
                "preserve_medical_facts_and_warnings": True,
                "geometry_mutation_allowed": False,
                "source_asset_unchanged": True,
                "binds_exact_observed_source_as_presentation": tier == "full",
                "virtual_reversible_sidecar": tier != "full",
                "category_policy_ref": f"visual_detail_category_policy_v1#{category}",
                "parameter_policy_category": parameter_policy_category,
                "presentation_parameters": dict(
                    CATEGORY_PARAMETER_PROFILES[parameter_policy_category][tier]
                ),
            }
            if category == "COMPOSITE_ASSEMBLY":
                variant["assembly_resolution"] = {
                    "assembly_domain": assembly_domain,
                    "action": (
                        "bind_exact_source_assembly"
                        if tier == "full"
                        else "unload_assembly_then_select_leaf_components"
                    ),
                    "leaf_parameter_resolution": (
                        "per_leaf_primary_category"
                        if assembly_domain == "MIXED_REGISTERED_HEAD"
                        else "fixed_assembly_domain_category"
                    ),
                    "assembly_control_parameters": dict(
                        CATEGORY_PARAMETER_PROFILES["COMPOSITE_ASSEMBLY"][tier]
                    ),
                }
            if tier == "reduced80":
                variant["semantic_density_target"] = 0.8
            elif tier == "minimal":
                variant["semantic_density"] = "smallest_reviewed_complete_explanation"
            asset_variants.append(variant["variant_id"])
            variants.append(variant)
        assets.append(
            {
                **record,
                "primary_category": category,
                "composition_kind": "assembly" if category == "COMPOSITE_ASSEMBLY" else "component",
                "assembly_domain": assembly_domain,
                "parameter_policy_category": parameter_policy_category,
                "variant_ids": asset_variants,
            }
        )
    return {
        "schema_version": "1.0.0",
        "module_id": MODULE_ID,
        "catalog_id": "visual_detail_variant_catalog_v1",
        "patient_display_authorized": False,
        "source_release_manifest_count": len(SOURCE_MANIFESTS),
        "source_release_asset_count": len(assets),
        "category_count": len(CATEGORY_ORDER),
        "category_counts": {category: len(CATEGORY_MEMBERS[category]) for category in CATEGORY_ORDER},
        "tier_count": len(TIERS),
        "tier_order": list(TIERS),
        "virtual_variant_count": len(variants),
        "runtime_geometry_included": False,
        "source_geometry_mutation_allowed": False,
        "full_binding_contract": "Every full variant binds the exact observed source USDZ path, byte count, and SHA-256 and permits no source mutation.",
        "lower_tier_contract": "Minimal and reduced80 are virtual reversible presentation sidecars only; they preserve silhouette or reviewed meaning, medical facts, warnings, pathway, laterality, and registration.",
        "assets": assets,
        "variants": variants,
    }


def render_category_text() -> str:
    lines = [
        "VISUAL_DETAIL_ASSET_CATEGORIES_V1",
        "schema_version=1.0.0",
        "asset_count=150",
        "category_count=14",
        "mapping_rule=exactly_one_primary_category_per_release_asset_id",
        "",
    ]
    for category in CATEGORY_ORDER:
        members = sorted(CATEGORY_MEMBERS[category])
        lines.append(f"[{category}] count={len(members)}")
        lines.extend(members)
        lines.append("")
    lines.append("[ASSEMBLY_DOMAIN_OVERRIDES] count=17")
    for asset_id, domain in sorted(ASSEMBLY_DOMAINS.items()):
        lines.append(f"{asset_id}={domain}")
    return "\n".join(lines) + "\n"


def build_manifest() -> dict[str, Any]:
    resources = []
    for relative_path in EXPECTED_PACK_RESOURCES:
        path = PACK_ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(path)
        media_type = {
            ".json": "application/json",
            ".js": "text/javascript",
            ".py": "text/x-python",
            ".md": "text/markdown",
            ".txt": "text/plain",
        }[path.suffix]
        resources.append(
            {
                "id": path.stem,
                "path": relative_path,
                "media_type": media_type,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": "1.0.0",
        "module_id": MODULE_ID,
        "title": "Visual detail virtual variants v1",
        "resource_count": len(resources),
        "integrity_algorithm": "sha256",
        "manifest_self_hash_policy": "This manifest excludes itself because a self-hash is recursive.",
        "patient_display_authorized": False,
        "asset_count": 150,
        "tier_count": 3,
        "virtual_variant_count": 450,
        "tiers": list(TIERS),
        "reduced80_semantic_density_target": 0.8,
        "runtime_geometry_included": False,
        "resources": resources,
    }


def main() -> None:
    release_assets = load_release_assets()
    category_for = validate_taxonomy(release_assets)
    write_json(PACK_ROOT / "visual_detail_category_policy_v1.json", build_policy_document())
    write_json(PACK_ROOT / "visual_detail_category_policy_schema_v1.json", build_policy_schema())
    write_json(PACK_ROOT / "visual_detail_variant_catalog_v1.json", build_catalog(release_assets, category_for))
    (PACK_ROOT / "VISUAL_DETAIL_ASSET_CATEGORIES.txt").write_text(render_category_text(), encoding="utf-8")
    write_json(PACK_ROOT / "asset_manifest_visual_detail_variants_v1.json", build_manifest())
    print("BUILD PASS: 14 categories; 150 assets; 3 explicit tiers; 450 virtual variants; 8 manifested resources.")


if __name__ == "__main__":
    main()
