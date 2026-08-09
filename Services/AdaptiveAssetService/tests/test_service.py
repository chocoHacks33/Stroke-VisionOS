from __future__ import annotations

from io import StringIO
from http.client import HTTPConnection
import hashlib
import json
import logging
from pathlib import Path
import socket
import stat
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from adaptive_asset_service.catalog import AssetCatalog, CatalogError
from adaptive_asset_service.detail_variants import (
    DETAIL_TIERS,
    FROZEN_DETAIL_CATALOG_SHA256,
    FROZEN_DETAIL_POLICY_SHA256,
    DetailVariantCatalog,
    DetailVariantError,
)
from adaptive_asset_service.procedural import ArtifactStore
from adaptive_asset_service.server import LOGGER, build_server


def write_manifest(root: Path, assets: list[dict[str, object]]) -> None:
    records: list[dict[str, object]] = []
    for source in assets:
        record = dict(source)
        asset_id = str(record.get("id", "invalid"))
        package = str(record.get("usdz", f"usdz/{asset_id}.usdz"))
        record["usdz"] = package
        package_path = root / package
        package_path.parent.mkdir(parents=True, exist_ok=True)
        payload = f"synthetic-usdz:{asset_id}".encode("utf-8")
        package_path.write_bytes(payload)
        record["usdz_bytes"] = len(payload)
        record["usdz_sha256"] = hashlib.sha256(payload).hexdigest()
        records.append(record)
    path = root / "asset_manifest_test.json"
    path.write_text(
        json.dumps(
            {
                "kit": "test-kit",
                "module": "test-module",
                "clinical_review_status": "review_required",
                "assets": records,
            }
        ),
        encoding="utf-8",
    )


