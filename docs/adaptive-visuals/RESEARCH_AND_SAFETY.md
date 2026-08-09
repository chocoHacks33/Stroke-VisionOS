# Adaptive visual comfort — research and safety contract

Last reviewed: 2026-08-09

## Purpose

The adaptive-visual feature changes how an already approved educational asset
is presented. It may reduce exposed anatomy, particles, labels, motion, shine,
or information density. It may expose a low-intensity orientation asset as an
unapproved review candidate, but must not substitute that asset in a
patient-facing build until the exact version passes specialist and human-factors
review. It must not change medical facts, decide what a person is entitled to
know, or infer a diagnosis.

This is a **visual-comfort preference system**, not an anxiety detector,
screening tool, clinical assessment, or treatment feature.

## Evidence boundary

### Pupil and movement signals are not an anxiety diagnosis

- Pupil size is affected by luminance, attention, effort, arousal type,
  stimulus modality, and individual physiology. A 2024 controlled study found
  substantial heterogeneity, including participants without a measurable
  pupil-linked arousal response. That evidence does not validate individual
  anxiety inference. See the
  [Scientific Reports study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11412980/)
  and a
  [review of task-evoked pupil dilation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6267528/).
- Movement is also nonspecific. Research using extended actigraphy can study
  associations at a population level, but it does not turn momentary joint
  motion into a validated anxiety measurement. See the
  [2021 wearable-movement study](https://pubmed.ncbi.nlm.nih.gov/33401123/).
- The
  [USPSTF anxiety-screening recommendation](https://www.uspreventivestaskforce.org/uspstf/recommendation/anxiety-adults-screening)
  discusses validated screening instruments followed by diagnostic assessment;
  it does not support diagnosis from pupil or hand-motion observations.
- Apple describes eye input on visionOS as privacy-preserving system input;
  applications do not receive raw gaze or pupil-diameter data. Hand tracking in
  a Full Space is permission-gated and may be unavailable. See
  [Apple visionOS privacy guidance](https://developer.apple.com/documentation/visionOS/adopting-best-practices-for-privacy)
  and the
  [Apple privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy).

Therefore, the service must reject fields that claim to provide pupil-derived,
joint-derived, or model-derived anxiety. The prototype may randomize a comfort
preference only in an explicitly labelled `simulated_demo` mode.

## Permitted preference sources

Production-facing contracts may accept only:

1. `self_report_preference` — the viewer directly chooses the amount of visual
   detail and motion they want.
2. `clinician_override` — a facilitator selects a reviewed presentation tier
   with the viewer's knowledge.
3. `simulated_demo` — a random or seeded value used only for demos and tests;
   every response must identify it as simulated and non-diagnostic.

Suggested plain-language prompt:

> How much visual detail would you like right now: Simplified, Standard, or
> More clinical detail?

Every adaptation must be visible, reversible, and accompanied by Show less,
Show more, Pause, and Exit/Return controls. The system must never silently
escalate graphic detail.

## Presentation tiers

The following tiers are a design hypothesis derived from trauma-informed,
health-literacy, and accessibility principles. They require user testing and do
not have a validated relationship to anxiety severity.

| Tier | Presentation behavior | Medical-content rule |
| --- | --- | --- |
| `overview` | Opaque exterior/orientation model, no incision, exposed tissue, blood particles, or surgical sound; static cues; 3–5 labels | State that the view is simplified and keep clinician-approved facts available on request |
| `simplified` | Reduced layer count, restrained saturation/specular response, abstract clot marker, optional slow flow, short labels | Do not remove risks, alternatives, uncertainties, or the ability to open the standard explanation |
| `standard` | Approved patient-education anatomy and instruments, restrained realism, labels on demand | Default factual lesson content remains available |
| `clinical_detail` | Full reviewed layers after explicit opt-in or facilitator selection | Still generic and non-patient-specific; never becomes navigation, planning, or training content |

There is no strong evidence for a universally calming color palette. Muted
materials are a hypothesis to test. Text and controls must retain accessible
contrast, and meaning must never depend on color alone. See the
[Apple color HIG](https://developer.apple.com/design/human-interface-guidelines/color)
and [WCAG 2.2](https://www.w3.org/TR/WCAG22/).

## Motion and spatial comfort

- Honor the system Reduce Motion preference.
- Avoid rapid, spinning, bouncing, large-field, peripheral, multi-axis, or
  sustained oscillating motion.
- Prefer a stationary reference frame and fades for relocation.
- Pause motion when a presentation tier changes and let the viewer restart it.

See
[Apple's visionOS accessibility guidance](https://developer.apple.com/documentation/visionos/improving-accessibility-support-in-your-app/),
[Apple's motion HIG](https://developer.apple.com/design/human-interface-guidelines/motion),
and the
[Reduced Motion evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria).

## Information and consent

Adaptation changes presentation intensity, not medical truth. Risks, benefits,
alternatives, uncertainty, and the fact that the assets are generic must remain
available in clinician-approved plain language. Decision support material must
complement, not replace, conversation with the clinical team. See
[NICE shared decision-making recommendations](https://www.nice.org.uk/guidance/ng197/chapter/Recommendations)
and
[NICE decision-aid guidance](https://www.nice.org.uk/process/pmg42/chapter/writing-the-decision-aid).

Use one concept per step, short headings, whitespace, meaningful controls,
user-controlled next/back pacing, and a comprehension check. See the
[AHRQ Health Literacy Universal Precautions Toolkit](https://psnet.ahrq.gov/issue/ahrq-health-literacy-universal-precautions-toolkit-2nd-edition)
and the
[HHS Health Literacy Online checklist](https://odphp.health.gov/healthliteracyonline/checklist/).

For family viewing, ask whether the patient wants family or carers involved and
respect confidentiality. Store a separate display preference rather than
assuming the family and patient want identical detail. See
[NICE patient-experience guidance](https://www.nice.org.uk/guidance/cg138/ifp/chapter/involving-you-in-your-care).

## Runtime editing and generation

The immediate path should apply a cached, non-destructive recipe to an approved
asset: visibility masks, reviewed material substitutions, particle limits,
label density, motion speed, and pacing. This should complete in milliseconds
and preserve the source USDZ.

New or anatomically altered geometry is asynchronous and blocked from
patient-facing use until technical, provenance, and specialist review passes.
The API may return a generation job specification, but must not pretend a model
or review pipeline exists when it does not. Sensor-derived measures used in a
future clinical investigation would require a documented fit-for-purpose and
verification/validation process; see the
[FDA digital-health technology guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/digital-health-technologies-remote-data-acquisition-clinical-investigations).

## Privacy and logging

- Collect the minimum preference data and keep it local and ephemeral by
  default.
- Do not collect raw gaze, pupil, hand-joint trajectories, voice, identifiers,
  patient records, or scans through this endpoint.
- Log only request IDs, route, status, and duration by default. Keep asset IDs,
  preferences, simulation seeds, bodies, and client addresses out of the
  development log.
- A denied permission, missing signal, or absent preference must leave the app
  usable with a conservative user-controlled default.

## Validation required before a patient pilot

Test with stroke patients, family members, clinicians, older adults,
motion-sensitive users, and people with varied health literacy. Measure
comprehension, recall, preference, simulator discomfort, observed distress,
accessibility, and the ability to restore full information. Do not optimize only
for apparent calmness: hiding essential information can undermine informed
choice.

The design should follow trauma-informed principles of safety,
trust/transparency, collaboration, empowerment, voice, and choice. See
[SAMHSA's trauma-informed guidance](https://library.samhsa.gov/sites/default/files/pep23-06-05-005.pdf).
