# Interaction Feedback asset pack

This directory contains seven original, short UI earcons, one optional
procedural water/rain ambience loop, and declarative playback contracts for the
Stroke Care Immersive developer preview. The pack is wired through the
application's `InteractionFeedbackController`: the target preloads the files,
enforces cooldown/priority/voice limits, and exposes persistent independent
settings without changing anatomical geometry or clinical state.

## Included cues

| ID | Intended trigger | Duration | Default behavior |
|---|---|---:|---|
| `focus` | Deliberate focus-boundary entry | 60 ms | Off; opt-in and heavily debounced |
| `selection` | Committed button or pinch | 110 ms | On |
| `confirm` | Confirmed reversible state change | 240 ms | On |
| `back` | Back, dismiss, or return | 150 ms | On |
| `warning` | Blocked or confirmation-required UI action | 310 ms | On; one-second cooldown |
| `transition` | Infrequent major view transition | 400 ms | On; never looped |
| `restore` | User-requested restore completes | 260 ms | On |

Every file is mono 48 kHz / 16-bit linear PCM WAV. Source peaks range from
-24 dBFS to -18 dBFS, then each recipe applies an additional -3 to -5 dB trim
and a default 0.35 master gain. Runtime integration must keep the master gain
user-adjustable and respect app mute and system volume.

## Optional ambience

`soft_water_rain_loop.wav` is a 12-second, seamless, procedurally synthesized
water/rain texture. It uses no field recording or third-party loop. Its source
peak is -22 dBFS and measured RMS is approximately -34.9 dBFS.

- It is **off by default** and only starts after an explicit user choice.
- It has an independent ambience-volume setting: default `0.25`, capped at
  `0.5`, with complete muting available.
- Enable and disable operations use 1.5-second and 1-second fades. The runtime
  should duck it by 6 dB while the warning earcon plays.
- It is diffuse and non-directional, never attached to anatomy, locomotion,
  head motion, procedural state, or the comfort/detail slider.
- A nature-like sound option is included as a preference because users can
  respond differently to environmental audio. It is not treatment, does not
  measure or infer anxiety, and carries no anxiety-reduction claim.

## Interaction boundaries

- Do not play sounds for continuous head, hand, pointer, or scene movement.
- Do not convert raw gaze updates into audio. `focus` is only for a stable,
  deliberate focus boundary and is disabled by default.
- Prefer visionOS system controls and system hover/press affordances. The pack
  supplements committed actions; it does not imitate protected system sounds.
- Keep UI earcons non-spatial. Do not place them on moving anatomy or in the
  environment, which could imply that a UI state has an anatomical location.
- `warning` is interface feedback only. It must never represent a medical
  alarm, diagnosis, patient status, or clinical urgency.
- No cue is described or evaluated as reducing anxiety. Comfort is individual;
  users must be able to lower or mute feedback without losing information.

## Haptic boundary

This pack does **not** assume headset haptic hardware and does not include a
visionOS haptic implementation. `Haptics/external_haptic_intents_v1.json` and
the Swift recipe file expose optional semantic intents for a future supported
companion/accessory adapter. They are not AHAP patterns or hardware amplitudes.
That channel defaults off, requires explicit user opt-in and a runtime
capability check, and must preserve an equivalent visual/audio path when
unavailable.

## Regenerate and validate

Run from the repository root:

```bash
python3 Apps/StrokeImmersiveExperience/Scripts/InteractionFeedback/generate_earcons.py
python3 Apps/StrokeImmersiveExperience/Scripts/InteractionFeedback/validate_earcons.py
```

Generation is deterministic. The validator checks manifest membership and
hashes, WAV encoding, duration, conservative peak and RMS levels, DC offset,
earcon edge silence, ambience sample/slope continuity at the loop boundary,
cooldowns, independent volume, and the no-headset-haptic/no-motion-audio
policies.

## Runtime integration

- `InteractionFeedbackRecipes.swift` declares the semantic event and optional
  external-accessory haptic boundary.
- `InteractionFeedbackController.swift` owns one player pool, cooldowns,
  priority/voice limiting, warning ducking, ambience fades, persisted user
  controls, and the mixable ambient audio session.
- `stage_release_resources.sh` copies the entire pack and verifies all eight
  WAV files against this manifest for direct and Xcode builds.
- The app emits custom feedback only for a committed tier boundary, lesson
  state, confirmation/warning, restore, major view transition, or the custom
  immersive spatial-tap target. Standard controls keep their system treatment.
- A debug-only `STROKE_RUNTIME_FEEDBACK_PROBE=1` launch prepares all resources
  and starts one confirmation cue for packaged-runtime verification.

Simulator testing verifies packaging and playback startup; it cannot establish
physical Vision Pro loudness, comfort, hearing-device behavior, or accessory
haptic behavior. Those remain release gates.

See `PROVENANCE.md` and `LICENSE.md` before redistributing the files.
