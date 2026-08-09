#!/usr/bin/env python3
"""Deterministically validate the isolated Page 2 interface contract pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "asset_manifest_figma_page2_surgical_interface_v1.json"
EXPECTED_CONTRACTS = {
    "surgical_walkthrough_scene_catalog_v1.json",
    "surgical_walkthrough_anchor_map_v1.json",
    "surgical_walkthrough_copy_catalog_v1.json",
}
EXPECTED_PATHWAYS = {
    "EVT",
    "OPEN_CRANIOTOMY",
    "DECOMPRESSIVE_CRANIECTOMY",
    "OPTIONAL_EVD",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        fail(f"{path.name}: top-level JSON value must be an object")
    return value


def digest(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def validate_manifest() -> tuple[dict, list[Path]]:
    manifest = load_json(MANIFEST)
    if manifest.get("module_id") != "figma_page2_surgical_interface_v1":
        fail("manifest: unexpected module_id")
    if manifest.get("patient_display_authorized") is not False:
        fail("manifest: patient_display_authorized must be false")

    resources = manifest.get("resources")
    if not isinstance(resources, list):
        fail("manifest: resources must be an array")
    if manifest.get("resource_count") != len(resources):
        fail("manifest: resource_count does not match resources length")

    ids: set[str] = set()
    paths: set[str] = set()
    resolved: list[Path] = []
    root_resolved = ROOT.resolve()
    for record in resources:
        if not isinstance(record, dict):
            fail("manifest: every resource record must be an object")
        resource_id = record.get("id")
        relative = record.get("path")
        if not isinstance(resource_id, str) or not resource_id:
            fail("manifest: resource id is missing")
        if resource_id in ids:
            fail(f"manifest: duplicate resource id {resource_id}")
        ids.add(resource_id)
        if not isinstance(relative, str) or not relative:
            fail(f"manifest: invalid path for {resource_id}")
        if relative in paths:
            fail(f"manifest: duplicate path {relative}")
        paths.add(relative)
        path = (ROOT / relative).resolve()
        if path.parent != root_resolved:
            fail(f"manifest: path escapes isolated pack: {relative}")
        if path == MANIFEST.resolve():
            fail("manifest: self-hashing is not allowed")
        if not path.is_file():
            fail(f"manifest: missing resource {relative}")
        actual_bytes, actual_hash = digest(path)
        if record.get("bytes") != actual_bytes:
            fail(f"manifest: byte-count mismatch for {relative}")
        if record.get("sha256") != actual_hash:
            fail(f"manifest: SHA-256 mismatch for {relative}")
        resolved.append(path)
    return manifest, resolved


def validate_common_json(resources: list[Path]) -> None:
    for path in resources:
        if path.suffix != ".json":
            continue
        value = load_json(path)
        if value.get("module_id") != "figma_page2_surgical_interface_v1":
            fail(f"{path.name}: unexpected module_id")
        if value.get("patient_display_authorized") is not False:
            fail(f"{path.name}: patient_display_authorized must be false")


def validate_scene_catalog() -> None:
    value = load_json(ROOT / "surgical_walkthrough_scene_catalog_v1.json")
    release = value.get("global_release_contract", {})
    if release.get("default_pathway_id") is not None:
        fail("scene catalog: default_pathway_id must be null")
    if release.get("default_scene_id") is not None:
        fail("scene catalog: default_scene_id must be null")
    if release.get("cross_pathway_transition_allowed") is not False:
        fail("scene catalog: cross-pathway transitions must be disabled")
    pathways = value.get("pathways", [])
    found = {item.get("id") for item in pathways}
    if found != EXPECTED_PATHWAYS:
        fail("scene catalog: exact pathway separation is missing")
    for pathway in pathways:
        if pathway.get("default_enabled") is not False:
            fail(f"scene catalog: {pathway.get('id')} must default disabled")
        for scene in pathway.get("scenes", []):
            if scene.get("display_copy") is not None:
                fail(f"scene catalog: {scene.get('id')} display_copy must be null")
            if scene.get("asset_binding") is not None:
                fail(f"scene catalog: {scene.get('id')} asset_binding must be null")


def validate_anchor_map() -> None:
    value = load_json(ROOT / "surgical_walkthrough_anchor_map_v1.json")
    if value.get("coordinate_space") is not None:
        fail("anchor map: coordinate_space must be null")
    null_fields = (
        "source_asset_id",
        "source_asset_sha256",
        "entity_selector",
        "local_transform_m",
        "display_copy_slot_id",
        "display_copy",
    )
    for request in value.get("requests", []):
        for field in null_fields:
            if request.get(field) is not None:
                fail(f"anchor map: {request.get('id')} {field} must be null")
        if request.get("review_ids") != []:
            fail(f"anchor map: {request.get('id')} review_ids must be empty")
        if request.get("display_authorized") is not False:
            fail(f"anchor map: {request.get('id')} must be display-blocked")


def validate_copy_catalog() -> None:
    value = load_json(ROOT / "surgical_walkthrough_copy_catalog_v1.json")
    null_fields = (
        "title",
        "short_label",
        "body",
        "voiceover",
        "accessibility_label",
        "source_citation",
        "locale",
    )
    found_pathways: set[str] = set()
    for slot in value.get("copy_slots", []):
        found_pathways.add(slot.get("pathway_id"))
        for field in null_fields:
            if slot.get(field) is not None:
                fail(f"copy catalog: {slot.get('id')} {field} must be null")
        if slot.get("review_ids") != []:
            fail(f"copy catalog: {slot.get('id')} review_ids must be empty")
        if slot.get("display_authorized") is not False:
            fail(f"copy catalog: {slot.get('id')} must be display-blocked")
    if found_pathways != EXPECTED_PATHWAYS:
        fail("copy catalog: exact pathway separation is missing")


def validate_cross_references() -> None:
    scene_value = load_json(ROOT / "surgical_walkthrough_scene_catalog_v1.json")
    anchor_value = load_json(ROOT / "surgical_walkthrough_anchor_map_v1.json")
    copy_value = load_json(ROOT / "surgical_walkthrough_copy_catalog_v1.json")

    scenes: dict[str, tuple[str, dict]] = {}
    for pathway in scene_value.get("pathways", []):
        pathway_id = pathway.get("id")
        for scene in pathway.get("scenes", []):
            scene_id = scene.get("id")
            if not isinstance(scene_id, str) or scene_id in scenes:
                fail(f"cross-reference: duplicate or invalid scene id {scene_id}")
            scenes[scene_id] = (pathway_id, scene)

    anchors: dict[str, dict] = {}
    for anchor in anchor_value.get("requests", []):
        anchor_id = anchor.get("id")
        if not isinstance(anchor_id, str) or anchor_id in anchors:
            fail(f"cross-reference: duplicate or invalid anchor id {anchor_id}")
        anchors[anchor_id] = anchor

    slots: dict[str, dict] = {}
    for slot in copy_value.get("copy_slots", []):
        slot_id = slot.get("id")
        if not isinstance(slot_id, str) or slot_id in slots:
            fail(f"cross-reference: duplicate or invalid copy slot id {slot_id}")
        slots[slot_id] = slot

    for pathway in scene_value.get("pathways", []):
        pathway_id = pathway.get("id")
        for slot_id in pathway.get("required_copy_slot_ids", []):
            slot = slots.get(slot_id)
            if slot is None or slot.get("pathway_id") != pathway_id or slot.get("scene_id") is not None:
                fail(f"cross-reference: invalid pathway disclosure slot {slot_id}")
        for scene in pathway.get("scenes", []):
            scene_id = scene.get("id")
            slot_id = scene.get("copy_slot_id")
            slot = slots.get(slot_id)
            if slot is None or slot.get("pathway_id") != pathway_id or slot.get("scene_id") != scene_id:
                fail(f"cross-reference: invalid scene copy slot {slot_id}")
            for anchor_id in scene.get("anchor_request_ids", []):
                anchor = anchors.get(anchor_id)
                if anchor is None or anchor.get("pathway_id") != pathway_id or anchor.get("scene_id") != scene_id:
                    fail(f"cross-reference: invalid anchor request {anchor_id}")

    for anchor_id, anchor in anchors.items():
        scene_record = scenes.get(anchor.get("scene_id"))
        if scene_record is None or scene_record[0] != anchor.get("pathway_id"):
            fail(f"cross-reference: orphan anchor {anchor_id}")
    for slot_id, slot in slots.items():
        scene_id = slot.get("scene_id")
        if scene_id is None:
            continue
        scene_record = scenes.get(scene_id)
        if scene_record is None or scene_record[0] != slot.get("pathway_id"):
            fail(f"cross-reference: orphan copy slot {slot_id}")


def validate_isolation(manifest: dict) -> None:
    actual_contracts = {
        path.name
        for path in ROOT.glob("surgical_walkthrough_*_v1.json")
        if path.is_file()
    }
    if actual_contracts != EXPECTED_CONTRACTS:
        fail("pack: expected exactly three surgical_walkthrough contracts")
    forbidden_extensions = {".usdz", ".usdc", ".usd", ".blend", ".png", ".jpg", ".jpeg"}
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix.lower() in forbidden_extensions:
            fail(f"pack: forbidden geometry or artwork file {path.name}")
    if manifest.get("contains_phi") is not False:
        fail("manifest: contains_phi must be false")


def main() -> int:
    try:
        manifest, resources = validate_manifest()
        validate_common_json(resources)
        validate_scene_catalog()
        validate_anchor_map()
        validate_copy_catalog()
        validate_cross_references()
        validate_isolation(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        "PASS: 10 manifested resources; exact byte/SHA-256 checks match; "
        "3 pathway-separated contracts remain fail-closed; patient display is blocked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
