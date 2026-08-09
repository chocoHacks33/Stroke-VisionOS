"""Strict loader and path-free responses for deterministic visual-detail variants."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from typing import Any

from .catalog import AssetCatalog, CatalogAsset, SHA256_PATTERN, valid_asset_id


DETAIL_TIERS = ("minimal", "reduced80", "full")
FROZEN_DETAIL_CATALOG_SHA256 = "78be2bddff068298b62da4b504fe1c4b898f052c30209e52c84cf446abc25822"
FROZEN_DETAIL_POLICY_SHA256 = "9097522cd240b2e929f05954482651e30e230e2c0fa8b85303c752e26f18248b"
NUMERIC_PARAMETER_KEYS = (
    "semantic_density_target",
    "texture_resolution_scale",
    "secondary_detail_visibility_ratio",
    "label_density_ratio",
    "saturation_multiplier",
    "specular_multiplier",
    "motion_speed_multiplier",
    "particle_or_flow_count_ratio",
)
PARAMETER_KEYS = frozenset(NUMERIC_PARAMETER_KEYS) | {"motion_mode", "particle_or_flow_mode"}
MOTION_MODES = {"static", "slowed", "source_authored"}
PARTICLE_OR_FLOW_MODES = {
    "none",
    "sparse_static_direction_markers",
    "reduced_direction_markers",
    "reduced_cells_and_flow",
    "representative_static_elements",
    "reduced_representative_elements",
    "source_authored",
}
CATALOG_KEYS = {
    "assets",
    "catalog_id",
    "category_count",
    "category_counts",
    "full_binding_contract",
    "lower_tier_contract",
    "module_id",
    "patient_display_authorized",
    "runtime_geometry_included",
    "schema_version",
    "source_geometry_mutation_allowed",
    "source_release_asset_count",
    "source_release_manifest_count",
    "tier_count",
    "tier_order",
    "variants",
    "virtual_variant_count",
}
POLICY_KEYS = {
    "assembly_domain_overrides",
    "categories",
    "category_count",
    "global_must_preserve",
    "global_prohibited",
    "module_id",
    "patient_display_authorized",
    "policy_id",
    "presentation_parameter_contract",
    "schema_version",
    "tier_order",
    "tier_semantics",
}
ASSET_KEYS = {
    "assembly_domain",
    "asset_id",
    "composition_kind",
    "parameter_policy_category",
    "primary_category",
    "source_asset_index",
    "source_manifest",
    "source_manifest_index",
    "source_usdz",
    "source_usdz_bytes",
    "source_usdz_sha256",
    "variant_ids",
}
VARIANT_BASE_KEYS = {
    "asset_id",
    "binds_exact_observed_source_as_presentation",
    "category_id",
    "category_policy_ref",
    "geometry_mutation_allowed",
    "parameter_policy_category",
    "patient_display_authorized",
    "presentation_parameters",
    "preserve_medical_facts_and_warnings",
    "preserve_silhouette_or_meaning",
    "source_asset_unchanged",
    "source_usdz",
    "source_usdz_bytes",
    "source_usdz_sha256",
    "tier",
    "variant_id",
    "virtual_reversible_sidecar",
}
ASSEMBLY_RESOLUTION_KEYS = {
    "action",
    "assembly_control_parameters",
    "assembly_domain",
    "leaf_parameter_resolution",
}


class DetailVariantError(RuntimeError):
    """The configured detail-variant documents are missing, stale, or unsafe."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DetailVariantError(message)


def _load_document(path: Path, label: str) -> tuple[dict[str, Any], str]:
    try:
        resolved = path.expanduser().resolve(strict=True)
        raw = resolved.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DetailVariantError(f"could not load {label}: {exc}") from exc
    _require(isinstance(document, dict), f"{label} must be a JSON object")
    return document, hashlib.sha256(raw).hexdigest()


