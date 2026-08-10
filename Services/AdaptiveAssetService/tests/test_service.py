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
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from adaptive_asset_service.catalog import AssetCatalog, CatalogError
from adaptive_asset_service.bindings import EntityBindingCatalog
from adaptive_asset_service.policy import POLICY_VERSION
from adaptive_asset_service.procedural import ArtifactStore
from adaptive_asset_service.profiles import AdaptationProfileCatalog
from adaptive_asset_service.server import LOGGER, build_server
from adaptive_asset_service.service import AdaptationService


def write_manifest(root: Path, assets: list[dict[str, object]]) -> None:
    prepared: list[dict[str, object]] = []
    for index, source in enumerate(assets):
        record = dict(source)
        package_relative = str(record.setdefault("usdz", f"packages/test_asset_{index}.usdz"))
        package = root / package_relative
        package.parent.mkdir(parents=True, exist_ok=True)
        payload = f"synthetic-usdz:{index}:{record.get('id', 'invalid')}".encode("utf-8")
        package.write_bytes(payload)
        record.setdefault("usdz_bytes", len(payload))
        record.setdefault("usdz_sha256", hashlib.sha256(payload).hexdigest())
        prepared.append(record)
    path = root / "asset_manifest_test.json"
    path.write_text(
        json.dumps(
            {
                "kit": "test-kit",
                "module": "test-module",
                "clinical_review_status": "review_required",
                "assets": prepared,
            }
        ),
        encoding="utf-8",
    )


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

    def test_public_assets_are_sorted_and_path_free(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_manifest(
                root,
                [
                    {"id": "z_asset", "title": "Zed", "usdz": "exports/usdz/z_asset.usdz"},
                    {"id": "a_asset", "title": "Alpha", "usdz": "exports/usdz/a_asset.usdz"},
                ],
            )
            catalog = AssetCatalog(root)
            public = catalog.public_assets()
            self.assertEqual([asset["asset_id"] for asset in public], ["a_asset", "z_asset"])
            self.assertEqual(public[0]["package_name"], "a_asset.usdz")
            self.assertNotIn("manifest_name", public[0])
            self.assertNotIn(str(root), json.dumps(public))

    def test_missing_or_escaping_package_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog_root = root / "catalog"
            catalog_root.mkdir()
            (catalog_root / "asset_manifest_missing.json").write_text(
                json.dumps({"assets": [{"id": "missing_asset", "usdz": "missing.usdz"}]}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CatalogError, "no readable USDZ package"):
                AssetCatalog(catalog_root)

            outside = root / "outside.usdz"
            outside.write_bytes(b"outside")
            (catalog_root / "asset_manifest_missing.json").write_text(
                json.dumps({"assets": [{"id": "escaping_asset", "usdz": "../outside.usdz"}]}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CatalogError, "unsafe USDZ package"):
                AssetCatalog(catalog_root)

    def test_manifest_integrity_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "asset.usdz"
            package.write_bytes(b"actual-package")
            manifest = root / "asset_manifest_test.json"
            manifest.write_text(
                json.dumps(
                    {
                        "assets": [
                            {
                                "id": "bad_bytes",
                                "usdz": package.name,
                                "usdz_bytes": 1,
                                "usdz_sha256": hashlib.sha256(b"actual-package").hexdigest(),
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CatalogError, "byte-count mismatch"):
                AssetCatalog(root)

            manifest.write_text(
                json.dumps(
                    {
                        "assets": [
                            {
                                "id": "bad_hash",
                                "usdz": package.name,
                                "usdz_bytes": package.stat().st_size,
                                "usdz_sha256": "0" * 64,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CatalogError, "SHA-256 mismatch"):
                AssetCatalog(root)

    def test_public_catalog_exposes_content_revision_without_local_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_manifest(root, [{"id": "known_asset", "title": "Known"}])
            public = AssetCatalog(root).public_assets()[0]
            self.assertEqual(public["package_integrity"], "verified_against_manifest")
            self.assertRegex(str(public["package_sha256"]), r"^[a-f0-9]{64}$")
            self.assertGreater(int(public["package_bytes"]), 0)
            self.assertNotIn(str(root), json.dumps(public))

    def test_recipe_fingerprint_changes_with_source_package_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "source.usdz"
            manifest = root / "asset_manifest_test.json"

            def response_for(payload: bytes) -> dict[str, object]:
                package.write_bytes(payload)
                manifest.write_text(
                    json.dumps(
                        {
                            "assets": [
                                {
                                    "id": "revisioned_asset",
                                    "usdz": package.name,
                                    "usdz_bytes": len(payload),
                                    "usdz_sha256": hashlib.sha256(payload).hexdigest(),
                                }
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
                service = AdaptationService(AssetCatalog(root), ArtifactStore(root / "output"))
                try:
                    status, document = service.adapt(
                        {
                            "asset_id": "revisioned_asset",
                            "audience": "patient",
                            "mode": "edit",
                            "adaptation_source": "self_report_preference",
                            "detail_preference": "simplified",
                        },
                        "request-id",
                    )
                    self.assertEqual(status, 200)
                    return document
                finally:
                    service.close()

            first = response_for(b"source-revision-one")
            second = response_for(b"source-revision-two")
            self.assertNotEqual(first["adaptation_id"], second["adaptation_id"])
            self.assertNotEqual(first["recipe_sha256"], second["recipe_sha256"])
            self.assertNotEqual(
                first["recipe"]["source_asset_revision"]["package_sha256"],
                second["recipe"]["source_asset_revision"]["package_sha256"],
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
        self.assertEqual(document["info"]["version"], "0.2.0")
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
        self.assertIn("(?!.*\\.\\.)", schema["properties"]["asset_id"]["pattern"])
        source_asset = document["components"]["schemas"]["SourceAsset"]
        self.assertIn("package_sha256", source_asset["required"])
        self.assertEqual(source_asset["properties"]["package_sha256"]["pattern"], "^[a-f0-9]{64}$")
        recipe = document["components"]["schemas"]["Recipe"]
        self.assertIn("source_asset_revision", recipe["required"])
        self.assertEqual(
            recipe["properties"]["source_asset_revision"]["$ref"],
            "#/components/schemas/SourceAssetRevision",
        )
        application = document["components"]["schemas"]["ApplicationContract"]
        self.assertIn("patient_display_authorized", application["required"])
        self.assertFalse(application["properties"]["patient_display_authorized"]["const"])
        self.assertIn("required_adaptive_policy_approval", application["required"])
        self.assertEqual(
            application["properties"]["required_adaptive_policy_approval"]["const"],
            POLICY_VERSION,
        )
        self.assertIn("developer_runtime_application_authorized", application["required"])
        self.assertIn("semantic_mapping_status", application["required"])
        self.assertIn("fallback_required", application["required"])
        self.assertIn("ApplicationPlan", document["components"]["schemas"])
        self.assertIn("ReviewArtifactEnvelope", document["components"]["schemas"])
        self.assertIn("/v1/catalog", document["paths"])
        for endpoint in ("/v1/visual-adaptations", "/v1/adaptations"):
            responses = document["paths"][endpoint]["post"]["responses"]
            for status in ("400", "404", "411", "413", "415"):
                self.assertIn(status, responses)
        catalog_asset = document["components"]["schemas"]["CatalogAsset"]
        self.assertIn("package_sha256", catalog_asset["required"])
        self.assertNotIn("manifest_path", catalog_asset["properties"])


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
        cls.server = build_server("127.0.0.1", 0, cls.catalog_root, cls.output_root)
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

    def test_control_panel_is_served_with_strict_security_headers(self) -> None:
        response = urlopen(self.base_url + "/", timeout=2)
        html = response.read().decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("text/html", response.headers["Content-Type"])
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("camera=()", response.headers["Permissions-Policy"])
        self.assertIn("microphone=()", response.headers["Permissions-Policy"])
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertIn("Adaptive Visual Lab", html)
        self.assertIn("Patient display blocked", html)
        self.assertIn("Preference, not diagnosis", html)
        self.assertIn('<script src="/ui/app.js" defer></script>', html)
        self.assertNotIn("<style", html)

        css = urlopen(self.base_url + "/ui/app.css", timeout=2)
        script = urlopen(self.base_url + "/ui/app.js", timeout=2)
        self.assertIn("text/css", css.headers["Content-Type"])
        self.assertIn("text/javascript", script.headers["Content-Type"])
        self.assertIn(b"prefers-reduced-motion", css.read())
        self.assertIn(b"/v1/visual-adaptations", script.read())

    def test_catalog_endpoint_returns_sorted_public_metadata(self) -> None:
        status, body, _ = self.request("GET", "/v1/catalog")
        self.assertEqual(status, 200)
        self.assertEqual(body["catalog"], {"assets": 4, "manifests": 1})
        identifiers = [asset["asset_id"] for asset in body["assets"]]
        self.assertEqual(identifiers, sorted(identifiers))
        self.assertEqual(len(identifiers), 4)
        self.assertNotIn("manifest_name", body["assets"][0])
        self.assertNotIn(str(self.catalog_root), json.dumps(body))

    def test_ui_static_allowlist_rejects_unknown_and_encoded_traversal(self) -> None:
        for path in ("/ui/unknown.js", "/ui/%2e%2e/server.py"):
            with self.subTest(path=path):
                status, body, _ = self.request("GET", path)
                self.assertEqual(status, 404)
                self.assertEqual(body["error"]["code"], "route_not_found")

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
            POLICY_VERSION,
        )
        self.assertEqual(body["presentation_preference"]["detail_preference"], "overview")
        self.assertEqual(body["presentation_preference"]["motion_preference"], "static")
        self.assertFalse(body["presentation_preference"]["biometric_inputs_used"])
        self.assertEqual(body["source_asset"]["package_integrity"], "verified_against_manifest")
        self.assertEqual(
            body["recipe"]["source_asset_revision"]["package_sha256"],
            body["source_asset"]["package_sha256"],
        )
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
        self.assertNotIn("orientation_asset_candidate", body)
        self.assertEqual(body["application_contract"]["semantic_mapping_status"], "not_configured")
        self.assertFalse(body["application_contract"]["developer_runtime_application_authorized"])
        self.assertTrue(body["application_contract"]["fallback_required"])

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
        self.assertNotIn("orientation_asset_candidate", contract)

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
        self.assertIn('bool displayAuthorized = false', scene)
        self.assertIn('string artifactRole = "abstract_procedural_review_draft"', scene)
        self.assertIn("not authorized for patient display", scene)
        self.assertNotIn("@", scene)  # no external USD references

        recipe_path = job["draft_artifacts"]["recipe"]["href"]
        recipe_response = urlopen(self.base_url + recipe_path, timeout=2)
        recipe_artifact = json.loads(recipe_response.read().decode("utf-8"))
        self.assertEqual(recipe_response.headers["X-Display-Authorized"], "false")
        self.assertFalse(recipe_artifact["display_authorized"])
        self.assertEqual(recipe_artifact["artifact_role"], "abstract_procedural_review_draft")
        self.assertEqual(
            recipe_artifact["review_gate"],
            "specialist_and_human_factors_review_required_before_patient_display",
        )
        self.assertIn("recipe", recipe_artifact)

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


class FullCatalogIntegrationTests(unittest.TestCase):
    def test_every_catalog_asset_has_a_content_bound_fail_closed_edit_contract(self) -> None:
        repository = Path(__file__).resolve().parents[3]
        catalog_root = repository / "RealityKitContent" / "Assets"
        catalog = AssetCatalog(catalog_root)
        profile_root = (
            repository
            / "Services"
            / "AdaptiveAssetService"
            / "adaptive_asset_service"
            / "runtime_profiles"
        )
        profiles = AdaptationProfileCatalog(
            profile_root / "catalog_adaptation_profiles.json",
            catalog,
        )
        bindings = EntityBindingCatalog(
            profile_root / "realitykit_entity_bindings.json",
            catalog,
        )
        self.assertEqual(catalog.asset_count, 135)
        self.assertEqual(catalog.manifest_count, 12)

        public_assets = catalog.public_assets()
        integrity_counts: dict[str, int] = {}
        for asset in public_assets:
            status = str(asset["package_integrity"])
            integrity_counts[status] = integrity_counts.get(status, 0) + 1
        self.assertEqual(integrity_counts["verified_against_manifest"], 99)
        self.assertEqual(integrity_counts["observed_without_manifest_digest"], 36)

        with tempfile.TemporaryDirectory() as temporary:
            service = AdaptationService(catalog, ArtifactStore(Path(temporary)), profiles, bindings)
            fingerprints: set[str] = set()
            try:
                for asset in public_assets:
                    asset_id = str(asset["asset_id"])
                    for detail_preference in ("overview", "simplified", "standard", "clinical_detail"):
                        status, document = service.adapt(
                            {
                                "asset_id": asset_id,
                                "audience": "patient",
                                "mode": "edit",
                                "adaptation_source": "self_report_preference",
                                "detail_preference": detail_preference,
                                "motion_preference": "reduced",
                            },
                            "catalog-integration-request",
                        )
                        self.assertEqual(status, 200)
                        self.assertFalse(document["application_contract"]["patient_display_authorized"])
                        self.assertTrue(document["application_contract"]["developer_runtime_application_authorized"])
                        self.assertEqual(
                            document["application_contract"]["semantic_mapping_status"],
                            "exact_revision_bound",
                        )
                        self.assertEqual(document["application_plan"]["source_package_sha256"], asset["package_sha256"])
                        self.assertEqual(
                            document["recipe"]["source_asset_revision"]["package_sha256"],
                            asset["package_sha256"],
                        )
                        self.assertEqual(document["source_asset"]["package_bytes"], asset["package_bytes"])
                        fingerprints.add(str(document["recipe_sha256"]))
                        profile = profiles.get(asset_id)
                        expects_candidate = (
                            detail_preference == "overview"
                            and asset_id != "brain_orientation_calm_educational_v1"
                            and "brain_orientation_calm_educational_v1"
                            in profile.replacement_rules["candidate_replacement_asset_ids"]
                        )
                        if expects_candidate:
                            candidate = document["orientation_asset_candidate"]
                            self.assertFalse(candidate["display_authorized"])
                            self.assertRegex(str(candidate["package_sha256"]), r"^[a-f0-9]{64}$")
                        else:
                            self.assertNotIn("orientation_asset_candidate", document)
            finally:
                service.close()
        self.assertEqual(len(fingerprints), 135 * 4)


if __name__ == "__main__":
    unittest.main()
