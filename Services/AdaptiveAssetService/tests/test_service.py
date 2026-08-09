from __future__ import annotations

from io import StringIO
from http.client import HTTPConnection
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
from adaptive_asset_service.procedural import ArtifactStore
from adaptive_asset_service.server import LOGGER, build_server


def write_manifest(root: Path, assets: list[dict[str, object]]) -> None:
    path = root / "asset_manifest_test.json"
    path.write_text(
        json.dumps(
            {
                "kit": "test-kit",
                "module": "test-module",
                "clinical_review_status": "review_required",
                "assets": assets,
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
