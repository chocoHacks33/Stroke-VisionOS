#!/usr/bin/env python3
"""Generate the original Stroke Care interaction audio deterministically.

The generator uses only the Python standard library. It deliberately produces
short, conservative-level PCM earcons plus one optional seamless procedural
water/rain ambience. No recorded, sampled, or third-party material is used.
"""

from __future__ import annotations

import argparse
import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


SAMPLE_RATE = 48_000
PCM_MAX = 32_767
AMBIENCE_FILENAME = "soft_water_rain_loop.wav"
AMBIENCE_DURATION_SECONDS = 12.0
AMBIENCE_TARGET_PEAK_DBFS = -22.0


@dataclass(frozen=True)
class EarconSpec:
    filename: str
    duration_seconds: float
    target_peak_dbfs: float
    synthesize: Callable[[list[float]], None]


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def envelope(local_time: float, duration: float, attack: float, release: float) -> float:
    if local_time < 0.0 or local_time >= duration:
        return 0.0
    attack_gain = smoothstep(local_time / max(attack, 1.0 / SAMPLE_RATE))
    release_gain = smoothstep((duration - local_time) / max(release, 1.0 / SAMPLE_RATE))
    return min(attack_gain, release_gain)


def add_chirp(
    samples: list[float],
    *,
    start: float,
    duration: float,
    frequency_start: float,
    frequency_end: float,
    amplitude: float,
    attack: float = 0.008,
    release: float = 0.045,
    overtone: float = 0.08,
) -> None:
    first = max(0, round(start * SAMPLE_RATE))
    last = min(len(samples), round((start + duration) * SAMPLE_RATE))
    phase = 0.0
    for index in range(first, last):
        local_time = (index - first) / SAMPLE_RATE
        progress = local_time / max(duration, 1.0 / SAMPLE_RATE)
        frequency = frequency_start * ((frequency_end / frequency_start) ** progress)
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE
        gain = envelope(local_time, duration, attack, release)
        fundamental = math.sin(phase)
        harmonic = math.sin(phase * 2.0 + 0.2)
        samples[index] += amplitude * gain * (fundamental + overtone * harmonic)


def add_soft_noise_swell(
    samples: list[float],
    *,
    start: float,
    duration: float,
    amplitude: float,
    seed: int,
) -> None:
    first = max(0, round(start * SAMPLE_RATE))
    last = min(len(samples), round((start + duration) * SAMPLE_RATE))
    state = seed & 0x7FFFFFFF
    low_pass = 0.0
    for index in range(first, last):
        state = (1_103_515_245 * state + 12_345) & 0x7FFFFFFF
        white = (state / 0x7FFFFFFF) * 2.0 - 1.0
        low_pass += 0.055 * (white - low_pass)
        local_time = (index - first) / SAMPLE_RATE
        gain = envelope(local_time, duration, 0.055, 0.12)
        samples[index] += amplitude * gain * low_pass


def synthesize_focus(samples: list[float]) -> None:
    add_chirp(
        samples,
        start=0.0,
        duration=0.060,
        frequency_start=690.0,
        frequency_end=760.0,
        amplitude=1.0,
        attack=0.006,
        release=0.032,
        overtone=0.04,
    )


def synthesize_selection(samples: list[float]) -> None:
    add_chirp(
        samples,
        start=0.0,
        duration=0.110,
        frequency_start=510.0,
        frequency_end=650.0,
        amplitude=1.0,
        attack=0.007,
        release=0.055,
        overtone=0.06,
    )


def synthesize_confirm(samples: list[float]) -> None:
    add_chirp(samples, start=0.000, duration=0.150, frequency_start=392.0, frequency_end=415.0, amplitude=0.64)
    add_chirp(samples, start=0.055, duration=0.155, frequency_start=493.88, frequency_end=523.25, amplitude=0.56)
    add_chirp(samples, start=0.110, duration=0.130, frequency_start=587.33, frequency_end=659.25, amplitude=0.46)


def synthesize_back(samples: list[float]) -> None:
    add_chirp(
        samples,
        start=0.0,
        duration=0.150,
        frequency_start=620.0,
        frequency_end=440.0,
        amplitude=1.0,
        attack=0.008,
        release=0.065,
        overtone=0.04,
    )


def synthesize_warning(samples: list[float]) -> None:
    add_chirp(samples, start=0.000, duration=0.180, frequency_start=380.0, frequency_end=350.0, amplitude=0.72, release=0.085)
    add_chirp(samples, start=0.115, duration=0.195, frequency_start=320.0, frequency_end=295.0, amplitude=0.68, release=0.095)
    add_chirp(samples, start=0.000, duration=0.310, frequency_start=261.63, frequency_end=246.94, amplitude=0.14, attack=0.035, release=0.100, overtone=0.0)


def synthesize_transition(samples: list[float]) -> None:
    add_soft_noise_swell(samples, start=0.0, duration=0.400, amplitude=0.70, seed=0x5354524B)
    add_chirp(samples, start=0.040, duration=0.330, frequency_start=300.0, frequency_end=450.0, amplitude=0.34, attack=0.060, release=0.130, overtone=0.02)


def synthesize_restore(samples: list[float]) -> None:
    add_chirp(samples, start=0.000, duration=0.145, frequency_start=392.0, frequency_end=415.0, amplitude=0.55)
    add_chirp(samples, start=0.055, duration=0.155, frequency_start=493.88, frequency_end=523.25, amplitude=0.49)
    add_chirp(samples, start=0.115, duration=0.145, frequency_start=587.33, frequency_end=622.25, amplitude=0.43)