def write_detail_documents(root: Path, catalog_root: Path) -> tuple[Path, Path, str, str]:
    manifest_path = catalog_root / "asset_manifest_test.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest["assets"]
    minimal = {
        "semantic_density_target": 0.3,
        "texture_resolution_scale": 0.4,
        "secondary_detail_visibility_ratio": 0.2,
        "label_density_ratio": 0.2,
        "saturation_multiplier": 0.7,
        "specular_multiplier": 0.4,
        "motion_speed_multiplier": 0.0,
        "particle_or_flow_count_ratio": 0.0,
        "motion_mode": "static",
        "particle_or_flow_mode": "none",
    }
    reduced = {
        "semantic_density_target": 0.8,
        "texture_resolution_scale": 0.8,
        "secondary_detail_visibility_ratio": 0.7,
        "label_density_ratio": 0.7,
        "saturation_multiplier": 0.9,
        "specular_multiplier": 0.8,
        "motion_speed_multiplier": 0.6,
        "particle_or_flow_count_ratio": 0.5,
        "motion_mode": "slowed",
        "particle_or_flow_mode": "reduced_direction_markers",
    }
    full = {
        "semantic_density_target": 1.0,
        "texture_resolution_scale": 1.0,
        "secondary_detail_visibility_ratio": 1.0,
        "label_density_ratio": 1.0,
        "saturation_multiplier": 1.0,
        "specular_multiplier": 1.0,
        "motion_speed_multiplier": 1.0,
        "particle_or_flow_count_ratio": 1.0,
        "motion_mode": "source_authored",
        "particle_or_flow_mode": "source_authored",
    }
    policy = {
        "assembly_domain_overrides": {},
        "categories": [
            {
                "asset_count": len(records),
                "category_id": "TEST_CATEGORY",
                "must_preserve": ["synthetic meaning"],
                "tiers": {
                    "minimal": {
                        "geometry_mutation_allowed": False,
                        "presentation_parameters": minimal,
                        "semantic_density": "smallest_reviewed_complete_explanation",
                        "strategy": ["show reviewed essentials"],
                        "virtual_reversible_sidecar": True,
                    },
                    "reduced80": {
                        "geometry_mutation_allowed": False,
                        "presentation_parameters": reduced,
                        "semantic_density_target": 0.8,
                        "strategy": ["show approximately eighty percent"],
                        "virtual_reversible_sidecar": True,
                    },
                    "full": {
                        "geometry_mutation_allowed": False,
                        "presentation_parameters": full,
                        "source_asset_unchanged": True,
                        "strategy": ["bind exact source"],
                    },
                },
            }
        ],
        "category_count": 1,
        "global_must_preserve": ["medical meaning"],
        "global_prohibited": ["biometric inference"],
        "module_id": "visual_detail_variants_v1",
        "patient_display_authorized": False,
        "policy_id": "visual_detail_category_policy_v1",
        "presentation_parameter_contract": {
            "motion_modes": ["static", "slowed", "source_authored"],
            "numeric_monotonic_order": "minimal <= reduced80 <= full",
            "numeric_range": [0.0, 1.0],
            "particle_or_flow_modes": [
                "none",
                "sparse_static_direction_markers",
                "reduced_direction_markers",
                "reduced_cells_and_flow",
                "representative_static_elements",
                "reduced_representative_elements",
                "source_authored",
            ],
            "reduced80_semantic_density_target": 0.8,
            "units": {
                "motion_speed_multiplier": "ratio_of_source_authored_speed",
                "particle_or_flow_count_ratio": "ratio_of_source_authored_count_or_reviewed_equivalent",
                "semantic_density_target": "ratio_of_approved_explanatory_information_not_polygon_count",
            },
        },
        "schema_version": "1.0.0",
        "tier_order": ["minimal", "reduced80", "full"],
        "tier_semantics": {
            "minimal": {"semantic_density": "smallest_reviewed_complete_explanation"},
            "reduced80": {
                "meaning": "Retain approximately 80% of approved semantic information.",
                "semantic_density_target": 0.8,
            },
            "full": {"source_asset_unchanged": True},
        },
    }
    assets = []
    variants = []
    for index, record in enumerate(records):
        asset_id = record["id"]
        source_usdz = f"RealityKitContent/Assets/{record['usdz']}"
        source = {
            "source_usdz": source_usdz,
            "source_usdz_bytes": record["usdz_bytes"],
            "source_usdz_sha256": record["usdz_sha256"],
        }
        assets.append(
            {
                "assembly_domain": None,
                "asset_id": asset_id,
                "composition_kind": "component",
                "parameter_policy_category": "TEST_CATEGORY",
                "primary_category": "TEST_CATEGORY",
                "source_asset_index": index,
                "source_manifest": "RealityKitContent/Assets/asset_manifest_test.json",
                "source_manifest_index": 0,
                **source,
                "variant_ids": [f"{asset_id}::{tier}" for tier in ("minimal", "reduced80", "full")],
            }
        )
        for tier, parameters in (("minimal", minimal), ("reduced80", reduced), ("full", full)):
            variant = {
                "asset_id": asset_id,
                "binds_exact_observed_source_as_presentation": tier == "full",
                "category_id": "TEST_CATEGORY",
                "category_policy_ref": "visual_detail_category_policy_v1#TEST_CATEGORY",
                "geometry_mutation_allowed": False,
                "parameter_policy_category": "TEST_CATEGORY",
                "patient_display_authorized": False,
                "presentation_parameters": parameters,
                "preserve_medical_facts_and_warnings": True,
                "preserve_silhouette_or_meaning": True,
                "source_asset_unchanged": True,
                **source,
                "tier": tier,
                "variant_id": f"{asset_id}::{tier}",
                "virtual_reversible_sidecar": tier != "full",
            }
            if tier == "minimal":
                variant["semantic_density"] = "smallest_reviewed_complete_explanation"
            elif tier == "reduced80":
                variant["semantic_density_target"] = 0.8
            variants.append(variant)
    catalog = {
        "assets": assets,
        "catalog_id": "visual_detail_variant_catalog_v1",
        "category_count": 1,
        "category_counts": {"TEST_CATEGORY": len(records)},
        "full_binding_contract": "exact observed source",
        "lower_tier_contract": "virtual reversible sidecar",
        "module_id": "visual_detail_variants_v1",
        "patient_display_authorized": False,
        "runtime_geometry_included": False,
        "schema_version": "1.0.0",
        "source_geometry_mutation_allowed": False,
        "source_release_asset_count": len(records),
        "source_release_manifest_count": 1,
        "tier_count": 3,
        "tier_order": ["minimal", "reduced80", "full"],
        "variants": variants,
        "virtual_variant_count": len(variants),
    }
    catalog_path = root / "detail_catalog.json"
    policy_path = root / "detail_policy.json"
    catalog_path.write_text(json.dumps(catalog, sort_keys=True), encoding="utf-8")
    policy_path.write_text(json.dumps(policy, sort_keys=True), encoding="utf-8")
    catalog_sha = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    policy_sha = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    return catalog_path, policy_path, catalog_sha, policy_sha


