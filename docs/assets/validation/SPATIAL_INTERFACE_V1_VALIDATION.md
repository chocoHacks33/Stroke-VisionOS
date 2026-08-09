# Spatial interface v1 validation

## Result

**PASS as an integrity-checked, display-blocked developer handoff.** The module
is not patient-authorized, not integrated into a visionOS app, and not clinical,
Simulator, physical-device, accessibility, comfort, or performance evidence.

## Automated checks

- All 9 module JSON files parse.
- The annotation schema parses as Draft 2020-12. A third-party JSON Schema
  validator was unavailable, so required-field/type-state invariants were
  checked directly; this is recorded rather than overstated as full schema-tool
  validation.
- The code-native SVG is well-formed XML and contains no external image asset.
- The interface manifest declares 14 unique resources. Every path exists and
  every declared byte count and SHA-256 matches.
- Scene presets reference 32 known IDs across the frozen 135-asset, 12-manifest
  release catalog. There are zero unknown IDs.
- Four case fixtures are `fictional=true`, `contains_phi=false`, have no
  recommendation or outcome prediction, resolve a manifested synthetic
  portrait, and resolve a known scene preset.
- All three evidence records have null claim/source/reviewer fields and
  `display_authorized=false`.
- All eight annotation requests resolve a released source asset and exact
  package hash. All selectors, anchor transforms, and display-copy fields remain
  null; no functional claim is allowed.
- Public text resources contain no user-home, download-folder, messaging-app,
  local-file URI, or other private absolute path.
- The module contains zero USDZ files and does not rewrite anatomy.

## Media checks

The four portraits are 1254 × 1254 RGB PNGs. The storyboard is 1653 × 952.
Their hashes and byte counts match the manifest and provenance file. macOS
metadata inspection found no creator, description, comment, or download-origin
fields. Visual inspection found centered synthetic adult portraits with plain
clothing, neutral clinic-style backgrounds, and no visible text, badge, logo,
medical device, or distress.

The storyboard passes only as a supporting layout image. It includes generated
visible phrases such as “real-world cases” and a generic evidence statement.
Those pixels are rejected as runtime copy and conflict with the authoritative
fictional-case and evidence-placeholder JSON. The app must not transcribe, OCR,
ship, or cite them.

## Safety and privacy checks

- Current source laterality is explicitly right M1; presets prohibit left-MCA
  copy with the right-sided clot and baked animation.
- Portrait appearance has no identity, diagnosis, history, role, prognosis, or
  demographic-evidence meaning.
- A persistent fictional-scenario badge is required.
- Family entry still requires patient participation or authorization and the
  host privacy flow.
- Platform hands/gaze are interaction only and may not drive anxiety inference.
- Evidence and annotation systems fail closed.
- Structural atlas labels may not become functional, deficit, perfusion, or
  outcome claims without separately approved mappings.

## Required external gates

Before any patient-facing pilot, the exact assembled app must complete:

1. Native Xcode integration, deterministic state/reset tests, and failure-state
   tests.
2. Exact annotation selector, local-anchor, copy, laterality, accessibility,
   and package-revision review.
3. Current-source evidence authoring and clinical approval.
4. Privacy and accidental-resemblance review for synthetic portraits.
5. Accessibility and human-factors review, including Reduce Transparency,
   Increase Contrast, Reduce Motion, VoiceOver, seated/reclined use, and opt-out.
6. Simulator evidence followed by separate physical Vision Pro input,
   readability, occlusion, comfort, memory, draw-call, and frame-timing evidence.
7. Clinical, neuroanatomy/interventional, licensing, security, quality, and
   release approval for the exact build.
