#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
app_root="${script_dir:h}"
repo_root="${app_root:h:h}"
build_root="${STROKE_IMMERSIVE_BUILD_ROOT:-$app_root/build}"
test_binary="$build_root/ExperienceCoreSmokeTests"

mkdir -p "$build_root"
swiftc \
    -parse-as-library \
    -O \
    -o "$test_binary" \
    "$app_root"/Sources/ExperienceCore/*.swift \
    "$app_root"/Tests/ExperienceCoreTests/ExperienceCoreSmokeMain.swift

"$test_binary" "$repo_root"