class CatalogTests(unittest.TestCase):
    def test_duplicate_ids_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_manifest(root, [{"id": "known_asset", "title": "One"}])
            (root / "nested").mkdir()
            (root / "nested" / "asset_manifest_duplicate.json").write_text(
                json.dumps({"assets": [{"id": "known_asset", "title": "Two"}]}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CatalogError, "duplicate asset ID"):
                AssetCatalog(root)

    def test_path_like_asset_id_is_not_indexed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_manifest(root, [{"id": "../../private", "title": "Invalid"}])
            with self.assertRaisesRegex(CatalogError, "invalid asset ID"):
                AssetCatalog(root)


class DetailVariantCatalogTests(unittest.TestCase):
    def test_frozen_production_catalog_covers_all_assets_and_tiers(self) -> None:
        repository = Path(__file__).resolve().parents[3]
        source = AssetCatalog(repository / "RealityKitContent" / "Assets")
        pack = repository / "RealityKitContent" / "InterfaceMedia" / "visual_detail_variants_v1"
        details = DetailVariantCatalog(
            pack / "visual_detail_variant_catalog_v1.json",
            pack / "visual_detail_category_policy_v1.json",
            source,
        )
        self.assertEqual(source.asset_count, 150)
        self.assertEqual(details.asset_count, 150)
        self.assertEqual(details.variant_count, 450)
        self.assertEqual(details.document_sha256, FROZEN_DETAIL_CATALOG_SHA256)
        self.assertEqual(details.policy_sha256, FROZEN_DETAIL_POLICY_SHA256)
        for asset_id in source.asset_ids:
            variants = details.variants_for(asset_id)
            self.assertIsNotNone(variants)
            assert variants is not None
            self.assertEqual([item["detail_tier"] for item in variants], list(DETAIL_TIERS))
            observed = source.get(asset_id)
            assert observed is not None
            self.assertTrue(
                all(
                    item["source_asset_revision"]["package_sha256"]
                    == observed.package_sha256
                    for item in variants
                )
            )

    def test_catalog_and_policy_tampering_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog_root = root / "assets"
            catalog_root.mkdir()
            write_manifest(catalog_root, [{"id": "known_asset", "title": "Known"}])
            catalog_path, policy_path, catalog_sha, policy_sha = write_detail_documents(
                root, catalog_root
            )
            source = AssetCatalog(catalog_root)
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["variants"][0]["patient_display_authorized"] = True
            catalog_path.write_text(json.dumps(catalog, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(DetailVariantError, "authorized frozen revision"):
                DetailVariantCatalog(
                    catalog_path,
                    policy_path,
                    source,
                    expected_catalog_sha256=catalog_sha,
                    expected_policy_sha256=policy_sha,
                )
            with self.assertRaisesRegex(DetailVariantError, "safety contract mismatch"):
                DetailVariantCatalog(
                    catalog_path,
                    policy_path,
                    source,
                    expected_catalog_sha256=None,
                    expected_policy_sha256=None,
                )

    def test_policy_recipe_mismatch_and_duplicate_variant_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog_root = root / "assets"
            catalog_root.mkdir()
            write_manifest(catalog_root, [{"id": "known_asset", "title": "Known"}])
            catalog_path, policy_path, _, _ = write_detail_documents(root, catalog_root)
            source = AssetCatalog(catalog_root)
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["variants"][0]["presentation_parameters"]["label_density_ratio"] = 0.3
            catalog_path.write_text(json.dumps(catalog, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(DetailVariantError, "recipe differs from policy"):
                DetailVariantCatalog(
                    catalog_path,
                    policy_path,
                    source,
                    expected_catalog_sha256=None,
                    expected_policy_sha256=None,
                )

            write_detail_documents(root, catalog_root)
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["variants"][1]["variant_id"] = catalog["variants"][0]["variant_id"]
            catalog_path.write_text(json.dumps(catalog, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(DetailVariantError, "invalid or duplicated"):
                DetailVariantCatalog(
                    catalog_path,
                    policy_path,
                    source,
                    expected_catalog_sha256=None,
                    expected_policy_sha256=None,
                )


class ArtifactStoreTests(unittest.TestCase):
    def test_preexisting_directories_and_written_files_are_private(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "shared-output"
            output.mkdir(mode=0o777)
            output.chmod(0o777)
            store = ArtifactStore(output)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)

            job_id = "a" * 24
            job_directory = output / job_id
            job_directory.mkdir(mode=0o777)
            job_directory.chmod(0o777)
            store.materialize(job_id, "asset", "Title", "overview", {}, "b" * 64)

            self.assertEqual(stat.S_IMODE(job_directory.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((job_directory / "scene.usda").stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((job_directory / "recipe.json").stat().st_mode), 0o600)

class ContractTests(unittest.TestCase):
    def test_openapi_contract_matches_safe_preference_inputs(self) -> None:
        path = Path(__file__).resolve().parents[1] / "openapi.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        schema = document["components"]["schemas"]["AdaptationRequest"]
        self.assertEqual(
            schema["properties"]["detail_preference"]["enum"],
            ["overview", "simplified", "standard", "clinical_detail"],
        )
        self.assertEqual(
            schema["properties"]["motion_preference"]["enum"],
            ["system_default", "reduced", "static"],
        )
        self.assertNotIn("anxiety_score", schema["properties"])
        self.assertNotIn("pupil_dilation", schema["properties"])
        application = document["components"]["schemas"]["ApplicationContract"]
        self.assertIn("patient_display_authorized", application["required"])
        self.assertFalse(application["properties"]["patient_display_authorized"]["const"])
        self.assertIn("required_adaptive_policy_approval", application["required"])

    def test_openapi_detail_variant_contract_is_exact_and_separate(self) -> None:
        root = Path(__file__).resolve().parents[1]
        document = json.loads((root / "openapi.json").read_text(encoding="utf-8"))
        self.assertIn("/v1/detail-variants/{asset_id}", document["paths"])
        post = document["paths"]["/v1/detail-variants"]["post"]
        self.assertIn("409", post["responses"])
        request = document["components"]["schemas"]["DetailVariantRequest"]
        self.assertFalse(request["additionalProperties"])
        self.assertEqual(
            set(request["required"]),
            {"asset_id", "detail_tier", "expected_package_sha256"},
        )
        self.assertEqual(
            document["components"]["schemas"]["DetailTier"]["enum"],
            ["minimal", "reduced80", "full"],
        )
        contract = document["components"]["schemas"]["DetailVariantApplicationContract"]
        self.assertEqual(contract["properties"]["runtime_scope"]["const"], "developer_preview_only")
        self.assertFalse(
            contract["properties"]["developer_runtime_application_authorized"]["const"]
        )
        self.assertFalse(contract["properties"]["patient_display_authorized"]["const"])
        example = json.loads(
            (root / "examples" / "detail_variant_request.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(example), set(request["required"]))


class HTTPServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.catalog_root = cls.root / "catalog"
        cls.output_root = cls.root / "outputs"
        cls.catalog_root.mkdir()
        write_manifest(
            cls.catalog_root,
            [
                {
                    "id": "artery_cutaway",
                    "title": "Artery Cutaway",
                    "description": "Educational vessel context",
                    "usdz": "usdz/artery_cutaway.usdz",
                },
                {"id": "device_set", "title": "Device Set"},
                {
                    "id": "brain_orientation_calm_educational_v1",
                    "title": "Calm Brain Orientation",
                    "module": "adaptive_visuals_v1",
                },
                {
                    "id": "approved_source_asset",
                    "title": "Synthetic Approved Source",
                    "clinical_review_status": "APPROVED_FOR_PATIENT_EDUCATION",
                },
            ],
        )
        (
            cls.detail_catalog_path,
            cls.detail_policy_path,
            detail_catalog_sha,
            detail_policy_sha,
        ) = write_detail_documents(cls.root, cls.catalog_root)
        cls.server = build_server(
            "127.0.0.1",
            0,
            cls.catalog_root,
            cls.output_root,
            cls.detail_catalog_path,
            cls.detail_policy_path,
            expected_detail_catalog_sha256=detail_catalog_sha,
            expected_detail_policy_sha256=detail_policy_sha,
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.temporary.cleanup()

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, object] | None = None,
        content_type: str = "application/json",
    ) -> tuple[int, dict[str, object], object]:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        request = Request(self.base_url + path, data=payload, method=method)
        if payload is not None:
            request.add_header("Content-Type", content_type)
        try:
            response = urlopen(request, timeout=2)
        except HTTPError as error:
            response = error
        document = json.loads(response.read().decode("utf-8"))
        return response.status, document, response.headers

    def base_request(self, **changes: object) -> dict[str, object]:
        document: dict[str, object] = {
            "asset_id": "artery_cutaway",
            "audience": "patient",
            "mode": "edit",
            "detail_preference": "standard",
            "adaptation_source": "self_report_preference",
        }
        document.update(changes)
        return document

    def detail_request(self, **changes: object) -> dict[str, object]:
        asset = self.server.service.catalog.get("artery_cutaway")
        assert asset is not None
        document: dict[str, object] = {
            "asset_id": "artery_cutaway",
            "detail_tier": "reduced80",
            "expected_package_sha256": asset.package_sha256,
        }
        document.update(changes)
        return document

    def raw_request(self, payload: bytes) -> bytes:
        with socket.create_connection(("127.0.0.1", self.server.server_port), timeout=2) as connection:
            connection.sendall(payload)
            connection.shutdown(socket.SHUT_WR)
            chunks: list[bytes] = []
            while True:
                chunk = connection.recv(65536)
                if not chunk:
                    return b"".join(chunks)
                chunks.append(chunk)

    def test_health_reports_index_without_paths(self) -> None:
        status, body, _ = self.request("GET", "/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(body["catalog"], {"assets": 4, "manifests": 1})
        self.assertNotIn(str(self.catalog_root), json.dumps(body))
        self.assertFalse(body["diagnostic_inference"])

    def test_request_ids_are_unique_on_one_keep_alive_connection(self) -> None:
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        try:
            identifiers: list[str] = []
            for _ in range(3):
                connection.request("GET", "/healthz")
                response = connection.getresponse()
                response.read()
                self.assertEqual(response.status, 200)
                identifiers.append(response.getheader("X-Request-ID", ""))
        finally:
            connection.close()
        self.assertEqual(len(set(identifiers)), 3)
        self.assertTrue(all(identifiers))

    def test_detail_variant_discovery_returns_exactly_three_path_free_recipes(self) -> None:
        status, body, _ = self.request("GET", "/v1/detail-variants/artery_cutaway")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "available")
        self.assertEqual(body["tier_order"], ["minimal", "reduced80", "full"])
        self.assertEqual(
            [variant["detail_tier"] for variant in body["variants"]],
            ["minimal", "reduced80", "full"],
        )
        self.assertFalse(body["patient_display_authorized"])
        contract = body["application_contract"]
        self.assertEqual(contract["runtime_scope"], "developer_preview_only")
        self.assertTrue(contract["developer_preview_authorized"])
        self.assertFalse(contract["developer_runtime_application_authorized"])
        self.assertEqual(contract["renderer_mapping_status"], "pending_exact_renderer_mapping")
        serialized = json.dumps(body)
        self.assertNotIn(str(self.catalog_root), serialized)
        self.assertNotIn("source_usdz", serialized)
        self.assertNotIn("source_manifest", serialized)

    def test_detail_variant_selection_is_deterministic_revision_bound_and_policy_resolved(self) -> None:
        for tier, density in (("minimal", 0.3), ("reduced80", 0.8), ("full", 1.0)):
            with self.subTest(tier=tier):
                request = self.detail_request(detail_tier=tier)
                first_status, first, _ = self.request("POST", "/v1/detail-variants", request)
                second_status, second, _ = self.request("POST", "/v1/detail-variants", request)
                self.assertEqual(first_status, 200)
                self.assertEqual(second_status, 200)
                self.assertEqual(first["selection_id"], second["selection_id"])
                self.assertEqual(first["selected_variant"], second["selected_variant"])
                self.assertEqual(first["selected_variant"]["detail_tier"], tier)
                self.assertEqual(
                    first["selected_variant"]["recipe"]["presentation_parameters"][
                        "semantic_density_target"
                    ],
                    density,
                )
                self.assertEqual(
                    first["source_asset"]["package_sha256"],
                    request["expected_package_sha256"],
                )
                self.assertFalse(first["patient_display_authorized"])
                self.assertFalse(
                    first["selected_variant"]["recipe"]["patient_display_authorized"]
                )

    def test_detail_variant_selection_rejects_stale_revision_and_unsafe_inputs(self) -> None:
        status, body, _ = self.request(
            "POST",
            "/v1/detail-variants",
            self.detail_request(expected_package_sha256="0" * 64),
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"]["code"], "package_revision_mismatch")

        cases = (
            ({"asset_id": "artery_cutaway", "detail_tier": "minimal"}, "missing_field"),
            (self.detail_request(detail_tier="Reduced80"), "invalid_detail_tier"),
            (self.detail_request(detail_tier="reduced80 "), "invalid_detail_tier"),
            (self.detail_request(detail_tier="standard"), "invalid_detail_tier"),
            (self.detail_request(expected_package_sha256="A" * 64), "invalid_package_sha256"),
            (self.detail_request(pupil_dilation=0.8), "biometric_input_not_accepted"),
            (self.detail_request(gaze_data=[1, 2]), "biometric_input_not_accepted"),
            (self.detail_request(source_usdz="/private/file"), "unknown_field"),
            (self.detail_request(presentation_parameters={}), "unknown_field"),
        )
        for request, code in cases:
            with self.subTest(code=code, request=request):
                case_status, case_body, _ = self.request(
                    "POST", "/v1/detail-variants", request
                )
                self.assertEqual(case_status, 400)
                self.assertEqual(case_body["error"]["code"], code)

    def test_detail_variant_get_rejects_unknown_and_invalid_asset_ids(self) -> None:
        status, body, _ = self.request("GET", "/v1/detail-variants/missing_asset")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"]["code"], "asset_not_found")
        status, body, _ = self.request("GET", "/v1/detail-variants/bad..identifier")
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "invalid_asset_id")

    def test_detail_variant_rejects_duplicate_json_keys_and_nonfinite_numbers(self) -> None:
        asset = self.server.service.catalog.get("artery_cutaway")
        assert asset is not None
        for body in (
            (
                '{"asset_id":"artery_cutaway","detail_tier":"minimal",'
                '"detail_tier":"full","expected_package_sha256":"'
                + asset.package_sha256
                + '"}'
            ),
            (
                '{"asset_id":"artery_cutaway","detail_tier":"minimal",'
                '"expected_package_sha256":"'
                + asset.package_sha256
                + '","sensor_data":NaN}'
            ),
        ):
            raw = body.encode("utf-8")
            response = self.raw_request(
                b"POST /v1/detail-variants HTTP/1.1\r\nHost: localhost\r\n"
                b"Content-Type: application/json\r\nContent-Length: "
                + str(len(raw)).encode("ascii")
                + b"\r\n\r\n"
                + raw
            )
            self.assertIn(b"HTTP/1.1 400", response)
            self.assertIn(b'"code":"invalid_json"', response)

    def test_detail_variant_detects_package_change_after_startup(self) -> None:
        asset = self.server.service.catalog.get("artery_cutaway")
        assert asset is not None
        original = asset.package_path.read_bytes()
        try:
            asset.package_path.write_bytes(original + b"tamper")
            status, body, _ = self.request(
                "POST", "/v1/detail-variants", self.detail_request()
            )
            self.assertEqual(status, 409)
            self.assertEqual(body["error"]["code"], "package_revision_changed")
        finally:
            asset.package_path.write_bytes(original)

    def test_detail_variant_detects_same_size_change_during_hash_observation(self) -> None:
        asset = self.server.service.catalog.get("artery_cutaway")
        assert asset is not None
        original = asset.package_path.read_bytes()
        changed = bytes([original[0] ^ 1]) + original[1:]
        original_hash = AssetCatalog._hash_open_file

        def mutate_after_hash(handle: object) -> str:
            digest = original_hash(handle)  # type: ignore[arg-type]
            asset.package_path.write_bytes(changed)
            return digest

        try:
            with patch.object(AssetCatalog, "_hash_open_file", side_effect=mutate_after_hash):
                status, body, _ = self.request(
                    "POST", "/v1/detail-variants", self.detail_request()
                )
            self.assertEqual(status, 409)
            self.assertEqual(body["error"]["code"], "package_revision_changed")
            self.assertEqual(asset.package_path.stat().st_size, len(original))
        finally:
            asset.package_path.write_bytes(original)

    def test_detail_variant_rejects_catalog_reload_drift_from_frozen_binding(self) -> None:
        asset = self.server.service.catalog.get("artery_cutaway")
        assert asset is not None
        manifest_path = self.catalog_root / "asset_manifest_test.json"
        original_package = asset.package_path.read_bytes()
        original_manifest = manifest_path.read_bytes()
        try:
            changed_package = original_package + b"authorized-elsewhere-but-not-in-detail-catalog"
            asset.package_path.write_bytes(changed_package)
            manifest = json.loads(original_manifest.decode("utf-8"))
            record = next(item for item in manifest["assets"] if item["id"] == "artery_cutaway")
            record["usdz_bytes"] = len(changed_package)
            record["usdz_sha256"] = hashlib.sha256(changed_package).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.server.service.catalog.reload()

            status, body, _ = self.request(
                "POST",
                "/v1/detail-variants",
                {
                    "asset_id": "artery_cutaway",
                    "detail_tier": "minimal",
                    "expected_package_sha256": record["usdz_sha256"],
                },
            )
            self.assertEqual(status, 409)
            self.assertEqual(
                body["error"]["code"], "detail_catalog_source_revision_mismatch"
            )
            get_status, get_body, _ = self.request(
                "GET", "/v1/detail-variants/artery_cutaway"
            )
            self.assertEqual(get_status, 409)
            self.assertEqual(
                get_body["error"]["code"], "detail_catalog_source_revision_mismatch"
            )
        finally:
            asset.package_path.write_bytes(original_package)
            manifest_path.write_bytes(original_manifest)
            self.server.service.catalog.reload()

    def test_detail_variant_logs_omit_selection_inputs(self) -> None:
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        LOGGER.addHandler(handler)
        previous = LOGGER.level
        LOGGER.setLevel(logging.INFO)
        try:
            self.request("POST", "/v1/detail-variants", self.detail_request())
        finally:
            LOGGER.removeHandler(handler)
            LOGGER.setLevel(previous)
        log = stream.getvalue()
        self.assertIn('"route":"/v1/detail-variants"', log)
        self.assertNotIn("artery_cutaway", log)
        self.assertNotIn("reduced80", log)
        asset = self.server.service.catalog.get("artery_cutaway")
        assert asset is not None
        self.assertNotIn(asset.package_sha256, log)

    def test_edit_is_immediate_transparent_reversible_and_static(self) -> None:
        status, body, _ = self.request(
            "POST",
            "/v1/visual-adaptations",
            self.base_request(detail_preference="overview", motion_preference="static"),
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "completed")
        self.assertEqual(body["resolved_mode"], "edit")
        self.assertTrue(body["application_contract"]["developer_preview_authorized"])
        self.assertFalse(body["application_contract"]["source_asset_manifest_approved"])
        self.assertFalse(body["application_contract"]["patient_display_authorized"])
        self.assertTrue(body["application_contract"]["patient_display_review_required"])
        self.assertEqual(
            body["application_contract"]["required_adaptive_policy_approval"],
            "presentation-preference-v1",
        )
        self.assertEqual(body["presentation_preference"]["detail_preference"], "overview")
        self.assertEqual(body["presentation_preference"]["motion_preference"], "static")
        self.assertFalse(body["presentation_preference"]["biometric_inputs_used"])
        self.assertEqual(body["recipe"]["motion"]["speed_multiplier"], 0.0)
        self.assertFalse(body["recipe"]["motion"]["autoplay"])
        self.assertFalse(body["recipe"]["motion"]["looping"])
        self.assertEqual(body["recipe"]["opacity"]["blood_and_particles"], 0.0)
        self.assertTrue(body["recipe"]["comfort_controls"]["reduce_detail_available"])
        self.assertTrue(body["recipe"]["comfort_controls"]["increase_detail_available"])
        self.assertTrue(body["recipe"]["comfort_controls"]["stop_or_pause_available"])
        self.assertTrue(body["recipe"]["comfort_controls"]["exit_or_return_available"])
        self.assertTrue(body["recipe"]["transparency"]["one_action_restore_source"])
        self.assertTrue(body["recipe"]["transparency"]["source_medical_content_remains_available"])
        self.assertNotIn("recommended_fallback_asset_id", body["recipe"])
        candidate = body["orientation_asset_candidate"]
        self.assertEqual(candidate["asset_id"], "brain_orientation_calm_educational_v1")
        self.assertEqual(candidate["role"], "orientation_only_candidate")
        self.assertEqual(candidate["clinical_review_status"], "review_required")
        self.assertFalse(candidate["display_authorized"])
        self.assertFalse(candidate["co_load_with_source"])

    def test_approved_source_does_not_approve_adaptive_policy_or_mapping(self) -> None:
        status, body, _ = self.request(
            "POST",
            "/v1/visual-adaptations",
            self.base_request(asset_id="approved_source_asset"),
        )
        self.assertEqual(status, 200)
        contract = body["application_contract"]
        self.assertTrue(contract["source_asset_manifest_approved"])
        self.assertFalse(contract["patient_display_authorized"])
        self.assertTrue(contract["patient_display_review_required"])

    def test_calm_asset_does_not_recommend_itself(self) -> None:
        status, body, _ = self.request(
            "POST",
            "/v1/visual-adaptations",
            self.base_request(
                asset_id="brain_orientation_calm_educational_v1",
                detail_preference="overview",
            ),
        )
        self.assertEqual(status, 200)
        self.assertNotIn("orientation_asset_candidate", body)

    def test_reduced_motion_overrides_tier_defaults(self) -> None:
        status, body, _ = self.request(
            "POST",
            "/v1/visual-adaptations",
            self.base_request(detail_preference="clinical_detail", motion_preference="reduced"),
        )
        self.assertEqual(status, 200)
        self.assertFalse(body["recipe"]["motion"]["autoplay"])
        self.assertLessEqual(body["recipe"]["motion"]["speed_multiplier"], 0.5)
        self.assertFalse(body["recipe"]["motion"]["looping"])

    def test_seeded_demo_preference_is_reproducible_and_non_diagnostic(self) -> None:
        request = {
            "asset_id": "artery_cutaway",
            "audience": "patient",
            "mode": "auto",
            "adaptation_source": "simulated_demo",
            "simulation_seed": 4281,
        }
        first = self.request("POST", "/v1/visual-adaptations", request)[1]
        second = self.request("POST", "/v1/visual-adaptations", request)[1]
        self.assertEqual(first["recipe_sha256"], second["recipe_sha256"])
        self.assertEqual(first["presentation_preference"], second["presentation_preference"])
        self.assertTrue(first["presentation_preference"]["simulated"])
        self.assertTrue(first["presentation_preference"]["non_diagnostic"])
        self.assertNotIn("anxiety", json.dumps(first).lower())

    def test_family_recipe_requires_patient_authorization_and_privacy(self) -> None:
        status, body, _ = self.request(
            "POST",
            "/v1/visual-adaptations",
            self.base_request(audience="family"),
        )
        self.assertEqual(status, 200)
        access = body["recipe"]["family_access"]
        self.assertTrue(access["patient_participation_or_authorization_confirmation_required"])
        self.assertTrue(access["privacy_confirmation_required"])
        self.assertFalse(access["may_exceed_patient_authorized_detail"])

    def test_biometric_and_anxiety_fields_are_rejected(self) -> None:
        for field, value in (
            ("pupil_dilation", 0.8),
            ("joint_movement", [1, 2]),
            ("anxiety_score", 0.6),
            ("simulated_anxiety_score", 0.4),
        ):
            with self.subTest(field=field):
                status, body, _ = self.request("POST", "/v1/visual-adaptations", self.base_request(**{field: value}))
                self.assertEqual(status, 400)
                self.assertEqual(body["error"]["code"], "biometric_input_not_accepted")

    def test_path_traversal_and_unknown_asset_are_rejected(self) -> None:
        status, body, _ = self.request(
            "POST", "/v1/visual-adaptations", self.base_request(asset_id="../../etc/passwd")
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "invalid_asset_id")
        status, body, _ = self.request(
            "POST", "/v1/visual-adaptations", self.base_request(asset_id="missing_asset")
        )
        self.assertEqual(status, 404)
        self.assertEqual(body["error"]["code"], "asset_not_found")

    def test_non_demo_requires_preference_and_rejects_seed(self) -> None:
        missing = self.base_request()
        del missing["detail_preference"]
        status, body, _ = self.request("POST", "/v1/visual-adaptations", missing)
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["field"], "detail_preference")
        status, body, _ = self.request(
            "POST", "/v1/visual-adaptations", self.base_request(simulation_seed=7)
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "simulation_seed_not_allowed")

    def test_wrong_json_types_return_validation_errors_not_server_errors(self) -> None:
        for field, value, expected in (
            ("audience", ["patient"], "invalid_audience"),
            ("mode", {"value": "edit"}, "invalid_mode"),
            ("adaptation_source", ["simulated_demo"], "invalid_adaptation_source"),
            ("detail_preference", ["overview"], "invalid_detail_preference"),
            ("motion_preference", {"value": "static"}, "invalid_motion_preference"),
        ):
            with self.subTest(field=field):
                status, body, _ = self.request(
                    "POST",
                    "/v1/visual-adaptations",
                    self.base_request(**{field: value}),
                )
                self.assertEqual(status, 400)
                self.assertEqual(body["error"]["code"], expected)

    def test_rejected_body_framing_closes_connection_without_second_request(self) -> None:
        requests = [
            (
                b"POST /v1/visual-adaptations HTTP/1.1\r\nHost: localhost\r\n"
                b"Content-Type: application/json\r\nContent-Length: 20000\r\n\r\n"
                b"GET /healthz HTTP/1.1\r\nHost: localhost\r\n\r\n",
                b"413",
            ),
            (
                b"POST /v1/visual-adaptations HTTP/1.1\r\nHost: localhost\r\n"
                b"Content-Type: application/json\r\nTransfer-Encoding: chunked\r\n"
                b"Content-Length: 0\r\n\r\n0\r\n\r\n"
                b"GET /healthz HTTP/1.1\r\nHost: localhost\r\n\r\n",
                b"400",
            ),
            (
                b"GET /healthz HTTP/1.1\r\nHost: localhost\r\nContent-Length: 100\r\n\r\n"
                b"GET /healthz HTTP/1.1\r\nHost: localhost\r\n\r\n",
                b"400",
            ),
        ]
        for payload, expected_status in requests:
            with self.subTest(expected_status=expected_status):
                response = self.raw_request(payload)
                self.assertEqual(response.count(b"HTTP/1.1"), 1)
                self.assertIn(expected_status, response.split(b"\r\n", 1)[0])
                self.assertNotIn(b'"status":"ok"', response)

    def test_content_length_accepts_ascii_digits_only(self) -> None:
        body = json.dumps(self.detail_request(), separators=(",", ":")).encode("utf-8")
        decimal = str(len(body))
        invalid_lengths = [f"+{decimal}", f"{decimal[0]}_{decimal[1:]}"]
        for raw_length in invalid_lengths:
            with self.subTest(raw_length=raw_length):
                response = self.raw_request(
                    b"POST /v1/detail-variants HTTP/1.1\r\nHost: localhost\r\n"
                    b"Content-Type: application/json\r\nContent-Length: "
                    + raw_length.encode("ascii")
                    + b"\r\n\r\n"
                    + body
                )
                self.assertEqual(response.count(b"HTTP/1.1"), 1)
                self.assertIn(b"HTTP/1.1 400", response)
                self.assertIn(b'"code":"invalid_content_length"', response)
        for raw_length in ("+0", "0_0"):
            with self.subTest(bodyless_raw_length=raw_length):
                response = self.raw_request(
                    b"GET /healthz HTTP/1.1\r\nHost: localhost\r\nContent-Length: "
                    + raw_length.encode("ascii")
                    + b"\r\n\r\n"
                )
                self.assertEqual(response.count(b"HTTP/1.1"), 1)
                self.assertIn(b"HTTP/1.1 400", response)
                self.assertIn(b'"code":"invalid_content_length"', response)

    def test_connection_error_log_omits_client_address_and_exception_text(self) -> None:
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        LOGGER.addHandler(handler)
        previous = LOGGER.level
        LOGGER.setLevel(logging.INFO)
        try:
            try:
                raise BrokenPipeError("sensitive-path-or-payload")
            except BrokenPipeError:
                self.server.handle_error(object(), ("203.0.113.99", 4444))
        finally:
            LOGGER.removeHandler(handler)
            LOGGER.setLevel(previous)
        log = stream.getvalue()
        self.assertIn('"event":"connection_error"', log)
        self.assertIn('"error_type":"BrokenPipeError"', log)
        self.assertNotIn("203.0.113.99", log)
        self.assertNotIn("4444", log)
        self.assertNotIn("sensitive-path-or-payload", log)

    def test_alias_is_supported_but_canonical_endpoint_is_returned(self) -> None:
        status, body, _ = self.request("POST", "/v1/adaptations", self.base_request())
        self.assertEqual(status, 200)
        self.assertEqual(body["endpoint_alias"]["canonical"], "/v1/visual-adaptations")

    def test_generate_is_async_non_ai_and_clinician_gated(self) -> None:
        status, body, _ = self.request(
            "POST",
            "/v1/visual-adaptations",
            self.base_request(mode="generate", detail_preference="overview"),
        )
        self.assertEqual(status, 202)
        contract = body["generation_contract"]
        self.assertEqual(contract["generator_kind"], "deterministic_non_ai_template")
        self.assertIsNone(contract["model_provider"])
        self.assertFalse(contract["display_authorized"])
        self.assertEqual(contract["review_gate"], "clinician_review_required_before_display")
        self.assertEqual(contract["artifact_role"], "abstract_procedural_review_draft")
        candidate = contract["orientation_asset_candidate"]
        self.assertEqual(candidate["asset_id"], "brain_orientation_calm_educational_v1")
        self.assertFalse(candidate["display_authorized"])
        self.assertIn("review_required", candidate["clinical_review_status"])

        job_id = contract["job_id"]
        deadline = time.monotonic() + 2
        while True:
            job_status, job, _ = self.request("GET", f"/v1/jobs/{job_id}")
            self.assertEqual(job_status, 200)
            if job["status"] != "queued" or time.monotonic() >= deadline:
                break
            time.sleep(0.01)
        self.assertEqual(job["status"], "awaiting_clinician_review")
        self.assertFalse(job["display_authorized"])

        scene_path = job["draft_artifacts"]["scene"]["href"]
        response = urlopen(self.base_url + scene_path, timeout=2)
        scene = response.read().decode("utf-8")
        self.assertEqual(response.headers["X-Display-Authorized"], "false")
        self.assertEqual(response.headers["X-Clinical-Review-Required"], "true")
        self.assertIn("#usda 1.0", scene)
        self.assertIn("not anatomy and not for clinical decisions", scene)
        self.assertNotIn("@", scene)  # no external USD references

    def test_logs_do_not_contain_request_values(self) -> None:
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        LOGGER.addHandler(handler)
        previous = LOGGER.level
        LOGGER.setLevel(logging.INFO)
        try:
            self.request(
                "POST",
                "/v1/visual-adaptations",
                {
                    "asset_id": "device_set",
                    "audience": "patient",
                    "mode": "edit",
                    "adaptation_source": "simulated_demo",
                    "simulation_seed": 9223372036854775000,
                },
            )
        finally:
            LOGGER.removeHandler(handler)
            LOGGER.setLevel(previous)
        log = stream.getvalue()
        self.assertIn('"route":"/v1/visual-adaptations"', log)
        self.assertNotIn("device_set", log)
        self.assertNotIn("9223372036854775000", log)


if __name__ == "__main__":
    unittest.main()
