# Adaptive visuals source provenance v1

## Source work and licence

`brain_orientation_calm_educational_v1` is a derivative of:

> Human Reference Atlas (HRA), “Brain, Male,” version 1.01, NIH 3D entry
> 3DPX-020960, https://3d.nih.gov/entries/20960?version=1.01, licensed CC BY 4.0.
> Source data informed by Ding et al. (2016), the Allen human brain reference
> atlas, and the Visible Human Project.

- Source entry: https://3d.nih.gov/entries/20960?version=1.01
- Licence: Creative Commons Attribution 4.0 International
- Licence URL: https://creativecommons.org/licenses/by/4.0/
- Local source record:
  `vendor/nih3d/hra_brain_male_3DPX-020960_v1.01/`
- Upstream derivative in this kit: `brain_anatomy_realistic_v2`

CC BY 4.0 attribution and the change notice below must accompany every
redistribution of this derivative. No new third-party geometry, textures, HDRIs,
fonts, or online marketplace assets were introduced.

## Change notice

Modified from the HRA source: selected only external orientation structures;
recentered, joined by anatomical region, decimated, smoothed, and recolored with
high-roughness pastel materials. Deep structures, ventricles, vessels, pathology,
blood, and cut surfaces are not included.

The derivative contains four visual regions: left cerebral hemisphere, right
cerebral hemisphere, cerebellum, and brainstem. The bilateral material contrast
supports orientation; it is not a tissue-colour claim. The palette and reduced
visual density are a comfort-oriented design hypothesis, not a proven anxiety-
reducing intervention, and require evaluation with representative users.

## Clinical and behavioural scope

This is generic, non-patient-specific educational media. It is not validated for
diagnosis, treatment planning, navigation, device sizing, outcome prediction,
clinical anxiety assessment, or treatment of anxiety. The asset performs no pupil,
movement, gaze, or behavioural inference. A host application may select this
display profile only through a transparent and reversible policy with manual
override; it must preserve optional access to the full clinician-approved facts.
The current package record sets `patient_display_authorized=false`; technical
validation and catalog presence do not clear it for patient use.
