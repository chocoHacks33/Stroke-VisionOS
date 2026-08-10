from __future__ import annotations

import copy
from importlib import resources
from pathlib import Path
import json
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen

from adaptive_asset_service.bindings import BindingError, EntityBindingCatalog
from adaptive_asset_service.catalog import AssetCatalog
from adaptive_asset_service.policy import make_recipe
from adaptive_asset_service.profiles import AdaptationProfileCatalog, ProfileError
from adaptive_asset_service.server import build_server


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CATALOG_ROOT = REPOSITORY_ROOT / "RealityKitContent" / "Assets"
PROFILE_ROOT = (
    REPOSITORY_ROOT
    / "Services"
    / "AdaptiveAssetService"
    / "adaptive_asset_service"
    / "runtime_profiles"
)


class FullCatalogProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = AssetCatalog(CATALOG_ROOT)
        cls.profiles = AdaptationProfileCatalog(
            PROFILE_ROOT / "catalog_adaptation_profiles.json",
            cls.catalog,
        )
        cls.bindings = EntityBindingCatalog(
            PROFILE_ROOT / "realitykit_entity_bindings.json",
            cls.catalog,
        )

    def test_all_released_assets_have_profiles_and_exact_bindings(self) -> None:
        self.assertEqual(self.catalog.asset_count, 135)
        self.assertEqual(self.profiles.asset_count, 135)
        self.assertEqual(self.bindings.asset_count, 135)
        self.assertEqual(
            sum(self.bindings.get(asset["asset_id"]).model_entity_count for asset in self.catalog.public_assets()),
            3472,
        )
        self.assertEqual(
            sum(self.bindings.get(asset["asset_id"]).animation_resource_count for asset in self.catalog.public_assets()),
            24,
        )

    def test_runtime_profile_documents_are_packaged_with_the_service(self) -> None:
        package_root = resources.files("adaptive_asset_service.runtime_profiles")
        expected = {
            "catalog_adaptation_profiles.json",
            "catalog_adaptation_profiles.schema.json",
            "realitykit_entity_bindings.json",
            "realitykit_entity_map.json",
        }
        observed = {
            item.name
            for item in package_root.iterdir()
            if item.name.endswith(".json")
        }
        self.assertEqual(observed, expected)

    def test_layered_head_overview_resolves_optional_entities_without_hiding_primary_anatomy(self) -> None:
        asset_id = "layered_head_cutaway_registered_v2"
        recipe = make_recipe(asset_id, "patient", "overview", "static")
        profile = self.profiles.get(asset_id)
        plan = self.bindings.application_plan(asset_id, recipe, profile)
        self.assertEqual(plan["mapping_status"], "exact_revision_bound")
        self.assertEqual(len(plan["visibility_operations"]), 4)
        self.assertTrue(
            all("anatomy_secondary" in operation["matched_groups"] for operation in plan["visibility_operations"])
        )
        self.assertEqual(plan["protected_primary_matches_not_hidden"], 0)
        self.assertEqual(len(plan["material_operations"]), 9)
        self.assertTrue(plan["source_asset_unchanged"])
        self.assertTrue(plan["source_medical_content_remains_available"])
        self.assertFalse(plan["patient_display_authorized"])
        self.assertEqual(
            plan["medical_content_preservation_status"],
            "requires_external_clinical_and_human_factors_review",
        )
        self.assertEqual(plan["opacity_contract"]["opacity_operations"], [])
        self.assertFalse(plan["lod_contract"]["applied"])
        self.assertTrue(plan["content_warning_required"])

    def test_primary_pathology_is_never_automatically_hidden(self) -> None:
        asset_id = "ischemic_mca_clot_v2"
        recipe = make_recipe(asset_id, "family", "overview", "static")
        # Exercise the protection invariant even if a future tier asks to hide pathology.
        recipe["detail"]["hidden_layer_groups"].append("pathology_primary")
        profile = self.profiles.get(asset_id)
        plan = self.bindings.application_plan(asset_id, recipe, profile)
        self.assertEqual(plan["visibility_operations"], [])
        self.assertEqual(plan["protected_primary_matches_not_hidden"], 1)
        self.assertTrue(plan["unresolved_requested_changes"])
        self.assertEqual(plan["material_operations"], [])
        self.assertTrue(plan["source_medical_content_remains_available"])

    def test_animated_asset_targets_the_exact_animation_entities(self) -> None:
        asset_id = "cerebral_bloodflow_animation_v2"
        recipe = make_recipe(asset_id, "patient", "simplified", "static")
        profile = self.profiles.get(asset_id)
        plan = self.bindings.application_plan(asset_id, recipe, profile)
        self.assertEqual(sum(item["animation_resource_count"] for item in plan["animation_operations"]), 24)
        self.assertTrue(all(item["speed_multiplier"] == 0.0 for item in plan["animation_operations"]))
        self.assertTrue(all(item["autoplay"] is False for item in plan["animation_operations"]))
        self.assertTrue(
            all(item["static_pose_strategy"] == "initial_authored_pose" for item in plan["animation_operations"])
        )
        self.assertTrue(
            all(item["reviewed_static_frame_available"] is False for item in plan["animation_operations"])
        )

    def test_clinical_detail_preserves_source_materials_and_labels(self) -> None:
        asset_id = "spatial_step_markers"
        recipe = make_recipe(asset_id, "patient", "clinical_detail", "system_default")
        profile = self.profiles.get(asset_id)
        plan = self.bindings.application_plan(asset_id, recipe, profile)
        self.assertEqual(plan["material_operations"], [])
        self.assertEqual(plan["material_contract"]["clinical_detail_behavior"], "preserve_source_materials")
        self.assertFalse(plan["presentation_ui_contract"]["authored_geometry_labels_automatically_hidden"])

    def test_material_preview_excludes_primary_pathology_and_mapped_labels(self) -> None:
        for asset_id in ("ischemic_mca_clot_v2", "spatial_step_markers"):
            with self.subTest(asset_id=asset_id):
                recipe = make_recipe(asset_id, "patient", "simplified", "reduced")
                profile = self.profiles.get(asset_id)
                plan = self.bindings.application_plan(asset_id, recipe, profile)
                self.assertEqual(plan["material_operations"], [])
                self.assertGreaterEqual(plan["material_contract"]["protected_entity_count"], 1)

    def test_every_profile_is_display_blocked_and_non_diagnostic(self) -> None:
        for asset in self.catalog.public_assets():
            profile = self.profiles.get(asset["asset_id"])
            with self.subTest(asset_id=asset["asset_id"]):
                self.assertFalse(profile.clinical_safeguards["patient_display_authorized"])
                self.assertFalse(profile.clinical_safeguards["anxiety_inference_allowed"])
                self.assertTrue(profile.clinical_safeguards["preserve_material_facts"])

    def test_binding_loader_rejects_tampered_selectors_types_counts_and_debug_paths(self) -> None:
        source = json.loads((PROFILE_ROOT / "realitykit_entity_bindings.json").read_text(encoding="utf-8"))
        topology = (PROFILE_ROOT / "realitykit_entity_map.json").read_bytes()

        def out_of_tree(document: dict[str, object]) -> None:
            document["assets"][0]["bindings"][0]["child_index_path"] = [999999]

        def string_boolean(document: dict[str, object]) -> None:
            document["assets"][0]["bindings"][0]["automatic_visibility_change_allowed"] = "false"

        def negative_material_slots(document: dict[str, object]) -> None:
            document["assets"][0]["bindings"][0]["material_slots"] = -7

        def missing_aggregate_counts(document: dict[str, object]) -> None:
            document.pop("asset_count")
            document.pop("model_entity_count")

        def empty_semantic_counts(document: dict[str, object]) -> None:
            document["assets"][0]["semantic_group_counts"] = {}

        def private_debug_path(document: dict[str, object]) -> None:
            document["assets"][0]["bindings"][0]["debug_path"] = "/Users/private/patient-name"

        cases = {
            "out-of-tree selector": out_of_tree,
            "string boolean": string_boolean,
            "negative material slots": negative_material_slots,
            "missing aggregate counts": missing_aggregate_counts,
            "empty semantic counts": empty_semantic_counts,
            "private debug path": private_debug_path,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "realitykit_entity_map.json").write_bytes(topology)
            binding_path = root / "realitykit_entity_bindings.json"
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    document = copy.deepcopy(source)
                    mutate(document)
                    binding_path.write_text(json.dumps(document), encoding="utf-8")
                    with self.assertRaises(BindingError):
                        EntityBindingCatalog(binding_path, self.catalog)

    def test_profile_loader_rejects_stale_or_unsafe_contracts(self) -> None:
        source = json.loads((PROFILE_ROOT / "catalog_adaptation_profiles.json").read_text(encoding="utf-8"))

        def stale_digest(document: dict[str, object]) -> None:
            document["generated_from"]["manifest_set_sha256"] = "0" * 64

        def source_restore_disabled(document: dict[str, object]) -> None:
            document["profiles"][0]["replacement_rules"]["source_must_remain_available"] = False

        def approved_review_status(document: dict[str, object]) -> None:
            document["profiles"][0]["clinical_safeguards"]["required_review_status"] = "APPROVED"

        def patient_specific(document: dict[str, object]) -> None:
            document["profiles"][0]["clinical_safeguards"]["patient_specific"] = True

        cases = {
            "stale manifest digest": stale_digest,
            "source restore disabled": source_restore_disabled,
            "unsafe review status": approved_review_status,
            "patient-specific profile": patient_specific,
        }
        with tempfile.TemporaryDirectory() as temporary:
            profile_path = Path(temporary) / "catalog_adaptation_profiles.json"
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    document = copy.deepcopy(source)
                    mutate(document)
                    profile_path.write_text(json.dumps(document), encoding="utf-8")
                    with self.assertRaises(ProfileError):
                        AdaptationProfileCatalog(profile_path, self.catalog)

    def test_default_catalog_can_serve_an_executable_revision_bound_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            server = build_server(
                "127.0.0.1",
                0,
                CATALOG_ROOT,
                Path(temporary),
                PROFILE_ROOT / "catalog_adaptation_profiles.json",
                PROFILE_ROOT / "realitykit_entity_bindings.json",
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}"
            try:
                health = json.loads(urlopen(base_url + "/healthz", timeout=2).read())
                self.assertTrue(health["adaptation_mapping"]["configured"])
                self.assertEqual(health["adaptation_mapping"]["profiled_assets"], 135)
                catalog = json.loads(urlopen(base_url + "/v1/catalog", timeout=2).read())
                self.assertEqual(len(catalog["assets"]), 135)
                self.assertTrue(all("adaptation_profile" in asset for asset in catalog["assets"]))
                payload = json.dumps(
                    {
                        "asset_id": "brain_anatomy_realistic_v2",
                        "audience": "patient",
                        "mode": "edit",
                        "detail_preference": "overview",
                        "adaptation_source": "self_report_preference",
                        "motion_preference": "static",
                    }
                ).encode("utf-8")
                request = Request(
                    base_url + "/v1/visual-adaptations",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                response = json.loads(urlopen(request, timeout=2).read())
                self.assertEqual(response["application_plan"]["mapping_status"], "exact_revision_bound")
                self.assertTrue(response["application_contract"]["developer_runtime_application_authorized"])
                self.assertFalse(response["application_contract"]["patient_display_authorized"])
                self.assertEqual(
                    response["application_plan"]["source_package_sha256"],
                    response["source_asset"]["package_sha256"],
                )
                self.assertFalse(response["orientation_asset_candidate"]["display_authorized"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
