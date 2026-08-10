"""Revision-bound RealityKit entity bindings for executable edit recipes."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .catalog import AssetCatalog
from .profiles import AssetAdaptationProfile


KNOWN_GROUPS = {
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
}


class BindingError(RuntimeError):
    """The executable entity map is absent, stale, or malformed."""


@dataclass(frozen=True)
class AssetBindings:
    asset_id: str
    package_sha256: str
    package_bytes: int
    primary_semantic_group: str
    model_entity_count: int
    animation_resource_count: int
    semantic_group_counts: dict[str, int]
    bindings: tuple[dict[str, Any], ...]
    animation_bindings: tuple[dict[str, Any], ...]

    def public_summary(self) -> dict[str, Any]:
        return {
            "mapping_status": "exact_revision_bound",
            "selector_kind": "child_index_path",
            "package_sha256": self.package_sha256,
            "model_entity_count": self.model_entity_count,
            "animation_resource_count": self.animation_resource_count,
            "primary_semantic_group": self.primary_semantic_group,
            "semantic_group_counts": dict(self.semantic_group_counts),
        }


class EntityBindingCatalog:
    """Loads and verifies exact selectors against the indexed USDZ revisions."""

    def __init__(self, path: Path, catalog: AssetCatalog):
        try:
            resolved = path.expanduser().resolve(strict=True)
            raw = resolved.read_bytes()
            document = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise BindingError(f"could not load RealityKit entity bindings: {exc}") from exc
        if not isinstance(document, dict) or document.get("schema_version") != "1.0":
            raise BindingError("unsupported RealityKit entity-binding schema")
        records = document.get("assets")
        if not isinstance(records, list):
            raise BindingError("RealityKit entity bindings contain no assets array")

        topology = self._load_topology(resolved.with_name("realitykit_entity_map.json"), catalog)

        bindings: dict[str, AssetBindings] = {}
        for record in records:
            parsed = self._parse_record(record, catalog, topology)
            if parsed.asset_id in bindings:
                raise BindingError(f"duplicate RealityKit entity binding: {parsed.asset_id}")
            bindings[parsed.asset_id] = parsed

        catalog_ids = {asset["asset_id"] for asset in catalog.public_assets()}
        if set(bindings) != catalog_ids:
            missing = sorted(catalog_ids - set(bindings))
            extra = sorted(set(bindings) - catalog_ids)
            raise BindingError(f"RealityKit entity-binding coverage mismatch; missing={missing}, extra={extra}")
        declared_asset_count = document.get("asset_count")
        if (
            isinstance(declared_asset_count, bool)
            or not isinstance(declared_asset_count, int)
            or declared_asset_count != len(bindings)
        ):
            raise BindingError("RealityKit entity-binding asset count does not match its records")
        declared_model_count = document.get("model_entity_count")
        observed_model_count = sum(binding.model_entity_count for binding in bindings.values())
        if (
            isinstance(declared_model_count, bool)
            or not isinstance(declared_model_count, int)
            or declared_model_count != observed_model_count
        ):
            raise BindingError("RealityKit entity-binding model count does not match its records")
        self.path = resolved
        self.document_sha256 = hashlib.sha256(raw).hexdigest()
        self._bindings = bindings

    @property
    def asset_count(self) -> int:
        return len(self._bindings)

    def get(self, asset_id: str) -> AssetBindings | None:
        return self._bindings.get(asset_id)

    @staticmethod
    def _child_index_path(value: Any, asset_id: str) -> tuple[int, ...]:
        if not isinstance(value, list) or any(isinstance(index, bool) or not isinstance(index, int) or index < 0 for index in value):
            raise BindingError(f"asset {asset_id} has an invalid child-index path")
        return tuple(value)

    @staticmethod
    def _nonnegative_int(value: Any, field: str, asset_id: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise BindingError(f"asset {asset_id} has an invalid {field}")
        return value

    @staticmethod
    def _string(value: Any, field: str, asset_id: str, *, allow_empty: bool = False) -> str:
        if not isinstance(value, str) or (not allow_empty and not value):
            raise BindingError(f"asset {asset_id} has an invalid {field}")
        return value

    @classmethod
    def _load_topology(
        cls,
        path: Path,
        catalog: AssetCatalog,
    ) -> dict[str, dict[tuple[int, ...], dict[str, Any]]]:
        try:
            raw = path.resolve(strict=True).read_bytes()
            document = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise BindingError(f"could not load RealityKit entity topology: {exc}") from exc
        if not isinstance(document, dict) or document.get("schemaVersion") != "1.0":
            raise BindingError("unsupported RealityKit entity-topology schema")
        if document.get("failures") != []:
            raise BindingError("RealityKit entity topology contains load failures")
        raw_assets = document.get("assets")
        if not isinstance(raw_assets, list):
            raise BindingError("RealityKit entity topology contains no assets array")

        topology: dict[str, dict[tuple[int, ...], dict[str, Any]]] = {}
        for raw_asset in raw_assets:
            if not isinstance(raw_asset, dict) or not isinstance(raw_asset.get("assetID"), str):
                raise BindingError("RealityKit entity topology contains an invalid asset record")
            asset_id = raw_asset["assetID"]
            asset = catalog.get(asset_id)
            if asset is None:
                raise BindingError(f"RealityKit entity topology references unknown asset: {asset_id}")
            if asset_id in topology:
                raise BindingError(f"duplicate RealityKit entity topology: {asset_id}")
            if (
                raw_asset.get("packageSHA256") != asset.package_sha256
                or raw_asset.get("packageBytes") != asset.package_bytes
            ):
                raise BindingError(f"RealityKit entity topology is stale for package revision: {asset_id}")
            try:
                expected_package_path = asset.package_path.relative_to(catalog.root).as_posix()
            except ValueError as exc:
                raise BindingError(f"asset {asset_id} escaped the configured catalog") from exc
            if raw_asset.get("packageRelativePath") != expected_package_path:
                raise BindingError(f"RealityKit entity topology has a package-path mismatch: {asset_id}")

            raw_entities = raw_asset.get("entities")
            if not isinstance(raw_entities, list) or not raw_entities:
                raise BindingError(f"asset {asset_id} has no RealityKit entity topology")
            entities: dict[tuple[int, ...], dict[str, Any]] = {}
            for raw_entity in raw_entities:
                if not isinstance(raw_entity, dict):
                    raise BindingError(f"asset {asset_id} has a malformed topology entity")
                index_path = cls._child_index_path(raw_entity.get("childIndexPath"), asset_id)
                if index_path in entities:
                    raise BindingError(f"asset {asset_id} has a duplicate topology child-index path")
                has_model = raw_entity.get("hasModel")
                if not isinstance(has_model, bool):
                    raise BindingError(f"asset {asset_id} has an invalid topology model flag")
                entities[index_path] = {
                    "debug_path": cls._string(raw_entity.get("path"), "topology debug path", asset_id),
                    "entity_name": cls._string(
                        raw_entity.get("name"),
                        "topology entity name",
                        asset_id,
                        allow_empty=True,
                    ),
                    "has_model": has_model,
                    "material_slots": cls._nonnegative_int(
                        raw_entity.get("materialCount"),
                        "topology material count",
                        asset_id,
                    ),
                    "animation_resource_count": cls._nonnegative_int(
                        raw_entity.get("animationCount"),
                        "topology animation count",
                        asset_id,
                    ),
                    "child_count": cls._nonnegative_int(
                        raw_entity.get("childCount"),
                        "topology child count",
                        asset_id,
                    ),
                }

            if () not in entities:
                raise BindingError(f"asset {asset_id} topology has no root entity")
            children_by_parent: dict[tuple[int, ...], list[int]] = {}
            for index_path in entities:
                if index_path:
                    children_by_parent.setdefault(index_path[:-1], []).append(index_path[-1])
            for index_path, entity in entities.items():
                if index_path:
                    parent = entities.get(index_path[:-1])
                    if parent is None or index_path[-1] >= parent["child_count"]:
                        raise BindingError(f"asset {asset_id} has an out-of-tree topology selector")
                observed_children = sorted(children_by_parent.get(index_path, []))
                if observed_children != list(range(entity["child_count"])):
                    raise BindingError(f"asset {asset_id} topology child count is inconsistent")

            observed_entity_count = len(entities)
            observed_model_count = sum(entity["has_model"] for entity in entities.values())
            observed_material_count = sum(entity["material_slots"] for entity in entities.values())
            observed_animation_count = sum(
                entity["animation_resource_count"] for entity in entities.values()
            )
            for field, observed in (
                ("entityCount", observed_entity_count),
                ("modelCount", observed_model_count),
                ("materialCount", observed_material_count),
                ("animationCount", observed_animation_count),
            ):
                declared = raw_asset.get(field)
                if isinstance(declared, bool) or not isinstance(declared, int) or declared != observed:
                    raise BindingError(f"asset {asset_id} topology {field} is inconsistent")
            topology[asset_id] = entities

        catalog_ids = {asset["asset_id"] for asset in catalog.public_assets()}
        if set(topology) != catalog_ids:
            missing = sorted(catalog_ids - set(topology))
            extra = sorted(set(topology) - catalog_ids)
            raise BindingError(f"RealityKit entity-topology coverage mismatch; missing={missing}, extra={extra}")
        return topology

    @classmethod
    def _parse_record(
        cls,
        record: Any,
        catalog: AssetCatalog,
        topology: dict[str, dict[tuple[int, ...], dict[str, Any]]],
    ) -> AssetBindings:
        if not isinstance(record, dict) or not isinstance(record.get("asset_id"), str):
            raise BindingError("RealityKit entity bindings contain an invalid asset record")
        asset_id = record["asset_id"]
        asset = catalog.get(asset_id)
        if asset is None:
            raise BindingError(f"RealityKit entity binding references unknown asset: {asset_id}")
        if record.get("package_sha256") != asset.package_sha256 or record.get("package_bytes") != asset.package_bytes:
            raise BindingError(f"RealityKit entity binding is stale for package revision: {asset_id}")
        primary_group = record.get("primary_semantic_group")
        if primary_group not in KNOWN_GROUPS:
            raise BindingError(f"asset {asset_id} has an invalid primary semantic group")
        if record.get("package_relative_path") != asset.package_path.relative_to(catalog.root).as_posix():
            raise BindingError(f"asset {asset_id} has a package-path mismatch")
        if record.get("source_manifest") != asset.manifest_name:
            raise BindingError(f"asset {asset_id} has a source-manifest mismatch")

        raw_bindings = record.get("bindings")
        if not isinstance(raw_bindings, list) or not raw_bindings:
            raise BindingError(f"asset {asset_id} has no renderable entity bindings")
        parsed_bindings: list[dict[str, Any]] = []
        seen_paths: set[tuple[int, ...]] = set()
        for binding in raw_bindings:
            if not isinstance(binding, dict):
                raise BindingError(f"asset {asset_id} has a malformed renderable binding")
            index_path = cls._child_index_path(binding.get("child_index_path"), asset_id)
            if index_path in seen_paths:
                raise BindingError(f"asset {asset_id} has a duplicate child-index path")
            seen_paths.add(index_path)
            topology_entity = topology[asset_id].get(index_path)
            if topology_entity is None or not topology_entity["has_model"]:
                raise BindingError(f"asset {asset_id} has an out-of-tree renderable selector")
            groups = binding.get("semantic_groups")
            if (
                not isinstance(groups, list)
                or not groups
                or any(not isinstance(group, str) or group not in KNOWN_GROUPS for group in groups)
                or len(set(groups)) != len(groups)
            ):
                raise BindingError(f"asset {asset_id} has invalid semantic groups")
            automatic_visibility = binding.get("automatic_visibility_change_allowed")
            if not isinstance(automatic_visibility, bool):
                raise BindingError(f"asset {asset_id} has an invalid automatic-visibility flag")
            if automatic_visibility != (primary_group not in groups):
                raise BindingError(f"asset {asset_id} violates the primary-group visibility safeguard")
            debug_path = cls._string(binding.get("debug_path"), "debug path", asset_id)
            entity_name = cls._string(
                binding.get("entity_name"),
                "entity name",
                asset_id,
                allow_empty=True,
            )
            material_slots = cls._nonnegative_int(binding.get("material_slots"), "material slots", asset_id)
            if (
                debug_path != topology_entity["debug_path"]
                or entity_name != topology_entity["entity_name"]
                or material_slots != topology_entity["material_slots"]
            ):
                raise BindingError(f"asset {asset_id} renderable binding disagrees with RealityKit topology")
            parsed_bindings.append(
                {
                    "child_index_path": list(index_path),
                    "debug_path": debug_path,
                    "entity_name": entity_name,
                    "material_slots": material_slots,
                    "semantic_groups": list(groups),
                    "automatic_visibility_change_allowed": automatic_visibility,
                }
            )
        expected_model_paths = {
            index_path for index_path, entity in topology[asset_id].items() if entity["has_model"]
        }
        if seen_paths != expected_model_paths:
            raise BindingError(f"asset {asset_id} renderable bindings do not cover its RealityKit models")

        raw_animations = record.get("animation_bindings", [])
        if not isinstance(raw_animations, list):
            raise BindingError(f"asset {asset_id} has invalid animation bindings")
        animations: list[dict[str, Any]] = []
        seen_animation_paths: set[tuple[int, ...]] = set()
        for binding in raw_animations:
            if not isinstance(binding, dict):
                raise BindingError(f"asset {asset_id} has a malformed animation binding")
            index_path = cls._child_index_path(binding.get("child_index_path"), asset_id)
            if index_path in seen_animation_paths:
                raise BindingError(f"asset {asset_id} has a duplicate animation child-index path")
            seen_animation_paths.add(index_path)
            topology_entity = topology[asset_id].get(index_path)
            animation_resource_count = cls._nonnegative_int(
                binding.get("animation_resource_count"),
                "animation resource count",
                asset_id,
            )
            debug_path = cls._string(binding.get("debug_path"), "animation debug path", asset_id)
            if (
                topology_entity is None
                or topology_entity["animation_resource_count"] <= 0
                or animation_resource_count != topology_entity["animation_resource_count"]
                or debug_path != topology_entity["debug_path"]
            ):
                raise BindingError(f"asset {asset_id} animation binding disagrees with RealityKit topology")
            animations.append(
                {
                    "child_index_path": list(index_path),
                    "debug_path": debug_path,
                    "animation_resource_count": animation_resource_count,
                }
            )
        expected_animation_paths = {
            index_path
            for index_path, entity in topology[asset_id].items()
            if entity["animation_resource_count"] > 0
        }
        if seen_animation_paths != expected_animation_paths:
            raise BindingError(f"asset {asset_id} animation bindings do not cover its RealityKit animations")
        model_count = record.get("model_entity_count")
        if isinstance(model_count, bool) or not isinstance(model_count, int) or model_count != len(parsed_bindings):
            raise BindingError(f"asset {asset_id} model-entity count does not match its bindings")
        animation_count = record.get("animation_resource_count", 0)
        if (
            isinstance(animation_count, bool)
            or not isinstance(animation_count, int)
            or animation_count != sum(item["animation_resource_count"] for item in animations)
        ):
            raise BindingError(f"asset {asset_id} animation count does not match its bindings")

        counts = record.get("semantic_group_counts")
        if (
            not isinstance(counts, dict)
            or not counts
            or any(not isinstance(group, str) or group not in KNOWN_GROUPS for group in counts)
        ):
            raise BindingError(f"asset {asset_id} has invalid semantic-group counts")
        observed_counts = {
            group: sum(group in binding["semantic_groups"] for binding in parsed_bindings)
            for group in KNOWN_GROUPS
        }
        expected_counts = {group: count for group, count in observed_counts.items() if count > 0}
        if set(counts) != set(expected_counts):
            raise BindingError(f"asset {asset_id} semantic-group counts are incomplete")
        for group, count in counts.items():
            if isinstance(count, bool) or not isinstance(count, int) or count != observed_counts[group]:
                raise BindingError(f"asset {asset_id} semantic-group count mismatch for {group}")

        return AssetBindings(
            asset_id=asset_id,
            package_sha256=asset.package_sha256,
            package_bytes=asset.package_bytes,
            primary_semantic_group=primary_group,
            model_entity_count=len(parsed_bindings),
            animation_resource_count=animation_count,
            semantic_group_counts=dict(counts),
            bindings=tuple(parsed_bindings),
            animation_bindings=tuple(animations),
        )

    def application_plan(
        self,
        asset_id: str,
        recipe: dict[str, Any],
        profile: AssetAdaptationProfile,
    ) -> dict[str, Any]:
        asset = self._bindings[asset_id]
        hidden_groups = set(recipe["detail"]["hidden_layer_groups"])
        present_groups = set(asset.semantic_group_counts)
        requested_hidden_groups_present = sorted(hidden_groups.intersection(present_groups))
        requested_hidden_groups_not_present = sorted(hidden_groups.difference(present_groups))
        visibility_allowed = (
            "hide_graphic_subcomponents_if_semantically_mapped"
            in profile.allowed_actions["visibility"]
        )
        visibility_operations: list[dict[str, Any]] = []
        protected_matches = 0
        profile_blocked_matches = 0
        for binding in asset.bindings:
            matches = sorted(hidden_groups.intersection(binding["semantic_groups"]))
            if not matches:
                continue
            if not binding["automatic_visibility_change_allowed"]:
                protected_matches += 1
                continue
            if not visibility_allowed:
                profile_blocked_matches += 1
                continue
            visibility_operations.append(
                {
                    "operation": "set_enabled",
                    "value": False,
                    "child_index_path": binding["child_index_path"],
                    "debug_path": binding["debug_path"],
                    "matched_groups": matches,
                }
            )

        material = recipe["materials"]
        material_actions = set(profile.allowed_actions["material"])
        material_parameters: dict[str, Any] = {
            "preserve_source_alpha": True,
            "unsupported_material_behavior": "preserve_source_material",
            "patient_display_authorized": False,
        }
        if "reduce_saturation_preserving_source_access" in material_actions:
            material_parameters["saturation_multiplier"] = material["saturation_multiplier"]
        if "increase_roughness" in material_actions:
            material_parameters["roughness_floor"] = material["roughness_floor"]
        if "reduce_specular" in material_actions:
            material_parameters["specular_multiplier"] = material["specular_multiplier"]
        if "apply_bounded_developer_preview_tint" in material_actions:
            material_parameters["tint_rgba"] = material["tint_rgba"]
        if "reduce_emission" in material_actions:
            material_parameters["emission_multiplier"] = material.get("emission_multiplier", 0.65)

        material_change_requested = recipe["adaptation_tier"] != "clinical_detail"
        material_protected_groups = {"labels", "pathology_primary"}
        material_protected_entities = sum(
            bool(material_protected_groups.intersection(binding["semantic_groups"]))
            for binding in asset.bindings
        )
        material_operations = [
            {
                "operation": "transform_existing_model_materials",
                "child_index_path": binding["child_index_path"],
                "debug_path": binding["debug_path"],
                "material_slots": binding["material_slots"],
                "semantic_groups": binding["semantic_groups"],
                **material_parameters,
            }
            for binding in asset.bindings
            if material_change_requested
            and binding["material_slots"] > 0
            and not material_protected_groups.intersection(binding["semantic_groups"])
        ]

        motion = recipe["motion"]
        motion_actions = set(profile.allowed_actions["motion"])
        static_requested = motion.get("preference") == "static"
        animation_operations = [
            {
                "operation": "configure_animation_playback",
                **binding,
                "autoplay": motion["autoplay"] if "disable_autoplay" in motion_actions else True,
                "looping": motion["looping"] if "disable_looping" in motion_actions else False,
                "speed_multiplier": motion["speed_multiplier"] if "reduce_speed" in motion_actions else 1.0,
                "static_pose_strategy": (
                    "initial_authored_pose"
                    if static_requested and "pause_at_initial_authored_pose" in motion_actions
                    else "not_requested"
                ),
                "reviewed_static_frame_available": False,
            }
            for binding in asset.animation_bindings
        ]

        opacity_request = dict(recipe["opacity"])
        opacity_contract = {
            "strategy": "discrete_visibility_only_no_runtime_transparency",
            "requested_values": opacity_request,
            "opacity_operations": [],
            "reason": (
                "The current packages do not carry reviewed per-entity opacity variants. "
                "Exact semantic visibility operations are used where allowed; otherwise source opacity is preserved."
            ),
        }
        lod_contract = {
            "requested_bias": recipe["detail"]["lod_bias"],
            "runtime_lod_variant_available": False,
            "applied": False,
            "behavior": "preserve_source_geometry_and_profile_on_device",
        }
        presentation_ui_contract = {
            "owner": "visionOS_application",
            "annotations": dict(recipe["annotations"]),
            "pacing": dict(recipe["pacing"]),
            "comfort_controls": dict(recipe["comfort_controls"]),
            "authored_geometry_labels_automatically_hidden": False,
            "reason": (
                "Label priority, reading order, pacing, and controls are app-owned. "
                "Mapped source labels remain unchanged until a reviewed priority map exists."
            ),
        }

        unresolved_requested_changes = profile_blocked_matches > 0 or protected_matches > 0

        return {
            "schema_version": "1.0",
            "mapping_status": "exact_revision_bound",
            "selector_kind": "child_index_path",
            "source_package_sha256": asset.package_sha256,
            "root_contract": "Start at the Entity returned by Entity.load(contentsOf:) and traverse children by index.",
            "revision_mismatch_behavior": "Reject the plan, preserve the source, and show the documented fallback.",
            "semantic_group_coverage": {
                "present_groups": sorted(present_groups),
                "requested_hidden_groups_present": requested_hidden_groups_present,
                "requested_hidden_groups_not_present": requested_hidden_groups_not_present,
                "absent_group_behavior": "not_applicable_no_fallback",
            },
            "visibility_operations": visibility_operations,
            "protected_primary_matches_not_hidden": protected_matches,
            "profile_blocked_visibility_matches": profile_blocked_matches,
            "material_operations": material_operations,
            "material_contract": {
                "status": "display_blocked_developer_preview_only",
                "clinical_detail_behavior": "preserve_source_materials",
                "protected_semantic_groups": sorted(material_protected_groups),
                "protected_entity_count": material_protected_entities,
                "mapped_labels_and_primary_pathology_remain_unmodified": True,
                "source_legend_and_unmodified_asset_remain_available": True,
            },
            "animation_operations": animation_operations,
            "animation_contract": {
                "static_pose_strategy": (
                    "initial_authored_pose" if static_requested else "not_requested"
                ),
                "reviewed_representative_frame_available": False,
                "invented_animation_allowed": False,
            },
            "opacity_contract": opacity_contract,
            "lod_contract": lod_contract,
            "presentation_ui_contract": presentation_ui_contract,
            "profile_action_contract": {
                key: list(value) for key, value in profile.allowed_actions.items()
            },
            "content_warning_required": (
                profile.presentation_intensity in {"moderate", "high"}
                and recipe["adaptation_tier"] in {"overview", "simplified"}
            ),
            "progressive_disclosure_required": (
                "progressive_disclosure" in profile.allowed_actions["visibility"]
                and recipe["adaptation_tier"] in {"overview", "simplified"}
            ),
            "unresolved_requested_changes": unresolved_requested_changes,
            "fallback_if_unresolved": recipe["recommended_fallback"],
            "restore_contract": {
                "strategy": "restore_snapshotted_isEnabled_and_materials_then_reestablish_app_owned_playback_state",
                "snapshot_before_first_edit": True,
                "one_action_restore_required": True,
                "playback_restore_owner": "visionOS_application",
                "apply_before_authored_playback_starts": True,
            },
            "source_asset_unchanged": True,
            "source_medical_content_remains_available": True,
            "medical_content_preservation_status": "requires_external_clinical_and_human_factors_review",
            "patient_display_authorized": False,
            "operation_counts": {
                "visibility": len(visibility_operations),
                "materials": len(material_operations),
                "animations": len(animation_operations),
            },
        }
