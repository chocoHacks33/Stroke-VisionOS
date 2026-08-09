# Clinical review gate for a patient-facing pilot

This checklist must be completed by the appropriate local clinical, regulatory,
accessibility, and engineering owners. A checked item records review; it is not
a claim that the model is suitable for treatment planning.

## Intended-use boundary

- [ ] The experience is labelled **generic patient education**, not a simulation
      of this patient's anatomy or predicted procedure.
- [ ] It never presents the model as diagnostic imaging, a navigation system,
      device-sizing guidance, a risk calculator, or an outcome prediction.
- [ ] The treating clinician remains responsible for the informed-consent
      conversation and can pause, skip, or correct the visualization.
- [ ] Patient-facing language distinguishes mechanical thrombectomy from open
      cranial surgery and avoids implying that every stroke follows this pathway.

## Neuroanatomy and procedure sequence

- [ ] An interventional neuroradiologist has reviewed left/right orientation,
      Circle of Willis branching, ICA-to-MCA path, and the conceptual right-M1
      occlusion position.
- [ ] A stroke neurologist has reviewed the stroke explanation, urgency, likely
      care pathway, alternatives, material risks, uncertainty, and recovery
      messaging.
- [ ] Device geometry and motion are clearly generic; deployment, aspiration,
      clot engagement, withdrawal, and reperfusion are not shown with misleading
      precision.
- [ ] Open-cranial assets are excluded from the thrombectomy flow unless a
      separate neurosurgical procedure is explicitly being explained.
- [ ] The clot is never used as a lesion measurement or a substitute for CTA,
      MRA, DSA, CT-perfusion, or clinician interpretation.
- [ ] Flow arrows, particles, streamline paths, and animation timing are labelled
      illustrative; they are never described as CFD, perfusion, pressure,
      velocity, collateral grading, or a prediction of reperfusion.
- [ ] Magnified artery-wall layers, capillaries, and red-blood-cell views are
      explicitly explained as scale-separated teaching vignettes rather than a
      single correctly scaled scene.
- [ ] The blue/purple venous palette is explained as an interface convention;
      no narration or label implies that venous blood is literally blue.

## Intracranial-detail v3 review

- [ ] A neuroanatomist or appropriately qualified neuroradiologist has reviewed
      the cortical parcels, deep nuclei, ventricular spaces, brainstem,
      cerebellum, broad white-matter regions, and pathway labels against the
      retained HRA source/version and the intended lesson.
- [ ] A specialist has reviewed every enabled cranial-nerve, orbital,
      pituitary, airway, nasal-space, and muscle layer for identity, laterality,
      continuity, registration, terminology, and patient-facing relevance.
- [ ] The broad white-matter parent volumes and detailed pathway surfaces are
      visibility alternatives; they are never presented as disjoint tissue
      compartments or as patient tractography.
- [ ] Review assemblies are not loaded with any of their transitive component
      packages. The application enforces every manifest
      `prohibited_combinations` rule before scene composition.
- [ ] The two packages marked `HOLD_FOR_INNER_EAR_LICENSE_REVIEW` are absent
      from the release bundle unless legal/provenance review has cleared them or
      the held geometry has been replaced with a compatible source.
- [ ] Microscopic teaching packages always show a persistent magnification and
      non-anatomical-scale warning. Their authored bounds, counts, spacing,
      material colors, and relative positions are never described as measured
      histology, physiology, pathology, or patient anatomy.
- [ ] A neuropathologist/hematologist has reviewed the intended explanation of
      the neurovascular unit, blood elements, platelet/fibrin thrombus,
      myelination, synapse, choroid-plexus/CSF interface, and ischemic tissue
      zones. Any unsupported literal or quantitative interpretation is removed.

## Surgical-tool v3 review

- [ ] An interventional neuroradiologist has reviewed every enabled
      endovascular-support category, its `EVT-*` stage association, and its
      relation to the existing guidewire, microcatheter, aspiration-catheter,
      and stent-retriever concepts. Availability never implies necessity,
      compatibility, a required access route, or a preferred technique.
- [ ] `EVT-06A_STENT_RETRIEVER`, `EVT-06B_CONTACT_ASPIRATION`, and
      `EVT-06C_COMBINED` are explicit alternatives. Comparison resets the scene
      and does not imply that every patient receives all three.
- [ ] Contrast/flush, aspiration support, suite controls, sterile tray, access
      tools, and hemostasis options are labelled generic and conditional on the
      clinician-selected approach and local protocol. No medication, dose,
      pressure, radiation, connector, timing, or operating instruction appears.
- [ ] Ordinary EVT contains zero open-cranial tools, scalp/bone/dural access,
      EVD props, cranial closure, or postoperative head dressing.
- [ ] A neurosurgeon has reviewed the exact open branch before any
      open-cranial tool becomes selectable. Every such asset remains behind
      `clinician_selected_hemorrhage_or_decompression_only` and is never
      inferred from generic hematoma or edema geometry.
- [ ] Open evacuation, minimally invasive evacuation, decompression, and
      optional CSF access remain conditional alternatives rather than one
      inevitable sequence. Conditional CSF-access tools remain hidden unless a
      separately approved narrative enables them.
- [ ] Bone-flap fixation is available only for a reviewed craniotomy-replacement
      branch and is prohibited in a decompressive-craniectomy leave-off state.
