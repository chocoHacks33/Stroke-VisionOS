#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
app_root="${script_dir:h}"
repo_root="${app_root:h:h}"
destination_root="${1:-}"

if [[ -z "$destination_root" ]]; then
    print -u2 "Usage: ${0:t} <app-resource-root>"
    exit 64
fi

catalog_relative="RealityKitContent/InterfaceMedia/visual_detail_variants_v1/visual_detail_variant_catalog_v1.json"
catalog_source="$repo_root/$catalog_relative"

if [[ ! -f "$catalog_source" ]]; then
    print -u2 "Missing 150-asset catalog: $catalog_source"
    exit 66
fi
if ! command -v jq >/dev/null 2>&1; then
    print -u2 "jq is required to stage the exact catalogued release resources."
    exit 69
fi

asset_count="$(jq -r '.source_release_asset_count' "$catalog_source")"
variant_count="$(jq -r '.virtual_variant_count' "$catalog_source")"
if [[ "$asset_count" != "150" || "$variant_count" != "450" ]]; then
    print -u2 "Catalog count mismatch: assets=$asset_count variants=$variant_count"
    exit 65
fi

destination_reality="$destination_root/RealityKitContent"
if [[ -d "$destination_reality" ]]; then
    rm -rf "$destination_reality"
fi
mkdir -p "$destination_reality"

while IFS= read -r relative_path; do
    source_path="$repo_root/$relative_path"
    destination_path="$destination_root/$relative_path"
    if [[ ! -f "$source_path" ]]; then
        print -u2 "Catalogued USDZ is missing: $relative_path"
        exit 66
    fi
    mkdir -p "${destination_path:h}"
    cp -p "$source_path" "$destination_path"
done < <(jq -r '.assets[].source_usdz' "$catalog_source" | sort -u)

while IFS=$'\t' read -r relative_path expected_bytes expected_sha; do
    staged_path="$destination_root/$relative_path"
    actual_bytes="$(stat -f '%z' "$staged_path")"
    actual_sha="$(shasum -a 256 "$staged_path" | awk '{print $1}')"
    if [[ "$actual_bytes" != "$expected_bytes" ]]; then
        print -u2 "Byte-count mismatch for $relative_path: expected $expected_bytes, found $actual_bytes"
        exit 65
    fi
    if [[ "$actual_sha" != "$expected_sha" ]]; then
        print -u2 "SHA-256 mismatch for $relative_path"
        exit 65
    fi
done < <(jq -r '.assets[] | [.source_usdz, (.source_usdz_bytes | tostring), .source_usdz_sha256] | @tsv' "$catalog_source")

while IFS= read -r relative_path; do
    source_path="$repo_root/$relative_path"
    destination_path="$destination_root/$relative_path"
    if [[ ! -f "$source_path" ]]; then
        print -u2 "Catalogued manifest is missing: $relative_path"
        exit 66
    fi
    mkdir -p "${destination_path:h}"
    cp -p "$source_path" "$destination_path"
done < <(jq -r '.assets[].source_manifest' "$catalog_source" | sort -u)

for pack in \
    figma_page2_surgical_interface_v1 \
    spatial_care_interface_v1 \
    visual_detail_variants_v1
do
    source_pack="$repo_root/RealityKitContent/InterfaceMedia/$pack"
    destination_pack="$destination_root/RealityKitContent/InterfaceMedia/$pack"
    if [[ ! -d "$source_pack" ]]; then
        print -u2 "InterfaceMedia pack is missing: $pack"
        exit 66
    fi
    mkdir -p "${destination_pack:h}"
    ditto "$source_pack" "$destination_pack"
done

feedback_source="$app_root/Resources/InteractionFeedback"
feedback_destination="$destination_root/InteractionFeedback"
feedback_manifest="$feedback_source/feedback_manifest_v1.json"
if [[ ! -f "$feedback_manifest" ]]; then
    print -u2 "Interaction-feedback manifest is missing: $feedback_manifest"
    exit 66
fi
rm -rf "$feedback_destination"
ditto "$feedback_source" "$feedback_destination"

feedback_resource_count=0
while IFS=$'\t' read -r relative_path expected_bytes expected_sha; do
    staged_path="$feedback_destination/$relative_path"
    if [[ ! -f "$staged_path" ]]; then
        print -u2 "Staged interaction-feedback resource is missing: $relative_path"
        exit 66
    fi
    actual_bytes="$(stat -f '%z' "$staged_path")"
    actual_sha="$(shasum -a 256 "$staged_path" | awk '{print $1}')"
    if [[ "$actual_bytes" != "$expected_bytes" || "$actual_sha" != "$expected_sha" ]]; then
        print -u2 "Interaction-feedback integrity mismatch: $relative_path"
        exit 65
    fi
    feedback_resource_count=$((feedback_resource_count + 1))
done < <(jq -r '(.earcons + .ambiences)[] | [.file, (.bytes | tostring), .sha256] | @tsv' "$feedback_manifest")

if [[ "$feedback_resource_count" != "8" ]]; then
    print -u2 "Expected 8 interaction-feedback audio resources, staged $feedback_resource_count"
    exit 65
fi

copied_count=0
while IFS= read -r relative_path; do
    [[ -f "$destination_root/$relative_path" ]] || {
        print -u2 "Staged bundle is missing: $relative_path"
        exit 66
    }
    copied_count=$((copied_count + 1))
done < <(jq -r '.assets[].source_usdz' "$catalog_source" | sort -u)

if [[ "$copied_count" != "150" ]]; then
    print -u2 "Expected 150 unique catalogued USDZ resources, staged $copied_count"
    exit 65
fi

print "STAGED_USDZ_COUNT=$copied_count"
print "STAGED_INTERFACE_PACK_COUNT=3"
print "STAGED_INTERACTION_FEEDBACK_COUNT=$feedback_resource_count"
