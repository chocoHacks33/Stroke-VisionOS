"""Request validation and adaptation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .catalog import AssetCatalog, valid_asset_id
from .policy import NON_DIAGNOSTIC_NOTICE, POLICY_VERSION, make_recipe, recipe_fingerprint, simulate_preference
from .procedural import ArtifactStore


ALLOWED_FIELDS = {
    "asset_id",
    "audience",
    "mode",
    "detail_preference",
    "adaptation_source",
    "simulation_seed",
    "motion_preference",
}
BIOMETRIC_FIELDS = {
    "pupil_dilation",
    "pupil_size",
    "eye_tracking",
    "joint_movement",
    "joint_movements",
    "movement_data",
    "biometrics",
    "diagnosed_anxiety",
    "anxiety_score",
    "simulated_anxiety_score",
    "comfort_score",
}
CALM_ORIENTATION_ASSET_ID = "brain_orientation_calm_educational_v1"
PATIENT_DISPLAY_APPROVED_STATUS = "APPROVED_FOR_PATIENT_EDUCATION"


@dataclass
class ServiceError(Exception):
    status: int
    code: str
    message: str
    field: str | None = None

    def body(self, request_id: str) -> dict[str, Any]:
        error: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.field:
            error["field"] = self.field
        return {"request_id": request_id, "error": error}


class AdaptationService:
    """Pure policy plus a constrained local artifact store."""

    def __init__(self, catalog: AssetCatalog, artifacts: ArtifactStore):
        self.catalog = catalog
        self.artifacts = artifacts
        self._jobs: dict[str, dict[str, Any]] = {}
        self._jobs_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="adaptive-template")
        self._closed = False

    @staticmethod
    def _validate(payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ServiceError(400, "invalid_request", "JSON body must be an object")
        biometric = sorted(set(payload).intersection(BIOMETRIC_FIELDS))
        if biometric:
            raise ServiceError(
                400,
                "biometric_input_not_accepted",
                "This service does not accept pupil, movement, or other biometric data and does not infer anxiety.",
                biometric[0],
            )
        extra = sorted(set(payload).difference(ALLOWED_FIELDS))
        if extra:
            raise ServiceError(400, "unknown_field", "Unknown request field", extra[0])
        missing = sorted({"asset_id", "audience", "mode", "adaptation_source"}.difference(payload))
        if missing:
            raise ServiceError(400, "missing_field", "Required request field is missing", missing[0])
        if not valid_asset_id(payload["asset_id"]):
            raise ServiceError(400, "invalid_asset_id", "asset_id must be a catalog identifier, not a path", "asset_id")
        if not isinstance(payload["audience"], str) or payload["audience"] not in {"patient", "family"}:
            raise ServiceError(400, "invalid_audience", "audience must be patient or family", "audience")
        if not isinstance(payload["mode"], str) or payload["mode"] not in {"auto", "edit", "generate"}:
            raise ServiceError(400, "invalid_mode", "mode must be auto, edit, or generate", "mode")
        if not isinstance(payload["adaptation_source"], str) or payload["adaptation_source"] not in {
            "simulated_demo",
            "self_report_preference",
            "clinician_override",
        }:
            raise ServiceError(
                400,
                "invalid_adaptation_source",
                "adaptation_source must be simulated_demo, self_report_preference, or clinician_override",
                "adaptation_source",
            )
        if "detail_preference" in payload and (
            not isinstance(payload["detail_preference"], str)
            or payload["detail_preference"] not in {
            "simplified",
            "standard",
            "clinical_detail",
            "overview",
            }
        ):
            raise ServiceError(
                400,
                "invalid_detail_preference",
                "detail_preference must be overview, simplified, standard, or clinical_detail",
                "detail_preference",
            )
        motion = payload.get("motion_preference", "system_default")
        if not isinstance(motion, str) or motion not in {"system_default", "reduced", "static"}:
            raise ServiceError(
                400,
                "invalid_motion_preference",
                "motion_preference must be system_default, reduced, or static",
                "motion_preference",
            )
        if payload["adaptation_source"] != "simulated_demo" and "detail_preference" not in payload:
            raise ServiceError(
                400,
                "missing_field",
                "detail_preference is required unless adaptation_source is simulated_demo",
                "detail_preference",
            )
        if payload["adaptation_source"] != "simulated_demo" and "simulation_seed" in payload:
            raise ServiceError(
                400,
                "simulation_seed_not_allowed",
                "simulation_seed is accepted only for simulated_demo requests",
                "simulation_seed",
            )
        if "simulation_seed" in payload:
            seed = payload["simulation_seed"]
            if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= (1 << 63) - 1:
                raise ServiceError(
                    400,
                    "invalid_simulation_seed",
                    "simulation_seed must be an integer from 0 through 2^63-1",
                    "simulation_seed",
                )
        return payload

    def adapt(self, payload: Any, request_id: str) -> tuple[int, dict[str, Any]]:
        data = self._validate(payload)
        asset = self.catalog.get(data["asset_id"])
        if asset is None:
            raise ServiceError(404, "asset_not_found", "asset_id is not present in the configured manifest catalog", "asset_id")

        if "detail_preference" in data:
            preference = data["detail_preference"]
            preference_source = data["adaptation_source"]
        else:
            preference, preference_source = simulate_preference(
                asset.asset_id,
                data["audience"],
                data.get("simulation_seed"),
            )

        resolved_mode = "edit" if data["mode"] == "auto" else data["mode"]
        motion_preference = data.get("motion_preference", "system_default")
        recipe = make_recipe(asset.asset_id, data["audience"], preference, motion_preference)
        calm_fallback = self.catalog.get(CALM_ORIENTATION_ASSET_ID)
        orientation_asset_candidate: dict[str, Any] | None = None
        if preference == "overview" and calm_fallback is not None and asset.asset_id != calm_fallback.asset_id:
            orientation_asset_candidate = {
                "asset_id": calm_fallback.asset_id,
                "role": "orientation_only_candidate",
                "clinical_review_status": calm_fallback.clinical_review_status,
                "display_authorized": False,
                "review_gate": "specialist_and_human_factors_review_required_before_patient_display",
                "co_load_with_source": False,
                "source_asset_remains_available": True,
            }
        fingerprint = recipe_fingerprint(recipe)
        response: dict[str, Any] = {
            "request_id": request_id,
            "adaptation_id": fingerprint[:24],
            "requested_mode": data["mode"],
            "resolved_mode": resolved_mode,
            "source_asset": asset.public_dict(),
            "presentation_preference": {
                "detail_preference": preference,
                "motion_preference": motion_preference,
                "source": preference_source,
                "simulated": data["adaptation_source"] == "simulated_demo",
                "non_diagnostic": True,
                "notice": NON_DIAGNOSTIC_NOTICE,
                "biometric_inputs_used": False,
            },
            "recipe": recipe,
            "recipe_sha256": fingerprint,
        }
        if orientation_asset_candidate is not None:
            response["orientation_asset_candidate"] = orientation_asset_candidate

        if resolved_mode == "edit":
            source_asset_manifest_approved = (
                asset.clinical_review_status.upper() == PATIENT_DISPLAY_APPROVED_STATUS
            )
            response["status"] = "completed"
            response["latency_class"] = "immediate_sidecar"
            response["application_contract"] = {
                "engine": "RealityKit",
                "operation": "apply_recipe_at_runtime",
                "mutates_source_asset": False,
                "fallback_if_semantic_layers_missing": recipe["recommended_fallback"],
                "developer_preview_authorized": True,
                "source_asset_manifest_approved": source_asset_manifest_approved,
                "patient_display_authorized": False,
                "patient_display_review_required": True,
                "required_manifest_status_for_patient_display": PATIENT_DISPLAY_APPROVED_STATUS,
                "required_adaptive_policy_approval": POLICY_VERSION,
                "authorization_notice": (
                    "This prototype cannot authorize patient display. An external governed release must approve "
                    "the exact source asset, semantic entity mapping, and adaptive policy/profile together."
                ),
            }
            return 200, response

        # This queues only a local procedural template. It does not imply that an AI
        # image/model generator is installed, queued, or clinically validated.
        job_material = json.dumps(
            {"asset_id": asset.asset_id, "audience": data["audience"], "recipe": fingerprint},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        job_id = hashlib.sha256(job_material).hexdigest()[:24]
        job = {
            "job_id": job_id,
            "status": "queued",
            "generator": "local_procedural_comfort_template_v1",
            "generator_kind": "deterministic_non_ai_template",
            "model_provider": None,
            "source_asset_mutated": False,
            "display_authorized": False,
            "review_gate": "clinician_review_required_before_display",
            "artifact_role": "abstract_procedural_review_draft",
            "limitations": [
                "The USDA is an abstract orientation scene, not generated anatomy.",
                "It must not replace the clinician-reviewed source in clinical workflows.",
                "No external model provider or generative-AI queue was invoked.",
            ],
        }
        if orientation_asset_candidate is not None:
            job["orientation_asset_candidate"] = orientation_asset_candidate
        with self._jobs_lock:
            existing = self._jobs.get(job_id)
            if existing is None:
                self._jobs[job_id] = job
            else:
                job = dict(existing)
        if existing is None:
            self._executor.submit(
                self._materialize_job,
                job_id,
                asset.asset_id,
                asset.title,
                recipe,
                fingerprint,
            )
        response["status"] = "accepted"
        response["generation_contract"] = job
        return 202, response

    def _materialize_job(
        self,
        job_id: str,
        asset_id: str,
        title: str,
        recipe: dict[str, Any],
        fingerprint: str,
    ) -> None:
        try:
            artifacts = self.artifacts.materialize(
                job_id,
                asset_id,
                title,
                recipe["adaptation_tier"],
                recipe,
                fingerprint,
            )
            with self._jobs_lock:
                if job_id in self._jobs:
                    self._jobs[job_id] = {
                        **self._jobs[job_id],
                        "status": "awaiting_clinician_review",
                        "draft_artifacts": artifacts,
                    }
        except Exception:
            with self._jobs_lock:
                if job_id in self._jobs:
                    self._jobs[job_id] = {**self._jobs[job_id], "status": "failed"}

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._jobs_lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def close(self) -> None:
        """Finish in-flight local writes before the runtime output is released."""
        with self._jobs_lock:
            if self._closed:
                return
            self._closed = True
        self._executor.shutdown(wait=True, cancel_futures=False)
