# Provenance

All eight WAV files in `Audio/` are original procedural synthesis created for
this repository. They contain no recordings, sampled media, third-party loops,
copied melodies, third-party sound libraries, or generated material from an
external media service.

The deterministic source is:

```text
Apps/StrokeImmersiveExperience/Scripts/InteractionFeedback/generate_earcons.py
```

The generator uses Python standard-library oscillators and envelopes. The
transition cue uses a seeded pseudo-random low-pass noise swell. The optional
water/rain ambience uses seeded noise, circular moving-average filters,
integer-cycle swells, DC removal, and deterministic selection of a quiet loop
boundary. Its output is fully described by the checked-in source. Re-running it
with a compatible Python 3 runtime must reproduce the hashes in
`feedback_manifest_v1.json`.

Design intent is limited to restrained interface feedback: rounded attacks and
releases, low peak levels, short earcon durations, cooldowns, and one optional
low-level seamless ambience. These are implementation choices, not clinical
evidence and not a claim of universal preference, comfort, calm, treatment, or
anxiety reduction.

The cue names describe UI events only. They do not encode anatomy, pathology,
patient condition, clinical priority, or procedural success.
