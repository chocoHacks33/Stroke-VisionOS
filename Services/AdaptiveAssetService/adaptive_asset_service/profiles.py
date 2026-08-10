"""Catalog-wide, non-clinical visual-adaptation profile registry."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from .catalog import AssetCatalog, CatalogAsset, valid_asset_id


KNOWN_ACTIONS = {
    "visibility": {
        "hide_asset",
        "restore_source_visibility",
        "reduce_label_density",
        "progressive_disclosure",
        "hide_graphic_subcomponents_if_semantically_mapped",
        "replace_aggregate_with_components",
        "replace_components_with_aggregate",
        "replace_semantic_overlap",
        "use_review_gated_orientation_interstitial_candidate",
    },
    "material": {
        "apply_bounded_developer_preview_tint",
        "reduce_saturation_preserving_source_access",
        "increase_roughness",
        "reduce_specular",
        "reduce_emission",
        "restore_source_materials",
    },
    "motion": {
        "disable_autoplay",
        "pause_runtime_motion",
        "reduce_speed",
        "disable_looping",
        "pause_at_initial_authored_pose",
        "block_unreviewed_motion",
        "restore_authored_motion",
    },
}
PROFILE_FIELDS = {
    "asset_id",
    "title",
    "module",
    "source_manifest",
    "content_categories",
    "graphic_content_tags",
    "presentation_intensity",
    "allowed_actions",
    "replacement_rules",
    "clinical_safeguards",
}
REPLACEMENT_FIELDS = {
    "role",
    "replaces_asset_ids",
    "never_co_load_with_asset_ids",
    "candidate_replacement_asset_ids",
    "candidate_use",
    "approval_required",
    "source_must_remain_available",
    "restore_source_before_medical_detail",
}
SAFEGUARD_FIELDS = {
    "patient_display_authorized",
    "required_review_status",
    "patient_specific",
    "non_diagnostic",
    "anxiety_inference_allowed",
    "preserve_material_facts",
    "safeguard_tags",
}


class ProfileError(RuntimeError):
    """The adaptation profile set is missing, incomplete, or unsafe."""


@dataclass(frozen=True)
class AssetAdaptationProfile:
    asset_id: str
    module: str
    content_categories: tuple[str, ...]
    graphic_content_tags: tuple[str, ...]
    presentation_intensity: str
    allowed_actions: dict[str, tuple[str, ...]]
    replacement_rules: dict[str, Any]
    clinical_safeguards: dict[str, Any]

    def public_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "module": self.module,
            "content_categories": list(self.content_categories),
            "graphic_content_tags": list(self.graphic_content_tags),
            "presentation_intensity": self.presentation_intensity,
            "allowed_actions": {key: list(value) for key, value in self.allowed_actions.items()},
            "replacement_rules": dict(self.replacement_rules),
            "clinical_safeguards": dict(self.clinical_safeguards),
        }


class AdaptationProfileCatalog:
    """Validates exact profile coverage and exposes path-free profile data."""

    def __init__(self, path: Path, catalog: AssetCatalog):
        try:
            resolved = path.expanduser().resolve(strict=True)
            raw_bytes = resolved.read_bytes()
            document = json.loads(raw_bytes.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ProfileError(f"could not load catalog adaptation profiles: {exc}") from exc
        if not isinstance(document, dict) or document.get("schema_version") != "1.0.0":
            raise ProfileError("unsupported catalog adaptation-profile schema")
        if document.get("$schema") != "./catalog_adaptation_profiles.schema.json":
            raise ProfileError("catalog adaptation profiles have an invalid schema reference")
        self._validate_manifest_provenance(document.get("generated_from"), catalog)
        scope = document.get("scope")
        safe_false_fields = {
            "presentation_intensity_is_clinical_score",
            "anxiety_inference_supported",
            "biometric_inputs_supported",
            "patient_display_authorization_conferred",
            "profile_actions_mutate_source_usdz",
            "material_facts_may_be_removed",
        }
        if (
            not isinstance(scope, dict)
            or not isinstance(scope.get("purpose"), str)
            or not scope["purpose"]
            or any(scope.get(field) is not False for field in safe_false_fields)
        ):
            raise ProfileError("catalog adaptation-profile scope violates the non-diagnostic safety contract")
        vocabulary = document.get("action_vocabulary")
        if not isinstance(vocabulary, dict) or set(vocabulary) != {"visibility", "material", "motion"}:
            raise ProfileError("catalog adaptation profiles have an invalid action vocabulary")
        for kind, expected in KNOWN_ACTIONS.items():
            values = vocabulary.get(kind)
            if (
                not isinstance(values, dict)
                or set(values) != expected
                or any(not isinstance(description, str) or not description for description in values.values())
            ):
                raise ProfileError(f"catalog adaptation profiles have an invalid {kind} action vocabulary")

        profiles: dict[str, AssetAdaptationProfile] = {}
        raw_profiles = document.get("profiles")
        if not isinstance(raw_profiles, list):
            raise ProfileError("catalog adaptation profiles contain no profiles array")
        for raw_profile in raw_profiles:
            asset_id = raw_profile.get("asset_id") if isinstance(raw_profile, dict) else None
            asset = catalog.get(asset_id) if isinstance(asset_id, str) else None
            profile = self._parse(raw_profile, vocabulary, asset)
            if profile.asset_id in profiles:
                raise ProfileError(f"duplicate catalog adaptation profile: {profile.asset_id}")
            profiles[profile.asset_id] = profile

        catalog_ids = {asset["asset_id"] for asset in catalog.public_assets()}
        if set(profiles) != catalog_ids:
            missing = sorted(catalog_ids - set(profiles))
            extra = sorted(set(profiles) - catalog_ids)
            raise ProfileError(f"catalog adaptation-profile coverage mismatch; missing={missing}, extra={extra}")
        for profile in profiles.values():
            referenced = set(profile.replacement_rules["replaces_asset_ids"])
            referenced.update(profile.replacement_rules["never_co_load_with_asset_ids"])
            referenced.update(profile.replacement_rules["candidate_replacement_asset_ids"])
            unknown = sorted(referenced - catalog_ids)
            if unknown:
                raise ProfileError(f"profile {profile.asset_id} references unknown assets: {unknown}")
            never_co_load = set(profile.replacement_rules["never_co_load_with_asset_ids"])
            if not set(profile.replacement_rules["replaces_asset_ids"]).issubset(never_co_load):
                raise ProfileError(f"profile {profile.asset_id} replacement is missing a never-co-load safeguard")
            for related_id in never_co_load:
                related = profiles[related_id]
                if profile.asset_id not in related.replacement_rules["never_co_load_with_asset_ids"]:
                    raise ProfileError(
                        f"profile {profile.asset_id} has an asymmetric never-co-load relationship with {related_id}"
                    )
        self.path = resolved
        self.document_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        self._profiles = profiles

    @property
    def asset_count(self) -> int:
        return len(self._profiles)

    def get(self, asset_id: str) -> AssetAdaptationProfile | None:
        return self._profiles.get(asset_id)

    @staticmethod
    def _validate_manifest_provenance(value: Any, catalog: AssetCatalog) -> None:
        if not isinstance(value, dict):
            raise ProfileError("catalog adaptation profiles have no manifest provenance")
        manifest_count = value.get("manifest_count")
        released_count = value.get("released_asset_count")
        if (
            isinstance(manifest_count, bool)
            or not isinstance(manifest_count, int)
            or manifest_count != catalog.manifest_count
            or isinstance(released_count, bool)
            or not isinstance(released_count, int)
            or released_count != catalog.asset_count
        ):
            raise ProfileError("catalog adaptation-profile provenance counts are stale")
        declared_paths = value.get("manifest_paths")
        if (
            not isinstance(declared_paths, list)
            or len(declared_paths) != catalog.manifest_count
            or len(set(declared_paths)) != len(declared_paths)
            or any(not isinstance(path, str) or not path for path in declared_paths)
        ):
            raise ProfileError("catalog adaptation-profile manifest paths are invalid")

        actual_paths = sorted(catalog.root.rglob("asset_manifest*.json"))
        if len(actual_paths) != catalog.manifest_count:
            raise ProfileError("catalog adaptation-profile manifest coverage is stale")
        matched: list[tuple[str, Path]] = []
        for actual in actual_paths:
            relative_parts = actual.relative_to(catalog.root).parts
            candidates: list[str] = []
            for declared in declared_paths:
                parsed = PurePosixPath(declared)
                if parsed.is_absolute() or ".." in parsed.parts or "\\" in declared:
                    raise ProfileError("catalog adaptation-profile manifest path is unsafe")
                if tuple(parsed.parts[-len(relative_parts) :]) == relative_parts:
                    candidates.append(declared)
            if len(candidates) != 1:
                raise ProfileError("catalog adaptation-profile manifest paths do not match the catalog")
            matched.append((candidates[0], actual))
        if [declared for declared, _ in matched] != declared_paths:
            raise ProfileError("catalog adaptation-profile manifest path order is stale")

        digest = hashlib.sha256()
        for declared, actual in matched:
            try:
                raw_manifest = actual.read_bytes()
            except OSError as exc:
                raise ProfileError("catalog adaptation-profile manifest is unreadable") from exc
            digest.update(declared.encode("utf-8"))
            digest.update(b"\0")
            digest.update(raw_manifest)
            digest.update(b"\0")
        if value.get("manifest_set_sha256") != digest.hexdigest():
            raise ProfileError("catalog adaptation-profile manifest digest is stale")
        held_ids = value.get("held_asset_ids_excluded")
        if (
            not isinstance(held_ids, list)
            or len(set(held_ids)) != len(held_ids)
            or any(not valid_asset_id(asset_id) for asset_id in held_ids)
            or any(catalog.get(asset_id) is not None for asset_id in held_ids)
        ):
            raise ProfileError("catalog adaptation-profile held-asset exclusions are invalid")

    @staticmethod
    def _string_tuple(value: Any, field: str, asset_id: str) -> tuple[str, ...]:
        if not isinstance(value, list) or not value or any(not isinstance(item, str) or not item for item in value):
            raise ProfileError(f"profile {asset_id} has invalid {field}")
        if len(set(value)) != len(value):
            raise ProfileError(f"profile {asset_id} has duplicate {field}")
        return tuple(value)

    @staticmethod
    def _id_list(value: Any, field: str, asset_id: str) -> list[str]:
        if (
            not isinstance(value, list)
            or any(not valid_asset_id(item) for item in value)
            or len(set(value)) != len(value)
        ):
            raise ProfileError(f"profile {asset_id} has invalid {field}")
        return list(value)

    @classmethod
    def _parse(
        cls,
        raw: Any,
        vocabulary: dict[str, Any],
        catalog_asset: CatalogAsset | None,
    ) -> AssetAdaptationProfile:
        if (
            not isinstance(raw, dict)
            or set(raw) != PROFILE_FIELDS
            or not valid_asset_id(raw.get("asset_id"))
        ):
            raise ProfileError("catalog adaptation profiles contain an invalid profile")
        asset_id = raw["asset_id"]
        if catalog_asset is None:
            raise ProfileError(f"catalog adaptation profile references unknown asset: {asset_id}")
        if not isinstance(raw.get("title"), str) or not raw["title"]:
            raise ProfileError(f"profile {asset_id} has an invalid title")
        if not isinstance(raw.get("module"), str) or not raw["module"]:
            raise ProfileError(f"profile {asset_id} has an invalid module")
        source_manifest = raw.get("source_manifest")
        if not isinstance(source_manifest, str) or not source_manifest:
            raise ProfileError(f"profile {asset_id} has an invalid source manifest")
        parsed_manifest = PurePosixPath(source_manifest)
        if (
            parsed_manifest.is_absolute()
            or ".." in parsed_manifest.parts
            or "\\" in source_manifest
            or parsed_manifest.name != catalog_asset.manifest_name
        ):
            raise ProfileError(f"profile {asset_id} has a source-manifest mismatch")
        actions = raw.get("allowed_actions")
        if not isinstance(actions, dict) or set(actions) != {"visibility", "material", "motion"}:
            raise ProfileError(f"profile {asset_id} has invalid allowed actions")
        parsed_actions: dict[str, tuple[str, ...]] = {}
        for kind, values in actions.items():
            parsed = cls._string_tuple(values, f"allowed_actions.{kind}", asset_id)
            unknown = set(parsed) - KNOWN_ACTIONS[kind]
            if unknown:
                raise ProfileError(f"profile {asset_id} uses unknown {kind} actions: {sorted(unknown)}")
            parsed_actions[kind] = parsed
        rules = raw.get("replacement_rules")
        if not isinstance(rules, dict) or set(rules) != REPLACEMENT_FIELDS:
            raise ProfileError(f"profile {asset_id} has unsafe replacement rules")
        if rules.get("role") not in {"standalone", "component", "aggregate", "orientation_candidate"}:
            raise ProfileError(f"profile {asset_id} has an invalid replacement role")
        if rules.get("candidate_use") not in {
            "not_applicable",
            "orientation_interstitial_only_not_content_equivalent",
        }:
            raise ProfileError(f"profile {asset_id} has an invalid candidate use")
        if (
            rules.get("approval_required") is not True
            or rules.get("source_must_remain_available") is not True
            or rules.get("restore_source_before_medical_detail") is not True
        ):
            raise ProfileError(f"profile {asset_id} has unsafe replacement rules")
        parsed_rules = dict(rules)
        for field in (
            "replaces_asset_ids",
            "never_co_load_with_asset_ids",
            "candidate_replacement_asset_ids",
        ):
            parsed_rules[field] = cls._id_list(rules.get(field), f"replacement_rules.{field}", asset_id)
        candidates = parsed_rules["candidate_replacement_asset_ids"]
        if bool(candidates) != (
            rules["candidate_use"] == "orientation_interstitial_only_not_content_equivalent"
        ):
            raise ProfileError(f"profile {asset_id} has inconsistent candidate replacement rules")
        safeguards = raw.get("clinical_safeguards")
        if (
            not isinstance(safeguards, dict)
            or set(safeguards) != SAFEGUARD_FIELDS
            or safeguards.get("patient_display_authorized") is not False
            or safeguards.get("required_review_status") != catalog_asset.clinical_review_status
            or safeguards.get("patient_specific") is not False
            or safeguards.get("non_diagnostic") is not True
            or safeguards.get("anxiety_inference_allowed") is not False
            or safeguards.get("preserve_material_facts") is not True
        ):
            raise ProfileError(f"profile {asset_id} violates the clinical safeguard contract")
        cls._string_tuple(safeguards.get("safeguard_tags"), "clinical_safeguards.safeguard_tags", asset_id)
        intensity = raw.get("presentation_intensity")
        if intensity not in {"minimal", "low", "moderate", "high"}:
            raise ProfileError(f"profile {asset_id} has invalid presentation intensity")
        return AssetAdaptationProfile(
            asset_id=asset_id,
            module=str(raw.get("module", "unspecified")),
            content_categories=cls._string_tuple(raw.get("content_categories"), "content_categories", asset_id),
            graphic_content_tags=cls._string_tuple(raw.get("graphic_content_tags"), "graphic_content_tags", asset_id),
            presentation_intensity=intensity,
            allowed_actions=parsed_actions,
            replacement_rules=parsed_rules,
            clinical_safeguards=dict(safeguards),
        )