def _exact_keys(value: Any, expected: set[str] | frozenset[str], label: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{label} must be an object")
    observed = set(value)
    _require(observed == set(expected), f"{label} fields mismatch")
    return value


def _string(value: Any, label: str) -> str:
    _require(isinstance(value, str) and bool(value), f"{label} must be a non-empty string")
    return value


def _nonnegative_int(value: Any, label: str) -> int:
    _require(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0,
        f"{label} must be a nonnegative integer",
    )
    return value


def _string_list(value: Any, label: str, *, exact: tuple[str, ...] | None = None) -> list[str]:
    _require(
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value)
        and len(set(value)) == len(value),
        f"{label} must be a non-empty unique string list",
    )
    if exact is not None:
        _require(tuple(value) == exact, f"{label} order or values mismatch")
    return value


def _validate_parameters(value: Any, label: str) -> dict[str, Any]:
    parameters = _exact_keys(value, PARAMETER_KEYS, label)
    for key in NUMERIC_PARAMETER_KEYS:
        number = parameters[key]
        _require(
            isinstance(number, (int, float))
            and not isinstance(number, bool)
            and math.isfinite(number)
            and 0.0 <= number <= 1.0,
            f"{label}.{key} must be finite and inside 0...1",
        )
    _require(parameters["motion_mode"] in MOTION_MODES, f"{label} has an invalid motion mode")
    _require(
        parameters["particle_or_flow_mode"] in PARTICLE_OR_FLOW_MODES,
        f"{label} has an invalid particle or flow mode",
    )
    speed = parameters["motion_speed_multiplier"]
    if parameters["motion_mode"] == "static":
        _require(speed == 0.0, f"{label} static motion must have zero speed")
    elif parameters["motion_mode"] == "slowed":
        _require(0.0 < speed < 1.0, f"{label} slowed motion speed must be between zero and one")
    else:
        _require(speed == 1.0, f"{label} source-authored motion speed must equal one")
    count = parameters["particle_or_flow_count_ratio"]
    if parameters["particle_or_flow_mode"] == "none":
        _require(count == 0.0, f"{label} none particle mode must have zero count")
    elif parameters["particle_or_flow_mode"] == "source_authored":
        _require(count == 1.0, f"{label} source-authored particle count must equal one")
    else:
        _require(0.0 < count < 1.0, f"{label} reduced particle count must be between zero and one")
    return parameters


