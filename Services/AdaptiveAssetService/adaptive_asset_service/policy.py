"""Deterministic, non-clinical presentation policy."""

from __future__ import annotations

import hashlib
import json
import secrets
from typing import Any


POLICY_VERSION = "presentation-preference-v1"
NON_DIAGNOSTIC_NOTICE = (
    "This is a presentation preference, not a measurement, diagnosis, or medical assessment. "
    "No pupil, motion, or other biometric inference is performed."
)


def simulate_preference(asset_id: str, audience: str, seed: int | None) -> tuple[str, str]:
    """Select a demo preference; seeded runs are exactly reproducible."""
    if seed is None:
        raw = secrets.randbelow(4)
        source = "random_simulation"
    else:
        material = f"{seed}:{asset_id}:{audience}:{POLICY_VERSION}".encode("utf-8")
        raw = int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % 4
        source = "deterministic_seeded_simulation"
    return ("overview", "simplified", "standard", "clinical_detail")[raw], source


def tier_for_preference(preference: str) -> tuple[str, int]:
    return {
        "clinical_detail": ("clinical_detail", 0),
        "standard": ("standard", 1),
        "simplified": ("simplified", 2),
        "overview": ("overview", 3),
    }[preference]


def _tier_values(level: int) -> dict[str, Any]:
    detail = ("full", "balanced", "essential", "minimal")[level]
    visible = (
        ["orientation", "anatomy_primary", "anatomy_secondary", "flow", "device", "labels"],
        ["orientation", "anatomy_primary", "flow", "device", "labels"],
        ["orientation", "anatomy_primary", "device", "labels"],
        ["orientation", "anatomy_primary", "labels"],
    )[level]
    hidden = (
        [],
        ["micro_detail"],
        ["micro_detail", "secondary_vessels", "incision_detail", "free_particles"],
        [
            "micro_detail",
            "secondary_vessels",
            "incision_detail",
            "free_particles",
            "blood_cells",
            "surgical_field",
            "instrument_motion",
        ],
    )[level]
    return {
        "detail": {
            "level": detail,
            "lod_bias": (0, 0, 1, 2)[level],
            "visible_layer_groups": visible,
            "hidden_layer_groups": hidden,
            "layer_match_behavior": "semantic_best_effort",
        },
        "materials": {
            "tint_rgba": (
                [0.96, 0.98, 1.0, 1.0],
                [0.91, 0.95, 0.98, 1.0],
                [0.85, 0.92, 0.95, 1.0],
                [0.80, 0.90, 0.93, 1.0],
            )[level],
            "saturation_multiplier": (1.0, 0.84, 0.68, 0.52)[level],
            "roughness_floor": (0.35, 0.42, 0.50, 0.58)[level],
            "specular_multiplier": (1.0, 0.85, 0.70, 0.55)[level],
            "blood_tone": ("source", "muted_crimson", "muted_rose", "soft_rose")[level],
            "preserve_legend": True,
        },
        "opacity": {
            "primary_anatomy": (1.0, 1.0, 0.96, 0.92)[level],
            "secondary_anatomy": (0.92, 0.78, 0.55, 0.25)[level],
            "blood_and_particles": (1.0, 0.75, 0.42, 0.0)[level],
        },
        "motion": {
            "autoplay": level < 2,
            "speed_multiplier": (1.0, 0.75, 0.50, 0.30)[level],
            "looping": level == 0,
            "allow_user_pause": True,
            "reduce_sudden_camera_motion": level >= 1,
        },
        "annotations": {
            "density": ("detailed", "guided", "essential", "single_focus")[level],
            "maximum_visible_labels": (12, 7, 4, 2)[level],
            "plain_language": True,
            "show_progressive_disclosure_control": True,
        },
        "pacing": {
            "minimum_seconds_per_step": (4, 6, 9, 12)[level],
            "transition_seconds": (0.35, 0.55, 0.80, 1.10)[level],
            "pause_between_steps": level >= 1,
            "confirm_before_procedure_detail": level >= 2,
        },
    }


def make_recipe(asset_id: str, audience: str, preference: str, motion_preference: str) -> dict[str, Any]:
    tier, level = tier_for_preference(preference)
    recipe = {
        "schema_version": "1.0",
        "policy_version": POLICY_VERSION,
        "asset_id": asset_id,
        "audience": audience,
        "adaptation_tier": tier,
        **_tier_values(level),
        "comfort_controls": {
            "reduce_detail_available": True,
            "increase_detail_available": True,
            "restore_source_available": True,
            "stop_or_pause_available": True,
            "exit_or_return_available": True,
            "clinician_controlled_reveal": level >= 2,
        },
        "recommended_fallback": (
            "source_asset_with_legend"
            if level == 0
            else "static_orientation_card"
            if level < 3
            else "plain_language_2d_summary"
        ),
        "warnings": [
            "Patient/family education only; do not use this rendering for diagnosis, planning, navigation, or consent by itself.",
            "Material and visibility changes can alter perceived anatomy; preserve an immediate path to the unmodified source and its legend.",
            "A clinician or trained facilitator must review medical content and decide what to reveal.",
        ],
        "transparency": {
            "adaptation_badge_required": True,
            "show_changed_properties": True,
            "one_action_restore_source": True,
            "source_medical_content_remains_available": True,
        },
    }
    if audience == "family":
        recipe["annotations"]["caregiver_context"] = True
        recipe["family_access"] = {
            "patient_participation_or_authorization_confirmation_required": True,
            "privacy_confirmation_required": True,
            "may_exceed_patient_authorized_detail": False,
            "notice": "Family presentation must follow the patient's participation, authorization, and privacy choices.",
        }
    recipe["motion"]["preference"] = motion_preference
    if motion_preference == "reduced":
        recipe["motion"].update(
            {
                "autoplay": False,
                "speed_multiplier": min(recipe["motion"]["speed_multiplier"], 0.5),
                "looping": False,
                "reduce_sudden_camera_motion": True,
            }
        )
    elif motion_preference == "static":
        recipe["motion"].update(
            {
                "autoplay": False,
                "speed_multiplier": 0.0,
                "looping": False,
                "reduce_sudden_camera_motion": True,
                "select_representative_frame": True,
            }
        )
    return recipe


def recipe_fingerprint(recipe: dict[str, Any]) -> str:
    packed = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(packed).hexdigest()
