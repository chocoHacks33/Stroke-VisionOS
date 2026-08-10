#!/usr/bin/env python3
"""Validate the Interaction Feedback manifest, WAV files, and reproducibility."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


EXPECTED_IDS = {
    "focus",
    "selection",
    "confirm",
    "back",
    "warning",
    "transition",
    "restore",
}
EXPECTED_AMBIENCE_IDS = {"soft_water_rain"}


class ValidationFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dbfs(linear_value: float) -> float:
    return 20.0 * math.log10(max(linear_value, 1.0e-12))


def read_pcm_metrics(path: Path, *, require_silent_edges: bool) -> dict[str, float | int]:
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        sample_rate = source.getframerate()
        frame_count = source.getnframes()
        compression = source.getcomptype()
        raw_frames = source.readframes(frame_count)

    require(channels == 1, f"{path.name}: expected mono, found {channels} channels")
    require(sample_width == 2, f"{path.name}: expected 16-bit PCM")
    require(sample_rate == 48_000, f"{path.name}: expected 48 kHz, found {sample_rate}")
    require(compression == "NONE", f"{path.name}: expected uncompressed PCM")
    require(len(raw_frames) == frame_count * 2, f"{path.name}: truncated PCM payload")

    samples = struct.unpack(f"<{frame_count}h", raw_frames)
    normalized = [sample / 32_768.0 for sample in samples]
    peak = max(abs(value) for value in normalized)
    rms = math.sqrt(sum(value * value for value in normalized) / frame_count)
    dc_offset = abs(sum(normalized) / frame_count)
    internal_deltas = [normalized[index] - normalized[index - 1] for index in range(1, frame_count)]
    delta_rms = math.sqrt(sum(value * value for value in internal_deltas) / len(internal_deltas))
    seam_delta = normalized[0] - normalized[-1]
    incoming_delta = normalized[-1] - normalized[-2]
    outgoing_delta = normalized[1] - normalized[0]
    seam_slope_mismatch = max(abs(seam_delta - incoming_delta), abs(outgoing_delta - seam_delta))

    if require_silent_edges:
        require(samples[0] == 0 and samples[-1] == 0, f"{path.name}: first/last samples must be silent")
    require(peak < 1.0, f"{path.name}: clipped sample detected")
    require(dc_offset <= 0.001, f"{path.name}: excessive DC offset {dc_offset:.6f}")

    return {
        "sample_rate": sample_rate,
        "channels": channels,
        "bits_per_sample": sample_width * 8,
        "frame_count": frame_count,
        "duration_ms": frame_count / sample_rate * 1000.0,
        "peak_dbfs": dbfs(peak),
        "rms_dbfs": dbfs(rms),
        "dc_offset": dc_offset,
        "delta_rms": delta_rms,
        "seam_delta": abs(seam_delta),
        "seam_slope_mismatch": seam_slope_mismatch,
    }


def validate_manifest(package_root: Path) -> tuple[dict, list[dict]]:
    manifest_path = package_root / "feedback_manifest_v1.json"
    require(manifest_path.is_file(), f"Missing manifest: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as source:
        manifest = json.load(source)

    require(manifest.get("schema_version") == "1.0.0", "Unexpected manifest schema")
    require(manifest.get("package_version") == "1.1.0", "Unexpected feedback package version")
    audio_format = manifest.get("format", {})
    require(audio_format.get("container") == "wav", "Manifest must declare WAV")
    require(audio_format.get("codec") == "linear_pcm", "Manifest must declare linear PCM")
    require(audio_format.get("sample_rate_hz") == 48_000, "Manifest sample rate must be 48 kHz")
    require(audio_format.get("channels") == 1, "Manifest audio must be mono")
    require(audio_format.get("bits_per_sample") == 16, "Manifest audio must be 16-bit")

    policy = manifest.get("playback_policy", {})
    require(0.0 <= policy.get("default_master_gain", 2.0) <= 0.5, "Default master gain must be conservative")
    require(policy.get("master_gain_is_user_adjustable") is True, "Master gain must remain user-adjustable")
    require(policy.get("respects_app_mute") is True, "App mute must be respected")
    require(policy.get("respects_system_volume") is True, "System volume must be respected")
    require(policy.get("spatialization") == "non_spatial_ui", "UI cues must remain non-spatial")
    require(policy.get("continuous_motion_audio") is False, "Continuous motion audio must be disabled")
    require(policy.get("raw_gaze_audio") is False, "Raw gaze audio must be disabled")
    require(policy.get("maximum_simultaneous_earcons", 99) <= 2, "Too many simultaneous earcons")
    require(policy.get("headset_haptic_assumed") is False, "Headset haptics must not be assumed")
    require(policy.get("external_haptic_default_enabled") is False, "External haptics must default off")

    ambience_policy = manifest.get("ambience_policy", {})
    require(ambience_policy.get("default_enabled") is False, "Ambience must default off")
    require(ambience_policy.get("independent_volume_control") is True, "Ambience requires independent volume")
    require(0.0 <= ambience_policy.get("default_gain", 2.0) <= 0.3, "Ambience default gain is too high")
    require(
        ambience_policy.get("default_gain", 2.0) <= ambience_policy.get("maximum_gain", -1.0) <= 0.5,
        "Ambience maximum gain is invalid",
    )
    require(ambience_policy.get("respects_app_mute") is True, "Ambience must respect app mute")
    require(ambience_policy.get("respects_system_volume") is True, "Ambience must respect system volume")
    require(
        ambience_policy.get("presentation") == "diffuse_non_directional_background",
        "Ambience must remain diffuse and non-directional",
    )
    require(ambience_policy.get("attached_to_anatomy") is False, "Ambience must not attach to anatomy")
    require(ambience_policy.get("controlled_by_comfort_slider") is False, "Ambience must be an explicit preference")
    require(ambience_policy.get("maximum_simultaneous_ambience_loops") == 1, "Only one ambience loop is allowed")
    require(int(ambience_policy.get("fade_in_ms", 0)) >= 1000, "Ambience fade-in is too abrupt")
    require(int(ambience_policy.get("fade_out_ms", 0)) >= 750, "Ambience fade-out is too abrupt")
    require(float(ambience_policy.get("duck_under_warning_db", 1.0)) <= -3.0, "Warning must remain intelligible")
    require(ambience_policy.get("therapeutic_claim") is False, "Ambience must not carry a therapeutic claim")

    haptic_relative_path = Path(manifest.get("external_haptic_recipe_file", ""))
    require(
        haptic_relative_path == Path("Haptics/external_haptic_intents_v1.json"),
        "Unexpected external haptic recipe path",
    )
    haptic_path = package_root / haptic_relative_path
    require(haptic_path.is_file(), f"Missing external haptic recipe: {haptic_path}")
    with haptic_path.open("r", encoding="utf-8") as source:
        haptic_contract = json.load(source)
    require(haptic_contract.get("target") == "optional_supported_external_adapter_only", "Unsafe haptic target")
    require(haptic_contract.get("vision_pro_headset_haptic_assumed") is False, "Headset haptic must not be assumed")
    require(haptic_contract.get("default_enabled") is False, "External haptic contract must default off")
    require(haptic_contract.get("requires_explicit_user_opt_in") is True, "External haptic requires opt-in")
    require(haptic_contract.get("requires_runtime_capability_check") is True, "External haptic requires capability check")
    require(haptic_contract.get("continuous_motion_feedback") is False, "Continuous haptic motion feedback is forbidden")
    haptic_intents = haptic_contract.get("intents", [])
    haptic_identifiers = {intent.get("id") for intent in haptic_intents}
    require(
        haptic_identifiers
        == {
            "light_selection_transient",
            "soft_confirmation_transient",
            "light_navigation_transient",
            "attention_transient",
        },
        "External haptic intent membership mismatch",
    )
    require(
        all(1 <= int(intent.get("transient_count", 0)) <= 2 for intent in haptic_intents),
        "External haptic intents must remain brief",
    )
    haptic_intent_by_id = {intent["id"]: intent for intent in haptic_intents}

    earcons = manifest.get("earcons", [])
    require(len(earcons) == len(EXPECTED_IDS), f"Expected {len(EXPECTED_IDS)} earcons")
    identifiers = [earcon.get("id") for earcon in earcons]
    require(set(identifiers) == EXPECTED_IDS, f"Unexpected earcon IDs: {identifiers}")
    require(len(identifiers) == len(set(identifiers)), "Earcon IDs must be unique")

    declared_files: set[Path] = set()
    metrics: list[dict] = []
    for earcon in earcons:
        identifier = earcon["id"]
        relative_path = Path(earcon["file"])
        require(not relative_path.is_absolute() and ".." not in relative_path.parts, f"{identifier}: unsafe path")
        audio_path = package_root / relative_path
        require(audio_path.is_file(), f"{identifier}: missing {relative_path}")
        require(relative_path.suffix.lower() == ".wav", f"{identifier}: expected .wav")
        declared_files.add(relative_path)

        require(audio_path.stat().st_size == earcon["bytes"], f"{identifier}: byte count mismatch")
        require(sha256(audio_path) == earcon["sha256"], f"{identifier}: SHA-256 mismatch")
        require(-12.0 >= float(earcon["peak_ceiling_dbfs"]) >= -30.0, f"{identifier}: unsafe peak ceiling")
        require(float(earcon["gain_trim_db"]) <= 0.0, f"{identifier}: gain trim must not boost")
        require(int(earcon["cooldown_ms"]) >= 80, f"{identifier}: cooldown is too short")
        haptic_intent_id = earcon.get("external_haptic_intent")
        if haptic_intent_id is not None:
            require(haptic_intent_id in haptic_intent_by_id, f"{identifier}: unknown external haptic intent")
            haptic_intent = haptic_intent_by_id[haptic_intent_id]
            require(earcon["event"] in haptic_intent["allowed_events"], f"{identifier}: haptic event mismatch")
            require(
                int(haptic_intent["minimum_interval_ms"]) >= int(earcon["cooldown_ms"]),
                f"{identifier}: haptic interval cannot be shorter than audio cooldown",
            )

        measured = read_pcm_metrics(audio_path, require_silent_edges=True)
        require(abs(measured["duration_ms"] - earcon["duration_ms"]) <= 0.1, f"{identifier}: duration mismatch")
        require(40.0 <= measured["duration_ms"] <= 500.0, f"{identifier}: duration is outside UI-cue bounds")
        require(measured["peak_dbfs"] <= earcon["peak_ceiling_dbfs"], f"{identifier}: exceeds declared peak ceiling")
        require(-36.0 <= measured["peak_dbfs"] <= -12.0, f"{identifier}: peak level outside conservative bounds")
        require(-60.0 <= measured["rms_dbfs"] <= -23.0, f"{identifier}: RMS level outside conservative bounds")
        metrics.append({"id": identifier, **measured, "sha256": earcon["sha256"]})

    ambiences = manifest.get("ambiences", [])
    require(len(ambiences) == len(EXPECTED_AMBIENCE_IDS), "Expected exactly one ambience")
    ambience_identifiers = [ambience.get("id") for ambience in ambiences]
    require(set(ambience_identifiers) == EXPECTED_AMBIENCE_IDS, "Unexpected ambience IDs")
    for ambience in ambiences:
        identifier = ambience["id"]
        relative_path = Path(ambience["file"])
        require(not relative_path.is_absolute() and ".." not in relative_path.parts, f"{identifier}: unsafe path")
        audio_path = package_root / relative_path
        require(audio_path.is_file(), f"{identifier}: missing {relative_path}")
        require(relative_path.suffix.lower() == ".wav", f"{identifier}: expected .wav")
        declared_files.add(relative_path)

        require(audio_path.stat().st_size == ambience["bytes"], f"{identifier}: byte count mismatch")
        require(sha256(audio_path) == ambience["sha256"], f"{identifier}: SHA-256 mismatch")
        require(ambience.get("default_enabled") is False, f"{identifier}: ambience must default off")
        require(ambience.get("loops") is True, f"{identifier}: ambience must be declared as a loop")
        require(ambience.get("seamless_loop_required") is True, f"{identifier}: seamless-loop contract missing")
        require(ambience.get("user_volume_is_independent") is True, f"{identifier}: independent volume missing")

        measured = read_pcm_metrics(audio_path, require_silent_edges=False)
        require(abs(measured["duration_ms"] - ambience["duration_ms"]) <= 0.1, f"{identifier}: duration mismatch")
        require(8000.0 <= measured["duration_ms"] <= 20000.0, f"{identifier}: loop duration is out of bounds")
        require(measured["peak_dbfs"] <= ambience["peak_ceiling_dbfs"], f"{identifier}: exceeds peak ceiling")
        require(-30.0 <= measured["peak_dbfs"] <= -18.0, f"{identifier}: peak level is not low-level")
        require(-55.0 <= measured["rms_dbfs"] <= -28.0, f"{identifier}: RMS level is not low-level")
        quantization_floor = 2.0 / 32_768.0
        require(
            measured["seam_delta"] <= max(quantization_floor, measured["delta_rms"] * 0.25),
            f"{identifier}: loop-boundary sample jump is too large",
        )
        require(
            measured["seam_slope_mismatch"] <= max(quantization_floor * 2.0, measured["delta_rms"] * 1.5),
            f"{identifier}: loop-boundary slope mismatch is too large",
        )
        metrics.append({"id": identifier, "kind": "ambience", **measured, "sha256": ambience["sha256"]})

    actual_files = {path.relative_to(package_root) for path in (package_root / "Audio").glob("*.wav")}
    require(actual_files == declared_files, f"Manifest/audio membership mismatch: declared={declared_files}, actual={actual_files}")
    return manifest, metrics


def validate_regeneration(package_root: Path, generator_path: Path, manifest: dict) -> None:
    require(generator_path.is_file(), f"Missing generator: {generator_path}")
    with tempfile.TemporaryDirectory(prefix="stroke-earcon-validation-") as temporary_directory:
        generated_root = Path(temporary_directory)
        result = subprocess.run(
            [sys.executable, str(generator_path), "--output", str(generated_root)],
            check=False,
            capture_output=True,
            text=True,
        )
        require(result.returncode == 0, f"Generator failed:\n{result.stdout}\n{result.stderr}")
        for audio_record in manifest["earcons"] + manifest["ambiences"]:
            generated_path = generated_root / Path(audio_record["file"]).name
            require(generated_path.is_file(), f"Generator omitted {generated_path.name}")
            require(
                sha256(generated_path) == audio_record["sha256"],
                f"Regeneration mismatch for {generated_path.name}",
            )


def main() -> None:
    script_directory = Path(__file__).resolve().parent
    app_root = script_directory.parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-root",
        type=Path,
        default=app_root / "Resources" / "InteractionFeedback",
    )
    parser.add_argument(
        "--generator",
        type=Path,
        default=script_directory / "generate_earcons.py",
    )
    parser.add_argument("--skip-regeneration", action="store_true")
    arguments = parser.parse_args()

    try:
        manifest, metrics = validate_manifest(arguments.package_root.resolve())
        if not arguments.skip_regeneration:
            validate_regeneration(arguments.package_root.resolve(), arguments.generator.resolve(), manifest)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, ValidationFailure) as error:
        print(f"INTERACTION_FEEDBACK_VALIDATION_FAILED: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    for metric in metrics:
        message = (
            "VALIDATED "
            f"{metric['id']}: {metric['duration_ms']:.0f}ms, "
            f"peak={metric['peak_dbfs']:.2f}dBFS, "
            f"rms={metric['rms_dbfs']:.2f}dBFS, "
            f"dc={metric['dc_offset']:.6f}"
        )
        if metric.get("kind") == "ambience":
            message += (
                f", seam={metric['seam_delta']:.8f}, "
                f"seam_slope={metric['seam_slope_mismatch']:.8f}"
            )
        print(message)
    print(
        "INTERACTION_FEEDBACK_VALIDATION_PASSED: "
        f"{len(EXPECTED_IDS)} earcons + {len(EXPECTED_AMBIENCE_IDS)} ambience; "
        "deterministic regeneration matched"
    )


if __name__ == "__main__":
    main()
