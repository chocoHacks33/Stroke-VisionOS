"""Compatibility metadata for older pip frontends shipped with Xcode Python."""

from setuptools import find_packages, setup


setup(
    name="stroke-vision-adaptive-asset-service",
    version="0.2.0",
    description="Local, non-diagnostic presentation-adaptation endpoint for Stroke VisionOS assets",
    python_requires=">=3.9",
    packages=find_packages(include=("adaptive_asset_service", "adaptive_asset_service.*")),
    package_data={
        "adaptive_asset_service": [
            "static/*.html",
            "static/*.css",
            "static/*.js",
            "runtime_profiles/*.json",
        ]
    },
    entry_points={
        "console_scripts": [
            "adaptive-asset-service=adaptive_asset_service.server:main",
        ]
    },
)
