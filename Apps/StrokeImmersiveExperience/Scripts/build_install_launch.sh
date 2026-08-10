#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
script_name="${0:t}"
app_root="${script_dir:h}"
repo_root="${app_root:h:h}"
xcode_developer="${STROKE_XCODE_DEVELOPER:-/Applications/Xcode-beta.app/Contents/Developer}"
device_selector="${STROKE_VISION_DEVICE_UDID:-}"
device_udid=""
build_root="${STROKE_IMMERSIVE_BUILD_ROOT:-$app_root/build}"
app_bundle="$build_root/Stroke Care Immersive.app"
app_identifier="com.strokevision.education.immersive"
build_only=false
screenshot_path=""
screenshot_delay="${STROKE_SCREENSHOT_DELAY_SECONDS:-15}"
enable_open_preview=false

usage() {
    print "Usage: $script_name [--build-only] [--device <UDID|exact-name>] [--screenshot <png-path>] [--enable-open-preview]"
}

while (( $# > 0 )); do
    case "$1" in
        --build-only)
            build_only=true
            shift
            ;;
        --screenshot)
            [[ $# -ge 2 ]] || { usage; exit 64; }
            screenshot_path="$2"
            shift 2
            ;;
        --device)
            [[ $# -ge 2 ]] || { usage; exit 64; }
            device_selector="$2"
            shift 2
            ;;
        --enable-open-preview)
            enable_open_preview=true
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            print -u2 "Unknown option: $1"
            usage
            exit 64
            ;;
    esac
done

if [[ ! -d "$xcode_developer" ]]; then
    print -u2 "Xcode developer directory is unavailable: $xcode_developer"
    exit 69
fi
export DEVELOPER_DIR="$xcode_developer"

sdk_path="$(xcrun --sdk xrsimulator --show-sdk-path)"
swift_compiler="$(xcrun --sdk xrsimulator --find swiftc)"
mkdir -p "$build_root"
if [[ -d "$app_bundle" ]]; then
    rm -rf "$app_bundle"
fi
mkdir -p "$app_bundle"

core_sources=("$app_root"/Sources/ExperienceCore/*.swift(N))
feedback_sources=("$app_root"/Sources/InteractionFeedback/*.swift(N))
app_sources=("$app_root"/Sources/StrokeImmersiveExperience/*.swift(N))
if (( ${#core_sources} == 0 || ${#feedback_sources} == 0 || ${#app_sources} == 0 )); then
    print -u2 "Expected ExperienceCore, InteractionFeedback, and app Swift sources under $app_root/Sources"
    exit 66
fi

"$swift_compiler" \
    -target arm64-apple-xros27.0-simulator \
    -sdk "$sdk_path" \
    -parse-as-library \
    -O \
    -framework SwiftUI \
    -framework RealityKit \
    -framework AVFAudio \
    -o "$app_bundle/StrokeImmersiveExperience" \
    "${core_sources[@]}" \
    "${feedback_sources[@]}" \
    "${app_sources[@]}"

cp "$app_root/Info.plist" "$app_bundle/Info.plist"
/usr/libexec/PlistBuddy -c 'Delete :UIDeviceFamily' "$app_bundle/Info.plist" 2>/dev/null || true
/usr/libexec/PlistBuddy -c 'Add :UIDeviceFamily array' "$app_bundle/Info.plist"
/usr/libexec/PlistBuddy -c 'Add :UIDeviceFamily:0 integer 7' "$app_bundle/Info.plist"
"$script_dir/stage_release_resources.sh" "$app_bundle"
codesign --force --sign - --timestamp=none "$app_bundle"

catalog="$app_bundle/RealityKitContent/InterfaceMedia/visual_detail_variants_v1/visual_detail_variant_catalog_v1.json"
bundled_count="$(jq -r '[.assets[].source_usdz] | unique | length' "$catalog")"
[[ "$bundled_count" == "150" ]] || {
    print -u2 "Bundle validation expected 150 USDZ bindings, found $bundled_count"
    exit 65
}

print "APP_BUNDLE=$app_bundle"
print "BUNDLE_ID=$app_identifier"
print "CATALOGUED_USDZ_COUNT=$bundled_count"

if $build_only; then
    exit 0
fi

if [[ -n "$device_selector" ]]; then
    device_udid="$(xcrun simctl list devices -j | jq -r --arg selector "$device_selector" '
        [.devices[][]
            | select(.isAvailable)
            | select(.udid == $selector or ((.name | ascii_downcase) == ($selector | ascii_downcase)))]
        | sort_by(if .state == "Booted" then 0 else 1 end)
        | first | .udid // empty
    ')"
    if [[ -z "$device_udid" ]]; then
        print -u2 "No available visionOS Simulator matched --device: $device_selector"
        exit 69
    fi
fi
if [[ -z "$device_udid" ]]; then
    device_udid="$(xcrun simctl list devices -j | jq -r '
        [.devices[][] | select(.isAvailable and .state == "Booted" and (.name | test("Vision Pro|Stroke Care"; "i")))]
        | first | .udid // empty
    ')"
fi
if [[ -z "$device_udid" ]]; then
    device_udid="$(xcrun simctl list devices -j | jq -r '
        [.devices[][] | select(.isAvailable and (.name | test("Vision Pro|Stroke Care"; "i")))]
        | first | .udid // empty
    ')"
fi
if [[ -z "$device_udid" ]]; then
    print -u2 "No available Apple Vision Pro simulator was found. Set STROKE_VISION_DEVICE_UDID."
    exit 69
fi

xcrun simctl boot "$device_udid" 2>/dev/null || true
xcrun simctl bootstatus "$device_udid" -b
xcrun simctl terminate "$device_udid" "$app_identifier" 2>/dev/null || true
xcrun simctl uninstall "$device_udid" "$app_identifier" 2>/dev/null || true
xcrun simctl install "$device_udid" "$app_bundle"
if $enable_open_preview; then
    SIMCTL_CHILD_STROKE_ENABLE_OPEN_CRANIAL_DEVELOPER_PREVIEW=1 \
        xcrun simctl launch --terminate-running-process "$device_udid" "$app_identifier"
    print "OPEN_CRANIAL_DEVELOPER_PREVIEW=enabled"
else
    xcrun simctl launch --terminate-running-process "$device_udid" "$app_identifier"
    print "OPEN_CRANIAL_DEVELOPER_PREVIEW=disabled"
fi
print "DEVICE=$device_udid"

if [[ -n "$screenshot_path" ]]; then
    screenshot_parent="${screenshot_path:h}"
    mkdir -p "$screenshot_parent"
    sleep "$screenshot_delay"
    xcrun simctl io "$device_udid" screenshot "$screenshot_path"
    print "SCREENSHOT=$screenshot_path"
fi