EARCONS = (
    EarconSpec("focus.wav", 0.060, -24.0, synthesize_focus),
    EarconSpec("selection.wav", 0.110, -21.0, synthesize_selection),
    EarconSpec("confirm.wav", 0.240, -18.0, synthesize_confirm),
    EarconSpec("back.wav", 0.150, -21.0, synthesize_back),
    EarconSpec("warning.wav", 0.310, -18.0, synthesize_warning),
    EarconSpec("transition.wav", 0.400, -22.0, synthesize_transition),
    EarconSpec("restore.wav", 0.260, -19.0, synthesize_restore),
)


def circular_moving_average(samples: list[float], radius: int) -> list[float]:
    """Return a moving average whose window wraps around the loop boundary."""
    if radius <= 0:
        return samples.copy()
    sample_count = len(samples)
    window_size = radius * 2 + 1
    running_total = sum(samples[index % sample_count] for index in range(-radius, radius + 1))
    averaged = [0.0] * sample_count
    averaged[0] = running_total / window_size
    for index in range(1, sample_count):
        leaving_index = (index - radius - 1) % sample_count
        entering_index = (index + radius) % sample_count
        running_total += samples[entering_index] - samples[leaving_index]
        averaged[index] = running_total / window_size
    return averaged


def rotate_to_quiet_seam(samples: list[float]) -> list[float]:
    """Choose an existing, smooth circular transition as the file boundary."""
    sample_count = len(samples)
    best_index = 0
    best_score = math.inf
    for index in range(sample_count):
        previous = (index - 1) % sample_count
        previous_previous = (index - 2) % sample_count
        following = (index + 1) % sample_count
        seam_slope = samples[index] - samples[previous]
        incoming_slope = samples[previous] - samples[previous_previous]
        outgoing_slope = samples[following] - samples[index]
        score = (
            abs(seam_slope) * 2.0
            + abs(seam_slope - incoming_slope)
            + abs(outgoing_slope - seam_slope)
        )
        if score < best_score:
            best_score = score
            best_index = index
    return samples[best_index:] + samples[:best_index]


def synthesize_soft_water_rain_loop(sample_count: int) -> list[float]:
    """Create a periodic, diffuse water/rain texture without samples or loops."""
    state = 0x57415452
    white_noise = [0.0] * sample_count
    for index in range(sample_count):
        state = (1_103_515_245 * state + 12_345) & 0x7FFFFFFF
        white_noise[index] = (state / 0x7FFFFFFF) * 2.0 - 1.0

    fine = circular_moving_average(white_noise, radius=2)
    medium = circular_moving_average(white_noise, radius=24)
    broad = circular_moving_average(white_noise, radius=480)
    texture = [0.0] * sample_count
    phase_a = 0.37
    phase_b = 1.91
    for index in range(sample_count):
        normalized_time = index / sample_count
        soft_rain = fine[index] - medium[index]
        water_body = medium[index] - broad[index]
        slow_wash = broad[index]
        periodic_swell = (
            0.045 * math.sin(2.0 * math.pi * 3.0 * normalized_time + phase_a)
            + 0.025 * math.sin(2.0 * math.pi * 7.0 * normalized_time + phase_b)
        )
        texture[index] = 0.32 * soft_rain + 0.86 * water_body + 0.60 * slow_wash + periodic_swell

    mean = sum(texture) / sample_count
    centered = [sample - mean for sample in texture]
    return rotate_to_quiet_seam(centered)


def normalize(samples: list[float], target_peak_dbfs: float, *, silent_edges: bool = True) -> list[int]:
    measured_peak = max(abs(value) for value in samples)
    if measured_peak <= 0.0:
        raise ValueError("Synthesizer produced silence")
    target_linear = 10.0 ** (target_peak_dbfs / 20.0)
    scale = target_linear / measured_peak
    pcm = [max(-PCM_MAX, min(PCM_MAX, round(value * scale * PCM_MAX))) for value in samples]
    if silent_edges:
        pcm[0] = 0
        pcm[-1] = 0
    return pcm


def write_wave(path: Path, pcm: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.setcomptype("NONE", "not compressed")
        output.writeframes(struct.pack(f"<{len(pcm)}h", *pcm))


def generate(output_directory: Path) -> None:
    for spec in EARCONS:
        sample_count = round(spec.duration_seconds * SAMPLE_RATE)
        floating_samples = [0.0] * sample_count
        spec.synthesize(floating_samples)
        write_wave(output_directory / spec.filename, normalize(floating_samples, spec.target_peak_dbfs))
        print(f"GENERATED {spec.filename} frames={sample_count} target_peak_dbfs={spec.target_peak_dbfs:.1f}")

    ambience_sample_count = round(AMBIENCE_DURATION_SECONDS * SAMPLE_RATE)
    ambience = synthesize_soft_water_rain_loop(ambience_sample_count)
    ambience_pcm = normalize(ambience, AMBIENCE_TARGET_PEAK_DBFS, silent_edges=False)
    write_wave(output_directory / AMBIENCE_FILENAME, ambience_pcm)
    print(
        f"GENERATED {AMBIENCE_FILENAME} frames={ambience_sample_count} "
        f"target_peak_dbfs={AMBIENCE_TARGET_PEAK_DBFS:.1f} seamless_loop=true"
    )


def main() -> None:
    script_directory = Path(__file__).resolve().parent
    default_output = script_directory.parent.parent / "Resources" / "InteractionFeedback" / "Audio"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=default_output)
    arguments = parser.parse_args()
    generate(arguments.output.resolve())


if __name__ == "__main__":
    main()