class DetailVariantCatalog:
    """Validates the frozen variant catalog against policy and source packages."""

    def __init__(
        self,
        catalog_path: Path,
        policy_path: Path,
        source_catalog: AssetCatalog,
        *,
        expected_catalog_sha256: str | None = FROZEN_DETAIL_CATALOG_SHA256,
        expected_policy_sha256: str | None = FROZEN_DETAIL_POLICY_SHA256,
    ):
        document, self.document_sha256 = _load_document(catalog_path, "detail-variant catalog")
        policy, self.policy_sha256 = _load_document(policy_path, "detail category policy")
        if expected_catalog_sha256 is not None:
            _require(
                self.document_sha256 == expected_catalog_sha256,
                "detail-variant catalog revision is not the authorized frozen revision",
            )
        if expected_policy_sha256 is not None:
            _require(
                self.policy_sha256 == expected_policy_sha256,
                "detail category policy revision is not the authorized frozen revision",
            )
        _exact_keys(document, CATALOG_KEYS, "detail-variant catalog")
        _exact_keys(policy, POLICY_KEYS, "detail category policy")

        policy_by_category = self._validate_policy(policy)
        assets, variants = self._validate_catalog(
            document,
            policy,
            policy_by_category,
            source_catalog,
        )
        self._document = document
        self._policy = policy
        self._source_catalog = source_catalog
        self._assets = assets
        self._variants = variants
        self._validated_sources = {
            asset_id: source_catalog.get(asset_id) for asset_id in assets
        }
        _require(
            all(source is not None for source in self._validated_sources.values()),
            "detail source catalog changed during validation",
        )

    @property
    def asset_count(self) -> int:
        return len(self._assets)

    @property
    def variant_count(self) -> int:
        return sum(len(variants) for variants in self._variants.values())

    @property
    def catalog_revision(self) -> dict[str, str]:
        return {
            "catalog_id": self._document["catalog_id"],
            "schema_version": self._document["schema_version"],
            "sha256": self.document_sha256,
        }

    @property
    def policy_revision(self) -> dict[str, str]:
        return {
            "policy_id": self._policy["policy_id"],
            "schema_version": self._policy["schema_version"],
            "sha256": self.policy_sha256,
        }

    @property
    def application_contract(self) -> dict[str, Any]:
        return {
            "runtime_scope": "developer_preview_only",
            "developer_preview_authorized": True,
            "developer_runtime_application_authorized": False,
            "renderer_mapping_status": "pending_exact_renderer_mapping",
            "requires_exact_renderer_mapping": True,
            "source_asset_unchanged": True,
            "patient_display_authorized": False,
            "patient_display_review_required": True,
        }

    @staticmethod
    def _validate_policy(policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
        _require(policy["schema_version"] == "1.0.0", "unsupported detail category policy schema")
        _require(policy["module_id"] == "visual_detail_variants_v1", "detail policy module mismatch")
        _require(policy["policy_id"] == "visual_detail_category_policy_v1", "detail policy ID mismatch")
        _require(policy["patient_display_authorized"] is False, "detail policy enabled patient display")
        _string_list(policy["tier_order"], "detail policy tiers", exact=DETAIL_TIERS)
        _string_list(policy["global_must_preserve"], "global preservation rules")
        _string_list(policy["global_prohibited"], "global prohibited rules")

        overrides = policy["assembly_domain_overrides"]
        _require(
            isinstance(overrides, dict)
            and all(valid_asset_id(key) and isinstance(value, str) and value for key, value in overrides.items()),
            "assembly-domain overrides are invalid",
        )
        contract = policy["presentation_parameter_contract"]
        _exact_keys(
            contract,
            {
                "motion_modes",
                "numeric_monotonic_order",
                "numeric_range",
                "particle_or_flow_modes",
                "reduced80_semantic_density_target",
                "units",
            },
            "presentation parameter contract",
        )
        _require(contract.get("numeric_range") == [0.0, 1.0], "presentation numeric range changed")
        _require(
            contract.get("numeric_monotonic_order") == "minimal <= reduced80 <= full",
            "presentation monotonic contract changed",
        )
        _require(
            contract.get("reduced80_semantic_density_target") == 0.8,
            "reduced80 semantic-density contract changed",
        )
        _require(set(contract.get("motion_modes", [])) == MOTION_MODES, "motion-mode contract changed")
        _require(
            set(contract.get("particle_or_flow_modes", [])) == PARTICLE_OR_FLOW_MODES,
            "particle or flow mode contract changed",
        )
        units = _exact_keys(
            contract["units"],
            {
                "motion_speed_multiplier",
                "particle_or_flow_count_ratio",
                "semantic_density_target",
            },
            "presentation parameter units",
        )
        _require(
            units
            == {
                "motion_speed_multiplier": "ratio_of_source_authored_speed",
                "particle_or_flow_count_ratio": "ratio_of_source_authored_count_or_reviewed_equivalent",
                "semantic_density_target": "ratio_of_approved_explanatory_information_not_polygon_count",
            },
            "presentation parameter units changed",
        )
        semantics = policy["tier_semantics"]
        _require(isinstance(semantics, dict) and set(semantics) == set(DETAIL_TIERS), "tier semantics mismatch")
        _exact_keys(semantics["minimal"], {"semantic_density"}, "minimal tier semantics")
        _exact_keys(
            semantics["reduced80"],
            {"meaning", "semantic_density_target"},
            "reduced80 tier semantics",
        )
        _exact_keys(semantics["full"], {"source_asset_unchanged"}, "full tier semantics")
        _require(semantics["full"].get("source_asset_unchanged") is True, "full tier mutates source")
        _require(
            semantics["minimal"].get("semantic_density") == "smallest_reviewed_complete_explanation",
            "minimal semantic contract changed",
        )
        _require(
            semantics["reduced80"].get("semantic_density_target") == 0.8,
            "reduced80 semantic contract changed",
        )
        _string(semantics["reduced80"]["meaning"], "reduced80 semantic meaning")

        categories = policy["categories"]
        _require(isinstance(categories, list) and bool(categories), "detail policy has no categories")
        _require(
            _nonnegative_int(policy["category_count"], "policy category count") == len(categories),
            "detail policy category count mismatch",
        )
        parsed: dict[str, dict[str, Any]] = {}
        observed_asset_count = 0
        for entry in categories:
            _exact_keys(entry, {"asset_count", "category_id", "must_preserve", "tiers"}, "category policy")
            category_id = _string(entry["category_id"], "category ID")
            _require(category_id not in parsed, f"duplicate category policy: {category_id}")
            asset_count = _nonnegative_int(entry["asset_count"], f"{category_id} asset count")
            _require(asset_count > 0, f"{category_id} has no assets")
            observed_asset_count += asset_count
            _string_list(entry["must_preserve"], f"{category_id} preservation rules")
            tiers = entry["tiers"]
            _require(isinstance(tiers, dict) and set(tiers) == set(DETAIL_TIERS), f"{category_id} tier coverage mismatch")
            for tier in DETAIL_TIERS:
                block = tiers[tier]
                common = {"geometry_mutation_allowed", "presentation_parameters", "strategy"}
                tier_specific = {
                    "minimal": {"semantic_density", "virtual_reversible_sidecar"},
                    "reduced80": {"semantic_density_target", "virtual_reversible_sidecar"},
                    "full": {"source_asset_unchanged"},
                }[tier]
                _exact_keys(block, common | tier_specific, f"{category_id}/{tier} policy")
                _require(block["geometry_mutation_allowed"] is False, f"{category_id}/{tier} permits geometry mutation")
                _string_list(block["strategy"], f"{category_id}/{tier} strategy")
                _validate_parameters(block["presentation_parameters"], f"{category_id}/{tier} parameters")
                if tier == "minimal":
                    _require(
                        block["semantic_density"] == "smallest_reviewed_complete_explanation"
                        and block["virtual_reversible_sidecar"] is True,
                        f"{category_id} minimal contract mismatch",
                    )
                elif tier == "reduced80":
                    _require(
                        block["semantic_density_target"] == 0.8
                        and block["virtual_reversible_sidecar"] is True,
                        f"{category_id} reduced80 contract mismatch",
                    )
                else:
                    _require(block["source_asset_unchanged"] is True, f"{category_id} full tier mutates source")
            for key in NUMERIC_PARAMETER_KEYS:
                values = [tiers[tier]["presentation_parameters"][key] for tier in DETAIL_TIERS]
                _require(values[0] <= values[1] <= values[2], f"{category_id} has non-monotonic {key}")
            full_parameters = tiers["full"]["presentation_parameters"]
            _require(
                all(full_parameters[key] == 1.0 for key in NUMERIC_PARAMETER_KEYS)
                and full_parameters["motion_mode"] == "source_authored"
                and full_parameters["particle_or_flow_mode"] == "source_authored",
                f"{category_id} full parameters do not preserve the source",
            )
            parsed[category_id] = entry
        _require(observed_asset_count > 0, "detail policy covers no assets")
        return parsed

    @staticmethod
    def _resolve_source_path(source_root: Path, value: Any, label: str, suffix: str) -> Path:
        raw = _string(value, label)
        _require("\\" not in raw, f"{label} contains a platform path separator")
        relative = PurePosixPath(raw)
        _require(not relative.is_absolute() and ".." not in relative.parts, f"{label} is not a safe relative path")
        prefix = ("RealityKitContent", "Assets")
        _require(relative.parts[:2] == prefix and len(relative.parts) > 2, f"{label} is outside the asset catalog")
        _require(relative.suffix.lower() == suffix, f"{label} has the wrong file type")
        try:
            resolved = (source_root / Path(*relative.parts[2:])).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise DetailVariantError(f"{label} is unreadable") from exc
        _require(resolved.is_relative_to(source_root) and resolved.is_file(), f"{label} escaped the asset catalog")
        return resolved

    @classmethod
    def _validate_catalog(
        cls,
        document: dict[str, Any],
        policy: dict[str, Any],
        policy_by_category: dict[str, dict[str, Any]],
        source_catalog: AssetCatalog,
    ) -> tuple[dict[str, dict[str, Any]], dict[str, tuple[dict[str, Any], ...]]]:
        _require(document["schema_version"] == "1.0.0", "unsupported detail-variant schema")
        _require(document["module_id"] == "visual_detail_variants_v1", "detail-variant module mismatch")
        _require(document["catalog_id"] == "visual_detail_variant_catalog_v1", "detail-variant catalog ID mismatch")
        _require(document["patient_display_authorized"] is False, "detail variants enabled patient display")
        _require(document["runtime_geometry_included"] is False, "detail catalog unexpectedly includes geometry")
        _require(document["source_geometry_mutation_allowed"] is False, "detail catalog permits source mutation")
        _string_list(document["tier_order"], "detail catalog tiers", exact=DETAIL_TIERS)
        _require(document["tier_count"] == len(DETAIL_TIERS), "detail catalog tier count mismatch")
        _require(
            document["source_release_asset_count"] == source_catalog.asset_count,
            "detail catalog asset count is stale",
        )
        _require(
            document["source_release_manifest_count"] == source_catalog.manifest_count,
            "detail catalog manifest count is stale",
        )
        _require(
            document["category_count"] == policy["category_count"],
            "detail catalog and policy category counts differ",
        )
        _string(document["full_binding_contract"], "full binding contract")
        _string(document["lower_tier_contract"], "lower-tier contract")

        raw_assets = document["assets"]
        raw_variants = document["variants"]
        _require(isinstance(raw_assets, list), "detail catalog assets must be an array")
        _require(isinstance(raw_variants, list), "detail catalog variants must be an array")
        _require(len(raw_assets) == source_catalog.asset_count, "detail catalog asset array is incomplete")
        _require(
            document["virtual_variant_count"] == len(raw_variants) == source_catalog.asset_count * 3,
            "detail catalog variant count mismatch",
        )

        assets: dict[str, dict[str, Any]] = {}
        category_counts: Counter[str] = Counter()
        indices_by_manifest: defaultdict[int, list[int]] = defaultdict(list)
        for record in raw_assets:
            _exact_keys(record, ASSET_KEYS, "detail catalog asset")
            asset_id = record["asset_id"]
            _require(valid_asset_id(asset_id) and asset_id not in assets, "invalid or duplicate detail asset ID")
            source = source_catalog.get(asset_id)
            _require(source is not None, f"detail catalog references unknown asset: {asset_id}")
            cls._validate_source_binding(record, source, source_catalog, asset_id)
            primary = _string(record["primary_category"], f"{asset_id} primary category")
            parameter_category = _string(
                record["parameter_policy_category"], f"{asset_id} parameter category"
            )
            _require(primary in policy_by_category, f"{asset_id} has unknown primary category")
            _require(parameter_category in policy_by_category, f"{asset_id} has unknown parameter category")
            kind = record["composition_kind"]
            _require(kind in {"component", "assembly"}, f"{asset_id} has invalid composition kind")
            assembly_domain = record["assembly_domain"]
            if kind == "assembly":
                _require(primary == "COMPOSITE_ASSEMBLY", f"{asset_id} assembly is not in the assembly category")
                _require(
                    isinstance(assembly_domain, str)
                    and assembly_domain
                    and policy["assembly_domain_overrides"].get(asset_id) == assembly_domain,
                    f"{asset_id} assembly-domain override mismatch",
                )
                expected_parameter = (
                    assembly_domain if assembly_domain in policy_by_category else primary
                )
                _require(parameter_category == expected_parameter, f"{asset_id} parameter category mismatch")
            else:
                _require(assembly_domain is None, f"{asset_id} component has an assembly domain")
                _require(asset_id not in policy["assembly_domain_overrides"], f"{asset_id} component has an override")
                _require(parameter_category == primary, f"{asset_id} component parameter category mismatch")
            expected_variants = [f"{asset_id}::{tier}" for tier in DETAIL_TIERS]
            _require(record["variant_ids"] == expected_variants, f"{asset_id} variant IDs mismatch")
            manifest_index = _nonnegative_int(record["source_manifest_index"], f"{asset_id} manifest index")
            source_index = _nonnegative_int(record["source_asset_index"], f"{asset_id} source index")
            indices_by_manifest[manifest_index].append(source_index)
            category_counts[primary] += 1
            assets[asset_id] = record
        _require(set(assets) == source_catalog.asset_ids, "detail catalog coverage differs from source catalog")
        for indices in indices_by_manifest.values():
            _require(sorted(indices) == list(range(len(indices))), "source asset indices are not contiguous")
        _require(
            document["category_counts"] == dict(sorted(category_counts.items())),
            "detail catalog category counts mismatch",
        )
        _require(
            {key: entry["asset_count"] for key, entry in policy_by_category.items()}
            == document["category_counts"],
            "detail policy asset counts differ from catalog categories",
        )

        variants_by_asset: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        seen_variant_ids: set[str] = set()
        for variant in raw_variants:
            _require(isinstance(variant, dict), "detail variant must be an object")
            tier = variant.get("tier")
            optional = {
                "minimal": {"semantic_density"},
                "reduced80": {"semantic_density_target"},
                "full": set(),
            }.get(tier)
            _require(optional is not None, "detail variant has an unknown tier")
            asset_id = variant.get("asset_id")
            _require(asset_id in assets, "detail variant references an unknown asset")
            if assets[asset_id]["composition_kind"] == "assembly":
                optional = set(optional) | {"assembly_resolution"}
            _exact_keys(variant, VARIANT_BASE_KEYS | set(optional), f"detail variant {asset_id}/{tier}")
            variant_id = variant["variant_id"]
            _require(
                variant_id == f"{asset_id}::{tier}" and variant_id not in seen_variant_ids,
                "detail variant ID is invalid or duplicated",
            )
            seen_variant_ids.add(variant_id)
            asset_record = assets[asset_id]
            source = source_catalog.get(asset_id)
            assert source is not None
            _require(
                variant["source_usdz"] == asset_record["source_usdz"]
                and variant["source_usdz_bytes"] == source.package_bytes
                and variant["source_usdz_sha256"] == source.package_sha256,
                f"detail variant source revision mismatch: {variant_id}",
            )
            _require(
                variant["category_id"] == asset_record["primary_category"]
                and variant["parameter_policy_category"] == asset_record["parameter_policy_category"]
                and variant["category_policy_ref"]
                == f"visual_detail_category_policy_v1#{asset_record['primary_category']}",
                f"detail variant category mismatch: {variant_id}",
            )
            expected_parameters = policy_by_category[asset_record["parameter_policy_category"]][
                "tiers"
            ][tier]["presentation_parameters"]
            _validate_parameters(variant["presentation_parameters"], f"{variant_id} parameters")
            _require(variant["presentation_parameters"] == expected_parameters, f"{variant_id} recipe differs from policy")
            _require(
                variant["patient_display_authorized"] is False
                and variant["geometry_mutation_allowed"] is False
                and variant["source_asset_unchanged"] is True
                and variant["preserve_silhouette_or_meaning"] is True
                and variant["preserve_medical_facts_and_warnings"] is True,
                f"detail variant safety contract mismatch: {variant_id}",
            )
            if tier == "full":
                _require(
                    variant["binds_exact_observed_source_as_presentation"] is True
                    and variant["virtual_reversible_sidecar"] is False,
                    f"full binding contract mismatch: {variant_id}",
                )
            elif tier == "reduced80":
                _require(
                    variant["binds_exact_observed_source_as_presentation"] is False
                    and variant["virtual_reversible_sidecar"] is True
                    and variant["semantic_density_target"] == 0.8,
                    f"reduced80 contract mismatch: {variant_id}",
                )
            else:
                _require(
                    variant["binds_exact_observed_source_as_presentation"] is False
                    and variant["virtual_reversible_sidecar"] is True
                    and variant["semantic_density"] == "smallest_reviewed_complete_explanation",
                    f"minimal contract mismatch: {variant_id}",
                )
            if asset_record["composition_kind"] == "assembly":
                cls._validate_assembly_resolution(
                    variant["assembly_resolution"],
                    tier,
                    asset_record,
                    policy_by_category,
                    variant_id,
                )
            variants_by_asset[asset_id].append(variant)
        _require(len(seen_variant_ids) == source_catalog.asset_count * 3, "detail variant IDs are incomplete")
        for asset_id, variants in variants_by_asset.items():
            _require(
                [variant["tier"] for variant in variants] == list(DETAIL_TIERS),
                f"detail tiers are missing or out of order for {asset_id}",
            )
        _require(
            Counter(variant["tier"] for variant in raw_variants)
            == Counter({tier: source_catalog.asset_count for tier in DETAIL_TIERS}),
            "detail tier totals mismatch",
        )
        return assets, {asset_id: tuple(variants) for asset_id, variants in variants_by_asset.items()}

    @classmethod
    def _validate_source_binding(
        cls,
        record: dict[str, Any],
        source: CatalogAsset,
        source_catalog: AssetCatalog,
        asset_id: str,
    ) -> None:
        source_path = cls._resolve_source_path(
            source_catalog.root,
            record["source_usdz"],
            f"{asset_id} source USDZ",
            ".usdz",
        )
        _require(source_path == source.package_path, f"{asset_id} source USDZ path differs from its manifest")
        manifest_path = cls._resolve_source_path(
            source_catalog.root,
            record["source_manifest"],
            f"{asset_id} source manifest",
            ".json",
        )
        _require(manifest_path == source.manifest_path, f"{asset_id} source manifest mismatch")
        _require(
            record["source_usdz_bytes"] == source.package_bytes,
            f"{asset_id} source byte count is stale",
        )
        sha256 = record["source_usdz_sha256"]
        _require(
            isinstance(sha256, str)
            and SHA256_PATTERN.fullmatch(sha256) is not None
            and sha256 == source.package_sha256,
            f"{asset_id} source SHA-256 is stale",
        )

    @staticmethod
    def _validate_assembly_resolution(
        value: Any,
        tier: str,
        asset: dict[str, Any],
        policy_by_category: dict[str, dict[str, Any]],
        variant_id: str,
    ) -> None:
        resolution = _exact_keys(value, ASSEMBLY_RESOLUTION_KEYS, f"{variant_id} assembly resolution")
        _require(
            resolution["assembly_domain"] == asset["assembly_domain"],
            f"{variant_id} assembly domain mismatch",
        )
        expected_action = "bind_exact_source_assembly" if tier == "full" else "unload_assembly_then_select_leaf_components"
        _require(resolution["action"] == expected_action, f"{variant_id} assembly action mismatch")
        expected_leaf = (
            "per_leaf_primary_category"
            if asset["assembly_domain"] == "MIXED_REGISTERED_HEAD"
            else "fixed_assembly_domain_category"
        )
        _require(
            resolution["leaf_parameter_resolution"] == expected_leaf,
            f"{variant_id} assembly leaf resolution mismatch",
        )
        controls = resolution["assembly_control_parameters"]
        _validate_parameters(controls, f"{variant_id} assembly controls")
        expected_controls = policy_by_category["COMPOSITE_ASSEMBLY"]["tiers"][tier][
            "presentation_parameters"
        ]
        _require(controls == expected_controls, f"{variant_id} assembly controls differ from policy")

    def has_asset(self, asset_id: str) -> bool:
        return asset_id in self._assets

    def source_revision(self, asset_id: str) -> dict[str, Any] | None:
        source = self._validated_sources.get(asset_id)
        if source is None or asset_id not in self._assets:
            return None
        return {
            "asset_id": source.asset_id,
            "package_name": source.package_name,
            "package_bytes": source.package_bytes,
            "package_sha256": source.package_sha256,
            "package_integrity": source.package_integrity,
        }

    def matches_validated_source(self, source: CatalogAsset) -> bool:
        """Return whether a mutable catalog still names the exact validated source binding."""
        validated = self._validated_sources.get(source.asset_id)
        return bool(
            validated is not None
            and validated.manifest_path == source.manifest_path
            and validated.package_path == source.package_path
            and validated.package_bytes == source.package_bytes
            and validated.package_sha256 == source.package_sha256
        )

    def variants_for(self, asset_id: str) -> list[dict[str, Any]] | None:
        variants = self._variants.get(asset_id)
        if variants is None:
            return None
        return [self._public_variant(variant) for variant in variants]

    def select(self, asset_id: str, tier: str) -> dict[str, Any] | None:
        variants = self._variants.get(asset_id)
        if variants is None:
            return None
        for variant in variants:
            if variant["tier"] == tier:
                return self._public_variant(variant)
        return None

    def _public_variant(self, variant: dict[str, Any]) -> dict[str, Any]:
        asset_id = variant["asset_id"]
        source_revision = self.source_revision(asset_id)
        assert source_revision is not None
        parameter_category = variant["parameter_policy_category"]
        tier = variant["tier"]
        policy_block = next(
            entry for entry in self._policy["categories"] if entry["category_id"] == parameter_category
        )["tiers"][tier]
        primary_policy = next(
            entry for entry in self._policy["categories"] if entry["category_id"] == variant["category_id"]
        )
        parameter_policy = next(
            entry for entry in self._policy["categories"] if entry["category_id"] == parameter_category
        )
        recipe: dict[str, Any] = {
            "schema_version": "1.0",
            "catalog_id": self._document["catalog_id"],
            "catalog_revision_sha256": self.document_sha256,
            "category_policy_id": self._policy["policy_id"],
            "category_policy_revision_sha256": self.policy_sha256,
            "asset_id": asset_id,
            "variant_id": variant["variant_id"],
            "detail_tier": tier,
            "category_id": variant["category_id"],
            "parameter_policy_category": parameter_category,
            "presentation_parameters": deepcopy(policy_block["presentation_parameters"]),
            "strategy": deepcopy(policy_block["strategy"]),
            "source_asset_revision": deepcopy(source_revision),
            "geometry_mutation_allowed": False,
            "source_asset_unchanged": True,
            "preserve_silhouette_or_meaning": True,
            "preserve_medical_facts_and_warnings": True,
            "global_must_preserve": deepcopy(self._policy["global_must_preserve"]),
            "primary_category_must_preserve": deepcopy(primary_policy["must_preserve"]),
            "parameter_category_must_preserve": deepcopy(parameter_policy["must_preserve"]),
            "prohibited": deepcopy(self._policy["global_prohibited"]),
            "patient_display_authorized": False,
        }
        if "semantic_density" in variant:
            recipe["semantic_density"] = variant["semantic_density"]
        if "semantic_density_target" in variant:
            recipe["semantic_density_target"] = variant["semantic_density_target"]
        if "assembly_resolution" in variant:
            recipe["assembly_resolution"] = deepcopy(variant["assembly_resolution"])
        return {
            "variant_id": variant["variant_id"],
            "detail_tier": tier,
            "virtual_reversible_sidecar": variant["virtual_reversible_sidecar"],
            "binds_exact_observed_source_as_presentation": variant[
                "binds_exact_observed_source_as_presentation"
            ],
            "source_asset_revision": deepcopy(source_revision),
            "recipe": recipe,
        }