- [ ] Review assemblies are never co-loaded with any direct or transitive
      component. Existing overlapping access, drill, suction/forceps, and EVD
      packages are replaced or reduced to non-overlapping context while a
      detailed close-up is active.
- [ ] The tool catalog is described as representative and non-exhaustive. Its
      omissions never become an assertion that no other equipment, monitoring,
      medication, personnel, sterile-processing step, or contingency is used.
- [ ] All tool motion is static or qualitative kinematic presentation. No force,
      depth, trajectory, drilling/cutting, suction/irrigation, pressure, energy,
      device sizing, navigation, compatibility, sterile technique, or training
      claim is made or inferred from mesh dimensions or placement.

## Visual and interaction safety

### Adaptive visual-comfort mode

- [ ] The feature is named and explained as a visual-detail preference, not an
      anxiety detector, mental-health screen, diagnosis, risk score, or anxiety
      treatment.
- [ ] Production selection comes only from the viewer's explicit preference or
      a visible, governed facilitator choice. `simulated_demo` is labelled
      simulated/non-diagnostic and is never used to make a real-person claim.
- [ ] Pupil diameter, gaze, hand joints, movement trajectories, voice, and
      other biometric or behavioural streams are not submitted to the endpoint
      or used to infer anxiety.
- [ ] `patient_display_authorized` remains false until an external governed
      release approves the exact source-asset hash/version, semantic entity
      mapping, adaptive policy/profile, warnings, and application controls.
- [ ] `brain_orientation_calm_educational_v1` remains a display-blocked review
      candidate until specialist and human-factors review is recorded for the
      exact package. It replaces the source during orientation and is never
      co-loaded over detailed anatomy.
- [ ] Generated USDA drafts remain `display_authorized: false`, are described
      as abstract/non-anatomical, and cannot self-approve or enter the
      patient-facing catalog without the full asset release process.
- [ ] Show Less, Show More, Pause, Exit/Return, and Restore Original remain
      visible and operable; no transition silently escalates graphic detail.
- [ ] System Reduce Motion and a static option are honored. The overview tier
      shows no blood particles or surgical motion and keeps a stationary frame.
- [ ] Every adaptation visibly discloses that it is active and lists the changed
      presentation properties. Risks, benefits, alternatives, uncertainty, and
      clinician-approved material facts remain available in plain language.
- [ ] Family mode requires patient participation or authorization and a privacy
      confirmation, and never reveals more detail than the patient authorized.
- [ ] Representative stroke patients, family members, older adults,
      motion-sensitive users, people with varied health literacy, clinicians,
      accessibility specialists, and patient-education owners have reviewed
      comprehension, preference, discomfort, distress, and restoration of full
      information.

- [ ] Skin/skull/dura/brain reveals use cutaways or toggles rather than stacked
      transparent shells that obscure spatial relationships.
- [ ] Falx, tentorium, dural sinuses, and head/neck vessels have been reviewed
      in their registered context; no simplified shell or flow cue is allowed to
      imply a patient-specific variant or operative corridor.
- [ ] Blood, incisions, and instruments use the least graphic presentation that
      still communicates the clinical point; the patient can opt out or stop.
- [ ] Labels, colors, and highlights are understandable without relying on red
      versus green alone; captions and spoken content have accessible equivalents.
- [ ] Controls work when seated or reclined and do not require rapid head/hand
      movement; comfort has been tested on actual Vision Pro hardware.
- [ ] The experience avoids guaranteed outcomes, false reassurance, and
      unnecessary fear-inducing detail.

## Technical release gate

- [ ] Every deployment USDZ passes `usdchecker --arkit` and contains the expected
      nonzero mesh/material hierarchy in a RealityKit load test.
- [ ] Dimensions, pivots, Y-up orientation, material appearance, culling, and
      reveal state are verified in Reality Composer Pro and on device.
- [ ] The assembled experience meets its on-device frame deadline under
      RealityKit Trace; only required layers are loaded at each step.
- [ ] Source attribution, ShareAlike obligations, third-party notices, and asset
      modification records are present in the distributed product.
- [ ] Privacy/security review is complete before any patient-derived imaging,
      identifiers, analytics, recordings, or cloud processing are introduced.
- [ ] Atlas geometry is visibly identified as generic. Any patient-specific
      replacement retains one reviewed DICOM frame of reference, source-series
      provenance, segmentation/registration versions, transform hash, error
      measurement, laterality check, reviewer record, and de-identification
      status; independently recentered structures are rejected.
- [ ] The DICOM LPS-millimetre to project Y-up-metre transform has been verified
      with at least three landmarks and a left/right reflection test. Raw DICOM,
      identifiers, and identifiable facial surfaces are absent from public
      repositories and distributable asset bundles.
- [ ] Houdini physics, VDB, flow, soft-body, collision, or particle layers are
      isolated from anatomical source geometry and labelled with their evidence
      class. A visually plausible solver result is never promoted to a clinical
      measurement without a separately approved validation protocol.

## Sign-off record

| Role | Name | Version reviewed | Date | Decision / notes |
| --- | --- | --- | --- | --- |
| Interventional neuroradiology |  |  |  |  |
| Stroke neurology |  |  |  |  |
| Neurosurgery, if applicable |  |  |  |  |
| Patient education / consent |  |  |  |  |
| Accessibility / human factors |  |  |  |  |
| Regulatory / legal / privacy |  |  |  |  |
| visionOS engineering / QA |  |  |  |  |
