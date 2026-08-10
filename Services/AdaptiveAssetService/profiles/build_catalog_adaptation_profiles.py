#!/usr/bin/env python3
"""Build and validate conservative presentation profiles for the release catalog.

The profile is deliberately separate from the HTTP service. It describes which
non-destructive presentation operations a future client may consider; it does
not authorize patient display, infer anxiety, or alter medical content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple


PROFILE_SCHEMA_VERSION = "1.0.0"
EXPECTED_MANIFEST_COUNT = 12
EXPECTED_RELEASE_ASSET_COUNT = 135
HELD_ASSET_IDS = {
    "middle_inner_ear_bilateral_v3",
    "cranial_support_registered_assembly_v3",
}

PROFILE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROFILE_DIR.parents[2]
ASSET_ROOT = REPO_ROOT / "RealityKitContent" / "Assets"
RUNTIME_PROFILE_DIR = PROFILE_DIR.parent / "adaptive_asset_service" / "runtime_profiles"
OUTPUT_PATH = RUNTIME_PROFILE_DIR / "catalog_adaptation_profiles.json"


MANIFEST_MODULES = {
    "asset_manifest.json": "prototype_v1",
    "asset_manifest_v2.json": "core_realistic_v2",
    "asset_manifest_head_details_v2.json": "head_details_v2",
    "asset_manifest_cranial_vascular_v2.json": "cranial_vascular_v2",
    "asset_manifest_bloodflow_v2.json": "cerebral_bloodflow_v2",
    "asset_manifest_devices_v2.json": "realistic_devices_v2",
    "asset_manifest_neural_detail_v3.json": "neural_detail_v3",
    "asset_manifest_cranial_detail_v3.json": "cranial_detail_v3",
    "asset_manifest_intracranial_micro_v3.json": "intracranial_micro_v3",
    "asset_manifest_endovascular_tools_v3.json": "endovascular_tools_v3",
    "asset_manifest_open_cranial_tools_v3.json": "open_cranial_tools_v3",
    "asset_manifest_adaptive_visuals_v1.json": "adaptive_visuals_v1",
}


# Direct aggregate membership. The generator expands this transitively for the
# never-co-load rule. These relationships mirror the release manifests and the
# canonical MASTER composition contract.
AGGREGATE_COMPONENTS: Mapping[str, Sequence[str]] = {
    "thrombectomy_registered_hero_v2": (
        "brain_anatomy_realistic_v2",
        "brain_deep_structures_v2",
        "brain_ventricles_v2",
        "skull_semantic_realistic_v2",
        "eyes_context_realistic_v2",
        "cerebral_arteries_realistic_v2",
        "ischemic_mca_clot_v2",
    ),
    "layered_head_cutaway_registered_v2": (
        "external_head_scalp_cutaway_v2",
        "dura_mater_cutaway_conceptual_v2",
        "meningeal_partitions_atlas_v2",
        "brain_anatomy_realistic_v2",
    ),
    "meningeal_partitions_atlas_v2": (
        "falx_cerebri_atlas_v2",
        "tentorium_cerebelli_atlas_v2",
    ),
    "dural_sinuses_jugulars_realistic_v2": (
        "dural_venous_sinuses_realistic_v2",
        "internal_jugular_veins_realistic_v2",
    ),
    "head_neck_veins_expanded_realistic_v2": (
        "dural_sinuses_jugulars_realistic_v2",
        "head_neck_veins_supplemental_v2",
    ),
    "cranial_vascular_registered_assembly_v2": (
        "head_neck_veins_expanded_realistic_v2",
        "neck_access_arteries_realistic_v2",
    ),
    "artery_cutaway_complete_v2": (
        "artery_wall_cutaway_v2",
        "artery_interior_bloodflow_v2",
    ),
    "cerebral_bloodflow_teaching_set_v2": (
        "artery_cutaway_complete_v2",
        "circle_of_willis_flow_overlay_v2",
        "red_blood_cells_closeup_v2",
        "microcirculation_arterial_venous_v2",
    ),
    "thrombectomy_device_set_educational_v2": (
        "guidewire_educational_v2",
        "microcatheter_educational_v2",
        "aspiration_catheter_educational_v2",
        "stent_retriever_educational_v2",
    ),
    "neural_detail_registered_review_assembly_v3": (
        "frontal_cortex_parcellation_v3",
        "parietal_cortex_parcellation_v3",
        "temporal_cortex_parcellation_v3",
        "occipital_cortex_parcellation_v3",
        "insular_opercular_cortex_v3",
        "cingulate_parahippocampal_cortex_v3",
        "cerebellar_substructures_v3",
        "brainstem_substructures_v3",
        "basal_ganglia_deep_nuclei_v3",
        "thalamic_hypothalamic_nuclei_v3",
        "hippocampal_amygdala_limbic_nuclei_v3",
        "ventricular_spaces_v3",
        "major_white_matter_regions_v3",
        "commissural_sensory_pathways_v3",
    ),
    "cranial_nerves_complete_assembly_v3": (
        "cranial_nerve_olfactory_i_bilateral_v3",
        "cranial_nerve_optic_ii_bilateral_v3",
        "cranial_nerves_ocular_motor_iii_iv_vi_v3",
        "cranial_nerve_trigeminal_v_expanded_v3",
        "cranial_nerve_facial_vii_bilateral_v3",
        "cranial_nerve_vestibulocochlear_viii_v3",
        "cranial_nerves_glossopharyngeal_ix_vagus_x_v3",
        "cranial_nerve_accessory_xi_bilateral_v3",
        "cranial_nerve_hypoglossal_xii_bilateral_v3",
    ),
    "intracranial_micro_teaching_set_v3": (
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
        "ischemic_tissue_zones_conceptual_v3",
    ),
    "vascular_access_setup_review_assembly_v3": (
        "vascular_access_needle_educational_v3",
        "vascular_access_wire_educational_v3",
        "introducer_sheath_dilator_set_educational_v3",
        "puncture_site_hemostasis_options_educational_v3",
    ),
    "endovascular_tools_workflow_review_assembly_v3": (
        "vascular_access_setup_review_assembly_v3",
        "vascular_access_needle_educational_v3",
        "vascular_access_wire_educational_v3",
        "introducer_sheath_dilator_set_educational_v3",
        "guide_catheter_hemostatic_valve_educational_v3",
        "aspiration_pump_canister_tubing_educational_v3",
        "contrast_manifold_syringe_flush_educational_v3",
        "torque_device_y_connector_accessories_educational_v3",
        "puncture_site_hemostasis_options_educational_v3",
        "sterile_endovascular_instrument_tray_educational_v3",
        "angiography_suite_controls_educational_v3",
    ),
    "cranial_access_tools_review_assembly_open_neurosurgery_v3": (
        "surface_marking_ruler_set_open_neurosurgery_v3",
        "scalpel_dissector_set_open_neurosurgery_v3",
        "scalp_retractor_hemostat_set_open_neurosurgery_v3",
        "perforator_craniotome_system_open_neurosurgery_v3",
        "bone_flap_fixation_set_open_neurosurgery_v3",
    ),
    "intradural_closure_tools_review_assembly_open_neurosurgery_v3": (
        "dural_scissors_hooks_forceps_set_open_neurosurgery_v3",
        "bipolar_forceps_irrigation_set_open_neurosurgery_v3",
        "suction_microdissector_set_open_neurosurgery_v3",
        "brain_spatula_retractor_set_open_neurosurgery_v3",
        "microscope_microinstrument_tray_open_neurosurgery_v3",
        "dural_closure_suture_patch_set_open_neurosurgery_v3",
    ),
}


# Directed, source-documented replacements that are not literal package
# containment. These state only which representation must be hidden to avoid
# duplicate geometry; they do not assert clinical superiority or equivalence.
SEMANTIC_REPLACEMENTS: Mapping[str, Sequence[str]] = {
    "ventricular_spaces_v3": (
        "brain_ventricles_v2",
    ),
    "neural_detail_registered_review_assembly_v3": (
        "brain_anatomy_realistic_v2",
        "brain_deep_structures_v2",
        "brain_ventricles_v2",
    ),
    "vascular_access_needle_educational_v3": (
        "arterial_access_site",
    ),
    "vascular_access_setup_review_assembly_v3": (
        "arterial_access_site",
    ),
    "endovascular_tools_workflow_review_assembly_v3": (
        "arterial_access_site",
    ),
    "perforator_craniotome_system_open_neurosurgery_v3": (
        "cranial_drill_generic",
    ),
    "cranial_access_tools_review_assembly_open_neurosurgery_v3": (
        "cranial_drill_generic",
    ),
    "suction_microdissector_set_open_neurosurgery_v3": (
        "suction_and_forceps",
    ),
    "intradural_closure_tools_review_assembly_open_neurosurgery_v3": (
        "suction_and_forceps",
    ),
    "conditional_csf_access_instrument_set_open_neurosurgery_v3": (
        "optional_evd_system",
    ),
}


# Non-directed overlaps that should still fail closed in a presentation
# composition. Pairs are made symmetric by the generator.
SEMANTIC_EXCLUSION_PAIRS: Sequence[Tuple[str, str]] = (
    ("major_white_matter_regions_v3", "commissural_sensory_pathways_v3"),
)


ORIENTATION_CANDIDATE_SOURCE_IDS: Set[str] = {
    "brain_structures_generic",
    "brain_anatomy_realistic_v2",
    "brain_deep_structures_v2",
    "brain_ventricles_v2",
    "frontal_cortex_parcellation_v3",
    "parietal_cortex_parcellation_v3",
    "temporal_cortex_parcellation_v3",
    "occipital_cortex_parcellation_v3",
    "insular_opercular_cortex_v3",
    "cingulate_parahippocampal_cortex_v3",
    "cerebellar_substructures_v3",
    "brainstem_substructures_v3",
    "basal_ganglia_deep_nuclei_v3",
    "thalamic_hypothalamic_nuclei_v3",
    "hippocampal_amygdala_limbic_nuclei_v3",
    "ventricular_spaces_v3",
    "major_white_matter_regions_v3",
    "commissural_sensory_pathways_v3",
    "neural_detail_registered_review_assembly_v3",
}
ORIENTATION_CANDIDATE_ID = "brain_orientation_calm_educational_v1"


MODULE_CATEGORY = {
    "prototype_v1": "prototype_patient_education",
    "core_realistic_v2": "registered_core_anatomy",
    "head_details_v2": "head_layer_anatomy",
    "cranial_vascular_v2": "cranial_vascular_anatomy",
    "cerebral_bloodflow_v2": "blood_flow_teaching",
    "realistic_devices_v2": "endovascular_device_concept",
    "neural_detail_v3": "neural_detail_anatomy",
    "cranial_detail_v3": "cranial_support_anatomy",
    "intracranial_micro_v3": "scale_separated_micro_teaching",
    "endovascular_tools_v3": "endovascular_support_tool",
    "open_cranial_tools_v3": "open_cranial_instrument",
    "adaptive_visuals_v1": "adaptive_orientation_candidate",
}

CONTENT_CATEGORY_VOCABULARY: Set[str] = set(MODULE_CATEGORY.values()).union(
    {
        "airway_orientation",
        "anatomy",
        "clinical_environment",
        "comfort_oriented_design_hypothesis",
        "conditional_open_cranial_context",
        "cranial_nerves",
        "endocrine_anatomy",
        "endovascular_procedure_context",
        "external_orientation",
        "flow_visualization",
        "guidance_ui",
        "microanatomy_teaching",
        "muscle_anatomy",
        "neuroanatomy",
        "pathology_teaching",
        "patient_context",
        "recovery_context",
        "review_assembly",
        "staff_context",
        "vascular_anatomy",
    }
)

GRAPHIC_CONTENT_TAG_VOCABULARY: Set[str] = {
    "animated_particles_or_flow",
    "blood_or_blood_components",
    "body_or_clinical_staff",
    "bone_access_instrument_or_state",
    "bone_anatomy",
    "clot_or_thrombus",
    "edema_or_swelling",
    "exposed_tissue_or_cutaway",
    "external_anatomy",
    "fluid_or_flow_cue",
    "hemorrhage",
    "incision_or_opening",
    "internal_anatomy",
    "ischemic_tissue_or_pathology",
    "medical_device",
    "medical_equipment",
    "microscopic_detail",
    "needle_wire_catheter_or_drain",
    "none_observed",
    "procedure_sequence_cue",
    "surgical_instrument",
    "suture_closure_or_dressing",
    "vascular_anatomy",
}


ANATOMY_IDS: Set[str] = {
    "head_skin_generic",
    "skull_cranium_generic",
    "brain_structures_generic",
    "cerebral_arteries_generic",
    "brain_anatomy_realistic_v2",
    "brain_deep_structures_v2",
    "brain_ventricles_v2",
    "skull_semantic_realistic_v2",
    "cerebral_arteries_realistic_v2",
    "thrombectomy_registered_hero_v2",
}

EXTERNAL_ANATOMY_IDS: Set[str] = {
    "head_skin_generic",
    "external_head_scalp_realistic_v2",
    ORIENTATION_CANDIDATE_ID,
}

PATHOLOGY_TAGS: Mapping[str, Sequence[str]] = {
    "ischemic_lvo_clot": ("clot_or_thrombus", "ischemic_tissue_or_pathology"),
    "ischemic_mca_clot_v2": ("clot_or_thrombus", "ischemic_tissue_or_pathology"),
    "ich_hematoma": ("blood_or_blood_components", "hemorrhage"),
    "edema_swelling": ("edema_or_swelling", "ischemic_tissue_or_pathology"),
    "ischemic_tissue_zones_conceptual_v3": ("ischemic_tissue_or_pathology",),
}

BLOOD_CONTENT_IDS: Set[str] = {
    "ich_hematoma",
    "artery_interior_bloodflow_v2",
    "artery_cutaway_complete_v2",
    "red_blood_cells_closeup_v2",
    "microcirculation_arterial_venous_v2",
    "cerebral_bloodflow_teaching_set_v2",
    "blood_brain_barrier_neurovascular_unit_conceptual_v3",
    "formed_blood_elements_magnified_v3",
    "platelet_fibrin_thrombus_microstructure_conceptual_v3",
    "intracranial_micro_teaching_set_v3",
}

CLOT_IDS: Set[str] = {
    "ischemic_lvo_clot",
    "stent_retriever",
    "ischemic_mca_clot_v2",
    "thrombectomy_registered_hero_v2",
    "platelet_fibrin_thrombus_microstructure_conceptual_v3",
    "intracranial_micro_teaching_set_v3",
}

PRIMARY_PATHOLOGY_IDS: Set[str] = set(PATHOLOGY_TAGS).union(CLOT_IDS)

VASCULAR_IDS: Set[str] = {
    "cerebral_arteries_generic",
    "cerebral_arteries_realistic_v2",
    "thrombectomy_registered_hero_v2",
    "artery_wall_cutaway_v2",
    "artery_interior_bloodflow_v2",
    "artery_cutaway_complete_v2",
    "circle_of_willis_flow_overlay_v2",
    "microcirculation_arterial_venous_v2",
    "cerebral_bloodflow_animation_v2",
    "cerebral_bloodflow_teaching_set_v2",
    "dural_venous_sinuses_realistic_v2",
    "internal_jugular_veins_realistic_v2",
    "dural_sinuses_jugulars_realistic_v2",
    "head_neck_veins_supplemental_v2",
    "head_neck_veins_expanded_realistic_v2",
    "neck_access_arteries_realistic_v2",
    "cranial_vascular_registered_assembly_v2",
    "blood_brain_barrier_neurovascular_unit_conceptual_v3",
    "capillary_endothelium_tight_junctions_conceptual_v3",
}

FLOW_CUE_IDS: Set[str] = {
    "angiography_contrast_flow",
    "artery_interior_bloodflow_v2",
    "artery_cutaway_complete_v2",
    "circle_of_willis_flow_overlay_v2",
    "microcirculation_arterial_venous_v2",
    "cerebral_bloodflow_animation_v2",
    "cerebral_bloodflow_teaching_set_v2",
    "choroid_plexus_csf_interface_conceptual_v3",
    "bipolar_forceps_irrigation_set_open_neurosurgery_v3",
    "suction_microdissector_set_open_neurosurgery_v3",
    "conditional_csf_access_instrument_set_open_neurosurgery_v3",
    "aspiration_pump_canister_tubing_educational_v3",
    "contrast_manifold_syringe_flush_educational_v3",
}

ANIMATED_FLOW_IDS: Set[str] = {
    "angiography_contrast_flow",
    "cerebral_bloodflow_animation_v2",
}

CUTAWAY_IDS: Set[str] = {
    "scalp_incision_flap",
    "craniotomy_bone_flap",
    "artery_wall_cutaway_v2",
    "artery_interior_bloodflow_v2",
    "artery_cutaway_complete_v2",
    "cerebral_bloodflow_teaching_set_v2",
    "external_head_scalp_cutaway_v2",
    "dura_mater_cutaway_conceptual_v2",
    "layered_head_cutaway_registered_v2",
    "blood_brain_barrier_neurovascular_unit_conceptual_v3",
    "platelet_fibrin_thrombus_microstructure_conceptual_v3",
}

INCISION_IDS: Set[str] = {
    "scalp_incision_flap",
    "craniotomy_bone_flap",
    "scalp_closure_sutures",
}

CLOSURE_IDS: Set[str] = {
    "scalp_closure_sutures",
    "dural_patch",
    "postoperative_head_dressing",
    "bone_flap_fixation_set_open_neurosurgery_v3",
    "dural_closure_suture_patch_set_open_neurosurgery_v3",
    "intradural_closure_tools_review_assembly_open_neurosurgery_v3",
}

NEEDLE_CATHETER_IDS: Set[str] = {
    "arterial_access_site",
    "catheter_body_to_brain_route",
    "guidewire_microcatheter_set",
    "aspiration_catheter",
    "minimally_invasive_evacuator_port",
    "optional_evd_system",
    "guidewire_educational_v2",
    "microcatheter_educational_v2",
    "aspiration_catheter_educational_v2",
    "thrombectomy_device_set_educational_v2",
    "vascular_access_needle_educational_v3",
    "vascular_access_wire_educational_v3",
    "introducer_sheath_dilator_set_educational_v3",
    "guide_catheter_hemostatic_valve_educational_v3",
    "vascular_access_setup_review_assembly_v3",
    "endovascular_tools_workflow_review_assembly_v3",
    "conditional_csf_access_instrument_set_open_neurosurgery_v3",
}

MEDICAL_DEVICE_IDS: Set[str] = {
    "guidewire_microcatheter_set",
    "stent_retriever",
    "aspiration_catheter",
    "cranial_drill_generic",
    "minimally_invasive_evacuator_port",
    "optional_evd_system",
    "guidewire_educational_v2",
    "microcatheter_educational_v2",
    "aspiration_catheter_educational_v2",
    "stent_retriever_educational_v2",
    "thrombectomy_device_set_educational_v2",
}

ROOM_EQUIPMENT_IDS: Set[str] = {
    "angiography_operating_table",
    "angiography_c_arm",
    "vital_sign_monitor",
    "iv_pole_and_bag",
    "aspiration_pump_canister_tubing_educational_v3",
    "contrast_manifold_syringe_flush_educational_v3",
    "sterile_endovascular_instrument_tray_educational_v3",
    "angiography_suite_controls_educational_v3",
    "endovascular_tools_workflow_review_assembly_v3",
}

BONE_ACCESS_IDS: Set[str] = {
    "craniotomy_bone_flap",
    "cranial_drill_generic",
    "perforator_craniotome_system_open_neurosurgery_v3",
    "bone_flap_fixation_set_open_neurosurgery_v3",
    "cranial_access_tools_review_assembly_open_neurosurgery_v3",
}

BONE_ANATOMY_IDS: Set[str] = {
    "skull_cranium_generic",
    "skull_semantic_realistic_v2",
    "craniotomy_bone_flap",
    "thrombectomy_registered_hero_v2",
}

HIGH_INTENSITY_IDS: Set[str] = {
    "ich_hematoma",
    "scalp_incision_flap",
    "artery_interior_bloodflow_v2",
    "artery_cutaway_complete_v2",
    "cerebral_bloodflow_teaching_set_v2",
    "platelet_fibrin_thrombus_microstructure_conceptual_v3",
    "ischemic_tissue_zones_conceptual_v3",
    "intracranial_micro_teaching_set_v3",
    "layered_head_cutaway_registered_v2",
    "thrombectomy_registered_hero_v2",
}

MINIMAL_INTENSITY_IDS: Set[str] = {
    "head_skin_generic",
    "patient_supine_generic",
    "angiography_operating_table",
    "clinical_team_generic",
    "spatial_step_markers",
    "external_head_scalp_realistic_v2",
    ORIENTATION_CANDIDATE_ID,
}

LOW_INTENSITY_IDS: Set[str] = {
    "postoperative_head_dressing",
}


ACTION_VOCABULARY = {
    "visibility": {
        "hide_asset": "Hide the complete asset without changing its source USDZ.",
        "restore_source_visibility": "Restore the unmodified source visibility in one action.",
        "reduce_label_density": "Reduce app-owned labels while preserving access to the full approved explanation.",
        "progressive_disclosure": "Reveal approved semantic groups one step at a time.",
        "hide_graphic_subcomponents_if_semantically_mapped": "Hide only reviewed semantic children; never infer child meaning from mesh appearance.",
        "replace_aggregate_with_components": "Swap an aggregate for its independent component packages.",
        "replace_components_with_aggregate": "Swap components for a review aggregate without co-loading either representation.",
        "replace_semantic_overlap": "Swap source-documented overlapping representations without implying clinical superiority or content equivalence.",
        "use_review_gated_orientation_interstitial_candidate": "Offer a separate orientation candidate only as a display-blocked review option; it is not content-equivalent.",
    },
    "material": {
        "apply_bounded_developer_preview_tint": "Apply the policy tint only in a display-blocked developer preview; external review is required before patient use.",
        "reduce_saturation_preserving_source_access": "Reduce saturation while excluding mapped labels and preserving one-action access to the unmodified source.",
        "increase_roughness": "Reduce glare using a reversible developer-preview material override.",
        "reduce_specular": "Reduce specular response using a reversible developer-preview material override.",
        "reduce_emission": "Reduce emissive intensity without changing route or state meaning.",
        "restore_source_materials": "Restore all source materials in one action.",
    },
    "motion": {
        "disable_autoplay": "Require an explicit user action before motion begins.",
        "pause_runtime_motion": "Pause authored or app-owned motion immediately.",
        "reduce_speed": "Use a reversible developer-preview playback rate without changing event order.",
        "disable_looping": "Do not repeat potentially distressing motion automatically.",
        "pause_at_initial_authored_pose": "Disable autoplay and hold the initial authored pose; no representative frame is implied.",
        "block_unreviewed_motion": "Keep a static source static; do not invent procedural motion.",
        "restore_authored_motion": "Restore only the authored, reviewed motion contract.",
    },
}


def _manifest_paths() -> List[Path]:
    return sorted(ASSET_ROOT.rglob("asset_manifest*.json"))


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _catalog_digest(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(_relative(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_catalog() -> Tuple[List[Dict[str, Any]], List[str], str]:
    manifest_paths = _manifest_paths()
    if len(manifest_paths) != EXPECTED_MANIFEST_COUNT:
        raise ValueError(
            "expected %d manifests, found %d"
            % (EXPECTED_MANIFEST_COUNT, len(manifest_paths))
        )

    records: List[Dict[str, Any]] = []
    for manifest_path in manifest_paths:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        module = MANIFEST_MODULES.get(manifest_path.name)
        if module is None:
            raise ValueError("unmapped release manifest: %s" % manifest_path.name)
        for source_record in manifest.get("assets", []):
            record = dict(source_record)
            record["_source_manifest"] = _relative(manifest_path)
            record["_module"] = str(record.get("module") or module)
            # Normalize the two human-readable module labels to stable IDs.
            if manifest_path.name in MANIFEST_MODULES:
                record["_module"] = module
            records.append(record)

    ids = [str(record["id"]) for record in records]
    if len(ids) != EXPECTED_RELEASE_ASSET_COUNT:
        raise ValueError(
            "expected %d released assets, found %d"
            % (EXPECTED_RELEASE_ASSET_COUNT, len(ids))
        )
    if len(set(ids)) != len(ids):
        duplicates = sorted(asset_id for asset_id in set(ids) if ids.count(asset_id) > 1)
        raise ValueError("duplicate released asset IDs: %s" % duplicates)
    held_hits = sorted(set(ids).intersection(HELD_ASSET_IDS))
    if held_hits:
        raise ValueError("held asset IDs entered the release catalog: %s" % held_hits)
    return records, [_relative(path) for path in manifest_paths], _catalog_digest(manifest_paths)


def _transitive_components(asset_id: str, visiting: Optional[Set[str]] = None) -> Set[str]:
    visiting = set() if visiting is None else set(visiting)
    if asset_id in visiting:
        raise ValueError("aggregate cycle detected at %s" % asset_id)
    visiting.add(asset_id)
    result: Set[str] = set()
    for component in AGGREGATE_COMPONENTS.get(asset_id, ()):
        result.add(component)
        result.update(_transitive_components(component, visiting))
    return result


def _exclusion_map(all_ids: Set[str]) -> Dict[str, Set[str]]:
    exclusions = {asset_id: set() for asset_id in all_ids}
    for aggregate_id, direct_components in AGGREGATE_COMPONENTS.items():
        if aggregate_id not in all_ids:
            raise ValueError("aggregate is not released: %s" % aggregate_id)
        for component in direct_components:
            if component not in all_ids:
                raise ValueError(
                    "aggregate %s references unknown component %s"
                    % (aggregate_id, component)
                )
        for component in _transitive_components(aggregate_id):
            exclusions[aggregate_id].add(component)
            exclusions[component].add(aggregate_id)
    for replacement_id, replaced_ids in SEMANTIC_REPLACEMENTS.items():
        if replacement_id not in all_ids:
            raise ValueError("semantic replacement is not released: %s" % replacement_id)
        for replaced_id in replaced_ids:
            if replaced_id not in all_ids:
                raise ValueError(
                    "semantic replacement %s references unknown asset %s"
                    % (replacement_id, replaced_id)
                )
            exclusions[replacement_id].add(replaced_id)
            exclusions[replaced_id].add(replacement_id)
    for left, right in SEMANTIC_EXCLUSION_PAIRS:
        if left not in all_ids or right not in all_ids:
            raise ValueError("semantic exclusion references unknown asset: %s, %s" % (left, right))
        exclusions[left].add(right)
        exclusions[right].add(left)
    return exclusions


def _declared_exclusion_pairs(all_ids: Set[str]) -> Set[Tuple[str, str]]:
    """Collect release-manifest exclusions for a drift/superset check."""
    pairs: Set[Tuple[str, str]] = set()
    for manifest_path in _manifest_paths():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for rule in manifest.get("prohibited_combinations", []):
            if not isinstance(rule, dict):
                continue
            left = str(rule.get("asset") or "")
            for right_value in rule.get("excludes", []):
                right = str(right_value)
                if left in all_ids and right in all_ids:
                    pairs.add((left, right))
        for rule in manifest.get("aggregate_exclusion_groups", []):
            if not isinstance(rule, dict):
                continue
            left = str(rule.get("aggregate_id") or "")
            for right_value in rule.get("exclude_when_loaded", []):
                right = str(right_value)
                if left in all_ids and right in all_ids:
                    pairs.add((left, right))
        for aggregate_value, component_values in manifest.get("assemblies", {}).items():
            aggregate = str(aggregate_value)
            for component_value in component_values:
                component = str(component_value)
                if aggregate in all_ids and component in all_ids:
                    pairs.add((aggregate, component))
        for record in manifest.get("assets", []):
            asset_id = str(record.get("id") or "")
            related_values: List[str] = []
            related_values.extend(str(value) for value in record.get("prohibited_co_load_asset_ids", []))
            related_values.extend(str(value) for value in record.get("transitive_exclusions", []))
            related_values.extend(str(value) for value in record.get("component_asset_ids", []))
            mutually_exclusive = record.get("mutually_exclusive_with_review_assembly")
            if mutually_exclusive:
                related_values.append(str(mutually_exclusive))
            for related in related_values:
                if asset_id in all_ids and related in all_ids:
                    pairs.add((asset_id, related))
    return pairs


def _is_neural_detail(asset_id: str, module: str) -> bool:
    return module == "neural_detail_v3" or asset_id in {
        "brain_structures_generic",
        "brain_anatomy_realistic_v2",
        "brain_deep_structures_v2",
        "brain_ventricles_v2",
        ORIENTATION_CANDIDATE_ID,
    }


def _content_categories(record: Mapping[str, Any]) -> List[str]:
    asset_id = str(record["id"])
    module = str(record["_module"])
    categories: Set[str] = {MODULE_CATEGORY[module]}

    prototype_module = str(record.get("module") or "")
    if prototype_module == "shared_anatomy" or asset_id in ANATOMY_IDS:
        categories.add("anatomy")
    if asset_id in EXTERNAL_ANATOMY_IDS:
        categories.add("external_orientation")
    if _is_neural_detail(asset_id, module):
        categories.add("neuroanatomy")
    if module == "cranial_detail_v3" and "cranial_nerve" in asset_id:
        categories.add("cranial_nerves")
    if module == "cranial_detail_v3" and "muscle" in asset_id:
        categories.add("muscle_anatomy")
    if module == "cranial_detail_v3" and "pituitary" in asset_id:
        categories.add("endocrine_anatomy")
    if asset_id in {
        "nasal_cavity_paranasal_spaces_v3",
        "pharyngeal_upper_airway_context_v3",
    }:
        categories.add("airway_orientation")
    if asset_id in VASCULAR_IDS or module == "cranial_vascular_v2":
        categories.add("vascular_anatomy")
    if asset_id in PATHOLOGY_TAGS or asset_id in CLOT_IDS:
        categories.add("pathology_teaching")
    if module == "cerebral_bloodflow_v2" or asset_id == "angiography_contrast_flow":
        categories.add("flow_visualization")
    if module == "intracranial_micro_v3":
        categories.add("microanatomy_teaching")
    if prototype_module == "shared_room" or asset_id in ROOM_EQUIPMENT_IDS:
        categories.add("clinical_environment")
    if asset_id == "patient_supine_generic":
        categories.add("patient_context")
    if asset_id == "clinical_team_generic":
        categories.add("staff_context")
    if prototype_module == "thrombectomy" or module in {
        "realistic_devices_v2",
        "endovascular_tools_v3",
    }:
        categories.add("endovascular_procedure_context")
    if prototype_module in {"open_cranial", "hemorrhage"} or module == "open_cranial_tools_v3":
        categories.add("conditional_open_cranial_context")
    if prototype_module == "recovery":
        categories.add("recovery_context")
    if prototype_module == "guidance":
        categories.add("guidance_ui")
    if asset_id in AGGREGATE_COMPONENTS:
        categories.add("review_assembly")
    if asset_id == ORIENTATION_CANDIDATE_ID:
        categories.add("comfort_oriented_design_hypothesis")
    return sorted(categories)


def _graphic_tags(record: Mapping[str, Any]) -> List[str]:
    asset_id = str(record["id"])
    module = str(record["_module"])
    tags: Set[str] = set(PATHOLOGY_TAGS.get(asset_id, ()))

    if module in {
        "core_realistic_v2",
        "head_details_v2",
        "cranial_vascular_v2",
        "neural_detail_v3",
        "cranial_detail_v3",
        "intracranial_micro_v3",
    } and asset_id not in EXTERNAL_ANATOMY_IDS:
        tags.add("internal_anatomy")
    if asset_id in {"brain_structures_generic", "cerebral_arteries_generic"}:
        tags.add("internal_anatomy")
    if asset_id in EXTERNAL_ANATOMY_IDS:
        tags.add("external_anatomy")
    if asset_id in VASCULAR_IDS:
        tags.add("vascular_anatomy")
    if asset_id in BLOOD_CONTENT_IDS:
        tags.add("blood_or_blood_components")
    if asset_id in CLOT_IDS:
        tags.add("clot_or_thrombus")
    if module == "intracranial_micro_v3" or asset_id in {
        "red_blood_cells_closeup_v2",
        "microcirculation_arterial_venous_v2",
    }:
        tags.add("microscopic_detail")
    if asset_id in CUTAWAY_IDS:
        tags.add("exposed_tissue_or_cutaway")
    if asset_id in INCISION_IDS:
        tags.add("incision_or_opening")
    if asset_id in CLOSURE_IDS:
        tags.add("suture_closure_or_dressing")
    if asset_id in NEEDLE_CATHETER_IDS:
        tags.add("needle_wire_catheter_or_drain")
    if asset_id in MEDICAL_DEVICE_IDS:
        tags.add("medical_device")
    if asset_id in ROOM_EQUIPMENT_IDS:
        tags.add("medical_equipment")
    if asset_id in FLOW_CUE_IDS:
        tags.add("fluid_or_flow_cue")
    if asset_id in ANIMATED_FLOW_IDS or bool(record.get("animated")):
        tags.add("animated_particles_or_flow")
    if asset_id in BONE_ACCESS_IDS:
        tags.add("bone_access_instrument_or_state")
    if asset_id in BONE_ANATOMY_IDS:
        tags.add("bone_anatomy")
    if asset_id in {"skull_cranium_generic", "craniotomy_bone_flap"}:
        tags.add("internal_anatomy")
    if module in {"endovascular_tools_v3", "open_cranial_tools_v3"} or asset_id in {
        "cranial_drill_generic",
        "suction_and_forceps",
    }:
        tags.add("surgical_instrument")
    if asset_id in {"patient_supine_generic", "clinical_team_generic"}:
        tags.add("body_or_clinical_staff")
    if asset_id == "spatial_step_markers":
        tags.add("procedure_sequence_cue")
    if not tags:
        tags.add("none_observed")
    return sorted(tags)


def _presentation_intensity(asset_id: str, tags: Sequence[str]) -> str:
    tag_set = set(tags)
    if asset_id in HIGH_INTENSITY_IDS:
        return "high"
    if asset_id in MINIMAL_INTENSITY_IDS:
        return "minimal"
    if asset_id in LOW_INTENSITY_IDS:
        return "low"
    if tag_set.intersection(
        {
            "hemorrhage",
            "incision_or_opening",
            "blood_or_blood_components",
            "clot_or_thrombus",
            "ischemic_tissue_or_pathology",
        }
    ):
        return "high"
    if tag_set.intersection(
        {
            "internal_anatomy",
            "vascular_anatomy",
            "microscopic_detail",
            "needle_wire_catheter_or_drain",
            "surgical_instrument",
            "medical_device",
            "bone_access_instrument_or_state",
            "animated_particles_or_flow",
            "suture_closure_or_dressing",
        }
    ):
        return "moderate"
    return "low"


def _allowed_actions(
    asset_id: str,
    tags: Sequence[str],
    aggregate_role: str,
) -> Dict[str, List[str]]:
    tag_set = set(tags)
    visibility = {
        "restore_source_visibility",
        "reduce_label_density",
    }
    if asset_id not in PRIMARY_PATHOLOGY_IDS:
        visibility.add("hide_asset")
    if "internal_anatomy" in tag_set or "microscopic_detail" in tag_set:
        visibility.add("progressive_disclosure")
        visibility.add("hide_graphic_subcomponents_if_semantically_mapped")
    if aggregate_role == "aggregate":
        visibility.add("replace_aggregate_with_components")
    elif aggregate_role == "component":
        visibility.add("replace_components_with_aggregate")
    if asset_id in SEMANTIC_REPLACEMENTS:
        visibility.add("replace_semantic_overlap")
    if asset_id in ORIENTATION_CANDIDATE_SOURCE_IDS:
        visibility.add("use_review_gated_orientation_interstitial_candidate")

    material = {
        "apply_bounded_developer_preview_tint",
        "reduce_saturation_preserving_source_access",
        "increase_roughness",
        "reduce_specular",
        "restore_source_materials",
    }
    if "animated_particles_or_flow" in tag_set or "fluid_or_flow_cue" in tag_set:
        material.add("reduce_emission")

    motion = {
        "disable_autoplay",
        "pause_runtime_motion",
        "disable_looping",
        "pause_at_initial_authored_pose",
        "block_unreviewed_motion",
        "restore_authored_motion",
    }
    if tag_set.intersection(
        {
            "animated_particles_or_flow",
            "fluid_or_flow_cue",
            "surgical_instrument",
            "medical_device",
            "needle_wire_catheter_or_drain",
        }
    ):
        motion.add("reduce_speed")
    return {
        "visibility": sorted(visibility),
        "material": sorted(material),
        "motion": sorted(motion),
    }


def _aggregate_roles(all_ids: Set[str]) -> Dict[str, str]:
    roles = {asset_id: "standalone" for asset_id in all_ids}
    for aggregate_id, components in AGGREGATE_COMPONENTS.items():
        roles[aggregate_id] = "aggregate"
        for component in components:
            if roles[component] == "standalone":
                roles[component] = "component"
    roles[ORIENTATION_CANDIDATE_ID] = "orientation_candidate"
    return roles


def _profile(
    record: Mapping[str, Any],
    exclusion_map: Mapping[str, Set[str]],
    aggregate_roles: Mapping[str, str],
) -> Dict[str, Any]:
    asset_id = str(record["id"])
    tags = _graphic_tags(record)
    aggregate_role = aggregate_roles[asset_id]
    review_status = str(record.get("clinical_review_status") or "REVIEW_STATUS_MISSING")
    if not review_status.startswith("REQUIRES_"):
        raise ValueError("unexpected review status for %s: %s" % (asset_id, review_status))

    candidate_ids = (
        [ORIENTATION_CANDIDATE_ID]
        if asset_id in ORIENTATION_CANDIDATE_SOURCE_IDS
        else []
    )
    never_co_load = set(exclusion_map[asset_id])
    if candidate_ids:
        never_co_load.update(candidate_ids)
    if asset_id == ORIENTATION_CANDIDATE_ID:
        never_co_load.update(ORIENTATION_CANDIDATE_SOURCE_IDS)

    safeguards = [
        "generic_education_only",
        "presentation_change_does_not_authorize_patient_display",
        "preserve_material_facts_and_access_to_source",
        "plain_language_fact_equivalent_required_when_hidden",
        "no_anxiety_or_distress_inference",
        "no_diagnosis_planning_navigation_or_training_use",
        "manual_restore_required",
    ]
    if tags != ["none_observed"]:
        safeguards.append("graphic_content_must_use_reviewed_progressive_disclosure")
    if asset_id in PRIMARY_PATHOLOGY_IDS:
        safeguards.append("primary_pathology_visibility_is_protected")
    if "vascular_anatomy" in tags or "blood_or_blood_components" in tags:
        safeguards.append("preserve_color_legend_and_nonquantitative_flow_warning")
    if aggregate_role == "aggregate":
        safeguards.append("aggregate_must_replace_not_augment_components")
    if asset_id in SEMANTIC_REPLACEMENTS:
        safeguards.append("semantic_replacement_does_not_imply_clinical_superiority")
    if candidate_ids or aggregate_role == "orientation_candidate":
        safeguards.extend(
            [
                "orientation_candidate_is_not_content_equivalent",
                "external_specialist_and_human_factors_approval_required",
            ]
        )

    replaces_asset_ids = set(AGGREGATE_COMPONENTS.get(asset_id, ()))
    replaces_asset_ids.update(SEMANTIC_REPLACEMENTS.get(asset_id, ()))

    return {
        "asset_id": asset_id,
        "title": str(record.get("title") or asset_id),
        "module": str(record["_module"]),
        "source_manifest": str(record["_source_manifest"]),
        "content_categories": _content_categories(record),
        "graphic_content_tags": tags,
        "presentation_intensity": _presentation_intensity(asset_id, tags),
        "allowed_actions": _allowed_actions(asset_id, tags, aggregate_role),
        "replacement_rules": {
            "role": aggregate_role,
            "replaces_asset_ids": sorted(replaces_asset_ids),
            "never_co_load_with_asset_ids": sorted(never_co_load),
            "candidate_replacement_asset_ids": candidate_ids,
            "candidate_use": (
                "orientation_interstitial_only_not_content_equivalent"
                if candidate_ids
                else "not_applicable"
            ),
            "approval_required": True,
            "source_must_remain_available": True,
            "restore_source_before_medical_detail": True,
        },
        "clinical_safeguards": {
            "patient_display_authorized": False,
            "required_review_status": review_status,
            "patient_specific": bool(record.get("patient_specific", False)),
            "non_diagnostic": True,
            "anxiety_inference_allowed": False,
            "preserve_material_facts": True,
            "safeguard_tags": sorted(set(safeguards)),
        },
    }


def build_payload() -> Dict[str, Any]:
    records, manifest_paths, manifest_digest = _load_catalog()
    all_ids = {str(record["id"]) for record in records}
    if ORIENTATION_CANDIDATE_ID not in all_ids:
        raise ValueError("orientation candidate is absent from the release catalog")
    exclusions = _exclusion_map(all_ids)
    for left, right in _declared_exclusion_pairs(all_ids):
        if right not in exclusions[left] or left not in exclusions[right]:
            raise ValueError(
                "profile exclusions do not cover manifest-declared pair: %s, %s"
                % (left, right)
            )
    roles = _aggregate_roles(all_ids)
    profiles = sorted(
        (_profile(record, exclusions, roles) for record in records),
        key=lambda profile: str(profile["asset_id"]),
    )

    payload: Dict[str, Any] = {
        "$schema": "./catalog_adaptation_profiles.schema.json",
        "schema_version": PROFILE_SCHEMA_VERSION,
        "generated_from": {
            "manifest_count": len(manifest_paths),
            "released_asset_count": len(profiles),
            "manifest_set_sha256": manifest_digest,
            "manifest_paths": manifest_paths,
            "held_asset_ids_excluded": sorted(HELD_ASSET_IDS),
        },
        "scope": {
            "purpose": "Authoring-time, non-destructive visual-comfort routing for candidate generic patient/family education; not patient-display authorization.",
            "presentation_intensity_is_clinical_score": False,
            "anxiety_inference_supported": False,
            "biometric_inputs_supported": False,
            "patient_display_authorization_conferred": False,
            "profile_actions_mutate_source_usdz": False,
            "material_facts_may_be_removed": False,
        },
        "action_vocabulary": ACTION_VOCABULARY,
        "profiles": profiles,
    }
    validate_payload(payload)
    return payload


def validate_payload(payload: Mapping[str, Any]) -> None:
    generated_from = payload.get("generated_from", {})
    profiles = payload.get("profiles", [])
    if generated_from.get("manifest_count") != EXPECTED_MANIFEST_COUNT:
        raise ValueError("profile manifest count is not 12")
    if generated_from.get("released_asset_count") != EXPECTED_RELEASE_ASSET_COUNT:
        raise ValueError("profile release count is not 135")
    if len(profiles) != EXPECTED_RELEASE_ASSET_COUNT:
        raise ValueError("profile list does not contain 135 records")

    ids = [str(profile.get("asset_id")) for profile in profiles]
    if len(ids) != len(set(ids)):
        raise ValueError("profile IDs are not unique")
    if set(ids).intersection(HELD_ASSET_IDS):
        raise ValueError("held IDs are present in the profile")

    catalog_records, _, digest = _load_catalog()
    catalog_ids = {str(record["id"]) for record in catalog_records}
    if set(ids) != catalog_ids:
        missing = sorted(catalog_ids.difference(ids))
        extra = sorted(set(ids).difference(catalog_ids))
        raise ValueError("profile/catalog mismatch missing=%s extra=%s" % (missing, extra))
    if generated_from.get("manifest_set_sha256") != digest:
        raise ValueError("profile manifest digest is stale")

    action_vocab = payload.get("action_vocabulary", {})
    profile_by_id = {str(profile["asset_id"]): profile for profile in profiles}
    role_counts: Dict[str, int] = {}
    for profile in profiles:
        asset_id = str(profile["asset_id"])
        if profile.get("presentation_intensity") not in {"minimal", "low", "moderate", "high"}:
            raise ValueError("invalid presentation intensity for %s" % asset_id)
        if not profile.get("content_categories") or not profile.get("graphic_content_tags"):
            raise ValueError("empty categorization for %s" % asset_id)
        unknown_categories = set(profile.get("content_categories", [])).difference(
            CONTENT_CATEGORY_VOCABULARY
        )
        if unknown_categories:
            raise ValueError(
                "unknown content categories for %s: %s"
                % (asset_id, sorted(unknown_categories))
            )
        unknown_graphic_tags = set(profile.get("graphic_content_tags", [])).difference(
            GRAPHIC_CONTENT_TAG_VOCABULARY
        )
        if unknown_graphic_tags:
            raise ValueError(
                "unknown graphic-content tags for %s: %s"
                % (asset_id, sorted(unknown_graphic_tags))
            )
        module = str(profile.get("module"))
        graphic_tags = set(profile.get("graphic_content_tags", []))
        if module in {"open_cranial_tools_v3", "endovascular_tools_v3"} and "surgical_instrument" not in graphic_tags:
            raise ValueError("tool profile lacks surgical-instrument tag: %s" % asset_id)
        if module == "realistic_devices_v2" and "medical_device" not in graphic_tags:
            raise ValueError("device profile lacks medical-device tag: %s" % asset_id)
        if module == "intracranial_micro_v3" and not {
            "internal_anatomy",
            "microscopic_detail",
        }.issubset(graphic_tags):
            raise ValueError("micro profile lacks internal/microscopic tags: %s" % asset_id)
        if module in {"neural_detail_v3", "cranial_detail_v3"} and "internal_anatomy" not in graphic_tags:
            raise ValueError("neural/cranial profile lacks internal-anatomy tag: %s" % asset_id)
        if module == "cranial_vascular_v2" and "vascular_anatomy" not in graphic_tags:
            raise ValueError("vascular profile lacks vascular-anatomy tag: %s" % asset_id)
        if module == "cerebral_bloodflow_v2" and graphic_tags == {"none_observed"}:
            raise ValueError("blood-flow profile lacks content tag: %s" % asset_id)
        safeguards = profile.get("clinical_safeguards", {})
        if safeguards.get("patient_display_authorized") is not False:
            raise ValueError("profile confers display authorization for %s" % asset_id)
        if safeguards.get("anxiety_inference_allowed") is not False:
            raise ValueError("profile permits anxiety inference for %s" % asset_id)
        if safeguards.get("preserve_material_facts") is not True:
            raise ValueError("profile permits material-fact removal for %s" % asset_id)
        if safeguards.get("patient_specific") is not False:
            raise ValueError("patient-specific asset entered generic profile: %s" % asset_id)
        actions = profile.get("allowed_actions", {})
        for kind in ("visibility", "material", "motion"):
            allowed = actions.get(kind, [])
            if not allowed:
                raise ValueError("%s actions empty for %s" % (kind, asset_id))
            unknown = sorted(set(allowed).difference(action_vocab.get(kind, {})))
            if unknown:
                raise ValueError("unknown %s actions for %s: %s" % (kind, asset_id, unknown))
        if asset_id in PRIMARY_PATHOLOGY_IDS:
            if "hide_asset" in actions.get("visibility", []):
                raise ValueError("primary pathology permits whole-asset hiding: %s" % asset_id)
            if "primary_pathology_visibility_is_protected" not in safeguards.get("safeguard_tags", []):
                raise ValueError("primary-pathology safeguard missing for %s" % asset_id)
        rules = profile.get("replacement_rules", {})
        role = str(rules.get("role"))
        role_counts[role] = role_counts.get(role, 0) + 1
        referenced = set(rules.get("replaces_asset_ids", []))
        referenced.update(rules.get("never_co_load_with_asset_ids", []))
        referenced.update(rules.get("candidate_replacement_asset_ids", []))
        unknown_references = sorted(referenced.difference(catalog_ids))
        if unknown_references:
            raise ValueError("unknown replacement IDs for %s: %s" % (asset_id, unknown_references))
        if rules.get("approval_required") is not True:
            raise ValueError("replacement lacks approval gate for %s" % asset_id)
        expected_replacements = set(AGGREGATE_COMPONENTS.get(asset_id, ()))
        expected_replacements.update(SEMANTIC_REPLACEMENTS.get(asset_id, ()))
        if set(rules.get("replaces_asset_ids", [])) != expected_replacements:
            raise ValueError("replacement mapping drift for %s" % asset_id)
        if asset_id in SEMANTIC_REPLACEMENTS:
            if "replace_semantic_overlap" not in actions.get("visibility", []):
                raise ValueError("semantic replacement action missing for %s" % asset_id)
            if "semantic_replacement_does_not_imply_clinical_superiority" not in safeguards.get("safeguard_tags", []):
                raise ValueError("semantic replacement safeguard missing for %s" % asset_id)
        never_co_load = set(rules.get("never_co_load_with_asset_ids", []))
        if not set(rules.get("replaces_asset_ids", [])).issubset(never_co_load):
            raise ValueError("aggregate replacement is not excluded for %s" % asset_id)
        for related_id in never_co_load:
            related_rules = profile_by_id[related_id]["replacement_rules"]
            if asset_id not in related_rules.get("never_co_load_with_asset_ids", []):
                raise ValueError(
                    "never-co-load rule is not symmetric: %s, %s"
                    % (asset_id, related_id)
                )
    if role_counts.get("aggregate") != len(AGGREGATE_COMPONENTS):
        raise ValueError("aggregate profile count does not match the composition map")
    if role_counts.get("orientation_candidate") != 1:
        raise ValueError("expected exactly one orientation-candidate profile")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the committed profile and fail if regeneration would change it",
    )
    args = parser.parse_args()
    payload = build_payload()
    rendered = json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + "\n"

    if args.check:
        if not OUTPUT_PATH.is_file():
            raise SystemExit("profile file is missing: %s" % OUTPUT_PATH)
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != rendered:
            raise SystemExit("profile file is stale; run %s" % Path(__file__).name)
        validate_payload(json.loads(current))
        print(
            "PASS: %d/%d released assets profiled across %d manifests; held assets absent"
            % (
                len(payload["profiles"]),
                EXPECTED_RELEASE_ASSET_COUNT,
                EXPECTED_MANIFEST_COUNT,
            )
        )
        return 0

    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print("wrote %s with %d profiles" % (OUTPUT_PATH, len(payload["profiles"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
