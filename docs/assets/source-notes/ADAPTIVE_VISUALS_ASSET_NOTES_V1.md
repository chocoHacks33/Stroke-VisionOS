# Adaptive visuals asset notes v1

## Asset

### `brain_orientation_calm_educational_v1`

A comfort-oriented external brain orientation model derived from
`brain_anatomy_realistic_v2`. It retains the bilateral cortical silhouette,
cerebellum, and brainstem in four matte, high-roughness, non-tissue pastel
materials. It intentionally contains no blood, fluid, vessel, clot, lesion,
incision, cut surface, procedural instrument, or dense label layer.

Suggested scene parent:
`patient_education/adaptive_visuals/brain_orientation`.

Suggested display contract:

- keep `patient_display_authorized=false` until the exact package and host
  presentation policy/entity mapping pass specialist and human-factors review;
- treat `comfort_oriented_low_intensity` as a presentation profile, not a clinical
  condition or diagnosis;
- activate after an explicit viewer choice or a consented, clinician-governed
  application rule;
- disclose that presentation detail changed and make the change immediately
  reversible;
- keep an obvious “show more detail” control and never remove information the
  clinical team considers material to informed consent;
- do not infer anxiety from pupil size, gaze, joint movement, or any other
  biometric/behavioural signal in this feature; a future research protocol
  would require separate consent, validation, privacy controls, and
  human-factors review and still could not silently become a diagnosis;
- do not claim that muted pastel colour is universally calming or that this model
  reduces anxiety. It is a design hypothesis requiring representative user tests.

Runtime geometry is authored in metres with Y-up. The source model is centred at
the origin and contains four model regions. The package is static/kinematic; no
collision, deformable-body, fluid, or force semantics are authored.

## Reproduction

With Blender 5.2.0 LTS installed at the standard macOS location:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python source/build_adaptive_visuals_v1.py
python3 source/validate_adaptive_visuals_v1.py
```

The builder records exact byte counts and SHA-256 values in
`asset_manifest_adaptive_visuals_v1.json`. The validator checks those records,
Apple strict USD conformance, metre/Y-up metadata, package structure, prohibited
graphic prim names, preview dimensions, and a real RealityKit decode.
