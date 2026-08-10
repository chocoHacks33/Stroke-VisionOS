#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
app_root="${script_dir:h:h}"
xcode_developer="${STROKE_XCODE_DEVELOPER:-/Applications/Xcode-beta.app/Contents/Developer}"
device_udid="${STROKE_VISION_DEVICE_UDID:-}"
derived_data="$(mktemp -d /tmp/stroke-runtime-asset-probe.XXXXXX)"

cleanup() {
    if [[ "$derived_data" == /tmp/stroke-runtime-asset-probe.* && -d "$derived_data" ]]; then
        rm -rf -- "$derived_data"
    fi
}
trap cleanup EXIT

[[ -d "$xcode_developer" ]] || {
    print -u2 "Xcode developer directory is unavailable: $xcode_developer"
    exit 69
}
export DEVELOPER_DIR="$xcode_developer"

if [[ -z "$device_udid" ]]; then
    device_udid="$(xcrun simctl list devices -j | jq -r '
        [.devices[][] | select(.isAvailable and .state == "Booted" and (.name | test("Vision Pro|Stroke Care"; "i")))]
        | first | .udid // empty
    ')"
fi
[[ -n "$device_udid" ]] || {
    print -u2 "Boot a visionOS Simulator or set STROKE_VISION_DEVICE_UDID."
    exit 69
}

probe_ids=(
    head_skin_generic
    thrombectomy_registered_hero_v2
    cerebral_bloodflow_teaching_set_v2
    neural_detail_registered_review_assembly_v3
    artery_cutaway_complete_v2
    artery_interior_bloodflow_v2
    artery_wall_cutaway_v2
    brain_anatomy_realistic_v2
    brain_orientation_calm_educational_v1
    cerebral_arteries_realistic_v2
    cerebral_bloodflow_animation_v2
    circle_of_willis_flow_overlay_v2
    cranial_bone_access_closure_registered_conceptual_v1
    dural_access_closure_registered_conceptual_v1
    external_head_scalp_cutaway_v2
    external_head_scalp_realistic_v2
    intracerebral_hematoma_registered_conceptual_v1
    ischemic_mca_clot_v2
    microcirculation_arterial_venous_v2
    neck_access_arteries_realistic_v2
    patient_supine_generic
    red_blood_cells_closeup_v2
    scalp_access_closure_registered_conceptual_v1
    skull_semantic_realistic_v2
    stent_retriever_educational_v2
)
probe_value="${(j:,:)probe_ids}"

xcodebuild \
    -project "$app_root/StrokeImmersiveExperience.xcodeproj" \
    -scheme StrokeImmersiveExperience \
    -configuration Debug \
    -sdk xrsimulator \
    -destination "platform=visionOS Simulator,id=$device_udid" \
    -derivedDataPath "$derived_data" \
    CODE_SIGNING_ALLOWED=YES \
    build >/dev/null

app_bundle="$derived_data/Build/Products/Debug-xrsimulator/StrokeImmersiveExperience.app"
bundle_id="com.strokevision.education.immersive"
xcrun simctl terminate "$device_udid" "$bundle_id" 2>/dev/null || true
xcrun simctl uninstall "$device_udid" "$bundle_id" 2>/dev/null || true
xcrun simctl install "$device_udid" "$app_bundle"
launch_output="$(
    SIMCTL_CHILD_STROKE_RUNTIME_ASSET_PROBE_ID="$probe_value" \
    SIMCTL_CHILD_STROKE_RUNTIME_UI_PROBE_ID=head_skin_generic \
    SIMCTL_CHILD_STROKE_RUNTIME_FEEDBACK_PROBE=1 \
        xcrun simctl launch --terminate-running-process "$device_udid" "$bundle_id"
)"
process_id="${launch_output##*: }"

summary=""
feedback_summary=""
for _ in {1..45}; do
    summary="$(
        xcrun simctl spawn "$device_udid" log show \
            --style compact \
            --last 3m \
            --predicate "processIdentifier == $process_id AND eventMessage CONTAINS \"[StrokeAssetProbe] SUMMARY\"" \
            2>/dev/null \
        | rg 'StrokeAssetProbe.*SUMMARY' \
        | tail -n 1 \
        || true
    )"
    feedback_summary="$(
        xcrun simctl spawn "$device_udid" log show \
            --style compact \
            --last 3m \
            --predicate "processIdentifier == $process_id AND eventMessage CONTAINS \"[StrokeFeedbackProbe]\"" \
            2>/dev/null \
        | rg 'StrokeFeedbackProbe.*(PASS|FAIL)' \
        | tail -n 1 \
        || true
    )"
    [[ -n "$summary" && -n "$feedback_summary" ]] && break
    sleep 2
done

print "$summary"
expected="requested=${#probe_ids} passed=${#probe_ids} failed=0"
[[ "$summary" == *"$expected"* ]] || {
    xcrun simctl spawn "$device_udid" log show \
        --style compact \
        --last 3m \
        --predicate "processIdentifier == $process_id AND eventMessage CONTAINS \"[StrokeAssetProbe] FAIL\"" \
        2>/dev/null \
        | rg 'StrokeAssetProbe.*FAIL' \
        || true
    print -u2 "Packaged RealityKit probe did not report: $expected"
    exit 1
}

print "PACKAGED_XROS_ASSET_PROBE=PASS"
print "$feedback_summary"
[[ "$feedback_summary" == *"StrokeFeedbackProbe] PASS earcons=7 ambience_ready=true"* ]] || {
    print -u2 "Packaged interaction-feedback probe did not prepare and start the complete pack."
    exit 1
}
print "PACKAGED_XROS_FEEDBACK_PROBE=PASS"
