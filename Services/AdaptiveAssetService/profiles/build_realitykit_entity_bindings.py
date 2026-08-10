#!/usr/bin/env python3
"""Compile exact RealityKit child-index bindings for every released USDZ.

The generated file is revision-bound: an edit client must compare the package
SHA-256 before walking a child-index path. Classification is presentation
routing only; it is not anatomical inference or clinical approval.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


GROUPS = (
    "orientation",
    "anatomy_primary",
    "anatomy_secondary",
    "pathology_primary",
    "blood_cells",
    "blood_volume",
    "flow_cues",
    "micro_detail",
    "incision_detail",
    "surgical_field",
    "device",
    "labels",
    "environment",
)

TOKEN_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("labels", ("label", "legend", "heading", "caption", "annotation", "text_")),
    (
        "pathology_primary",
        ("clot", "thrombus", "occlusion", "hematoma", "haematoma", "edema", "oedema", "ischemic", "ischaemic", "penumbra", "at_risk"),
    ),
    ("incision_detail", ("incision", "suture", "wound", "scalp_flap", "closure_line", "staple")),
    (
        "blood_cells",
        ("rbc", "erythro", "leukocyte", "platelet", "blood_cell", "blood_element", "blood_granule", "entrapped_rbc"),
    ),
    ("blood_volume", ("blood_volume", "hematoma_volume", "haematoma_volume", "blood_pool")),
    (
        "anatomy_secondary",
        ("deep_brain", "ventricular", "dura_mater", "falx_cerebri", "tentorium_cerebelli", "meningeal", "secondary_vessel"),
    ),
    (
        "flow_cues",
        ("streamline", "flow_arrow", "blood_arrow", "flow_marker", "direction_cue", "contrast_flow", "perfusion", "circulation", "csf_direction"),
    ),
    (
        "device",
        (
            "catheter", "guidewire", "access_wire", "sheath", "dilator", "stent", "needle", "forceps", "scissors", "dissector",
            "retractor", "craniotome", "perforator", "drill", "suction", "aspiration", "pump", "canister", "tubing", "syringe",
            "manifold", "connector", "valve", "instrument", "ruler", "marker_pen", "hemostat", "haemostat", "fixation", "microprobe",
        ),
    ),
    (
        "micro_detail",
        (
            "vesicle", "granule", "tight_junction", "junction_seam", "lamellar", "channel_cue", "dendritic_spine", "nucleus",
            "astrocyte_process", "endfoot_process", "myelinating_process", "fibrin_strand", "capillary_fold", "receptor_cue",
        ),
    ),
    ("environment", ("patient", "staff", "clinical_team", "operating_table", "procedure_table", "monitor", "iv_pole", "c_arm", "room")),
)

DEVICE_MODULE_MARKERS = ("device", "tool", "thrombectomy")
VASCULAR_MARKERS = ("artery", "arterial", "vein", "venous", "vascular", "jugular", "sinus", "bloodflow", "circulation")


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _manifest_index(catalog_root: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for manifest in sorted(catalog_root.rglob("asset_manifest*.json")):
        document = json.loads(manifest.read_text(encoding="utf-8"))
        for record in document.get("assets", []):
            asset_id = record["id"]
            if asset_id in index:
                raise ValueError(f"duplicate manifest asset ID: {asset_id}")
            index[asset_id] = {
                "manifest": manifest.name,
                "module": str(record.get("module", document.get("module_id", document.get("module", document.get("kit", "unspecified"))))),
                "title": str(record.get("title", asset_id)),
                "description": str(record.get("description", "")),
            }
    return index


def _primary_group(asset_id: str, module: str, title: str) -> str:
    haystack = _normalized(" ".join((asset_id, module, title)))
    if any(token in haystack for token in ("clot", "thrombus", "occlusion", "hematoma", "edema", "ischemic_tissue")):
        return "pathology_primary"
    if any(token in haystack for token in ("scalp_incision", "scalp_closure", "closure_sutures")):
        return "incision_detail"
    if any(token in haystack for token in ("craniotomy_bone_flap", "dural_patch")):
        return "surgical_field"
    if any(token in haystack for token in ("red_blood_cell", "blood_elements")):
        return "blood_cells"
    if any(token in haystack for token in ("flow_overlay", "bloodflow_animation", "bloodflow_teaching", "interior_bloodflow", "microcirculation", "contrast_flow")):
        return "flow_cues"
    if any(token in haystack for token in ("cranial_drill", "suction_and_forceps", "evacuator_port", "evd_system")):
        return "device"
    if "spatial_step_markers" in haystack:
        return "labels"
    if "postoperative_head_dressing" in haystack:
        return "environment"
    if any(marker in haystack for marker in DEVICE_MODULE_MARKERS) and "anatomy" not in haystack:
        return "device"
    if any(token in haystack for token in ("shared_room", "patient_supine", "operating_table", "clinical_team", "vital_sign_monitor", "iv_pole", "c_arm")):
        return "environment"
    if "intracranial_micro" in haystack or "conceptual_v3" in haystack:
        return "micro_detail"
    return "anatomy_primary"


def _classify(path: str, asset_id: str, module: str, primary_group: str) -> list[str]:
    normalized_path = _normalized(path)
    normalized_asset = _normalized(asset_id)
    normalized_module = _normalized(module)
    groups: list[str] = []
    for group, tokens in TOKEN_RULES:
        if any(token in normalized_path for token in tokens):
            groups.append(group)

    if not groups:
        if any(marker in normalized_module for marker in DEVICE_MODULE_MARKERS):
            groups.append("device")
        elif any(marker in normalized_asset for marker in VASCULAR_MARKERS):
            groups.append("anatomy_primary")
        elif "intracranial_micro" in normalized_module:
            groups.append("micro_detail")
        elif any(marker in normalized_asset for marker in ("head", "brain", "skull", "cortex", "nerve", "muscle", "eye", "dura", "falx", "tentorium", "pituitary", "airway", "nasal", "ventric")):
            groups.append("anatomy_primary")
        else:
            groups.append(primary_group)

    if primary_group == "anatomy_primary" and "anatomy_primary" in groups:
        orientation_tokens = ("head", "scalp", "skull", "brain", "cortex", "cerebell", "brainstem")
        if any(token in normalized_path for token in orientation_tokens):
            groups.append("orientation")
    if "incision_detail" in groups:
        groups.append("surgical_field")
    return sorted(set(groups), key=GROUPS.index)


def build(catalog_root: Path, entity_map_path: Path) -> dict[str, Any]:
    manifests = _manifest_index(catalog_root)
    entity_map = json.loads(entity_map_path.read_text(encoding="utf-8"))
    mapped_ids = {record["assetID"] for record in entity_map["assets"]}
    if set(manifests) != mapped_ids:
        missing = sorted(set(manifests) - mapped_ids)
        extra = sorted(mapped_ids - set(manifests))
        raise ValueError(f"entity-map/catalog mismatch; missing={missing}, extra={extra}")
    if entity_map.get("failures"):
        raise ValueError("entity map contains load failures")

    assets: list[dict[str, Any]] = []
    for source in sorted(entity_map["assets"], key=lambda item: item["assetID"]):
        metadata = manifests[source["assetID"]]
        primary = _primary_group(source["assetID"], metadata["module"], metadata["title"])
        bindings: list[dict[str, Any]] = []
        for entity in source["entities"]:
            if not entity["hasModel"]:
                continue
            groups = _classify(entity["path"], source["assetID"], metadata["module"], primary)
            bindings.append(
                {
                    "child_index_path": entity["childIndexPath"],
                    "debug_path": entity["path"],
                    "entity_name": entity["name"],
                    "material_slots": entity["materialCount"],
                    "semantic_groups": groups,
                    "automatic_visibility_change_allowed": primary not in groups,
                }
            )
        if not bindings:
            raise ValueError(f"asset has no renderable entity binding: {source['assetID']}")
        if not any(primary in binding["semantic_groups"] for binding in bindings):
            for binding in bindings:
                binding["semantic_groups"] = sorted(
                    set(binding["semantic_groups"] + [primary]),
                    key=GROUPS.index,
                )
                binding["automatic_visibility_change_allowed"] = False
        group_counts = {
            group: sum(group in binding["semantic_groups"] for binding in bindings)
            for group in GROUPS
            if any(group in binding["semantic_groups"] for binding in bindings)
        }
        animation_bindings = [
            {
                "child_index_path": entity["childIndexPath"],
                "debug_path": entity["path"],
                "animation_resource_count": entity["animationCount"],
            }
            for entity in source["entities"]
            if entity["animationCount"] > 0
        ]
        assets.append(
            {
                "asset_id": source["assetID"],
                "source_manifest": metadata["manifest"],
                "module": metadata["module"],
                "package_relative_path": source["packageRelativePath"],
                "package_bytes": source["packageBytes"],
                "package_sha256": source["packageSHA256"],
                "primary_semantic_group": primary,
                "model_entity_count": len(bindings),
                "animation_resource_count": source["animationCount"],
                "animation_bindings": animation_bindings,
                "semantic_group_counts": group_counts,
                "bindings": bindings,
            }
        )

    return {
        "schema_version": "1.0",
        "purpose": "Exact, package-revision-bound RealityKit entity selectors for reversible presentation editing",
        "selector_contract": {
            "kind": "child_index_path",
            "root": "Entity returned by Entity.load(contentsOf:)",
            "revision_gate": "Reject the map unless package_sha256 matches the loaded USDZ bytes.",
            "failure_behavior": "Do not guess or silently hide content; use the profile fallback and preserve the source view.",
        },
        "classification_notice": "Semantic groups are deterministic presentation routing, not clinical or anatomical validation.",
        "asset_count": len(assets),
        "model_entity_count": sum(asset["model_entity_count"] for asset in assets),
        "assets": assets,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-root", type=Path, required=True)
    parser.add_argument("--entity-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = build(args.catalog_root.resolve(), args.entity_map.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
