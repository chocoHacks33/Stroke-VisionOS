"""Original, dependency-free low-intensity USDA presentation scene."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import secrets
import stat
from typing import Any


JOB_ID_PATTERN = re.compile(r"^[a-f0-9]{24}$")


def _usda_string(value: str) -> str:
    """JSON string escaping is compatible with USDA string literals."""
    return json.dumps(value, ensure_ascii=True)


def build_usda(asset_id: str, title: str, tier: str, recipe_sha256: str) -> str:
    """Build a soft, abstract orientation scene—not simulated anatomy."""
    return f'''#usda 1.0
(
    defaultPrim = "CalmPresentation"
    metersPerUnit = 1
    upAxis = "Y"
    customLayerData = {{
        string artifactRole = "abstract_procedural_review_draft"
        bool displayAuthorized = false
        string generator = "Stroke Vision procedural comfort template v1"
        string intendedUse = "Governed developer and clinician review draft only"
        string reviewGate = "specialist_and_human_factors_review_required_before_patient_display"
    }}
)

def Xform "CalmPresentation"
{{
    custom string sourceAssetId = {_usda_string(asset_id)}
    custom string sourceAssetTitle = {_usda_string(title)}
    custom string adaptationTier = {_usda_string(tier)}
    custom string artifactRole = "abstract_procedural_review_draft"
    custom bool displayAuthorized = false
    custom string recipeSha256 = {_usda_string(recipe_sha256)}
    custom string reviewGate = "specialist_and_human_factors_review_required_before_patient_display"
    custom string clinicalWarning = "Abstract review draft; not anatomy, not authorized for patient display, and not for clinical decisions"

    def Scope "Materials"
    {{
        def Material "ShellMaterial"
        {{
            token outputs:surface.connect = </CalmPresentation/Materials/ShellMaterial/Preview.outputs:surface>
            def Shader "Preview"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.38, 0.68, 0.74)
                float inputs:metallic = 0
                float inputs:opacity = 0.30
                float inputs:roughness = 0.72
                token outputs:surface
            }}
        }}
        def Material "AccentMaterial"
        {{
            token outputs:surface.connect = </CalmPresentation/Materials/AccentMaterial/Preview.outputs:surface>
            def Shader "Preview"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.94, 0.76, 0.47)
                float inputs:metallic = 0
                float inputs:roughness = 0.52
                token outputs:surface
            }}
        }}
        def Material "BaseMaterial"
        {{
            token outputs:surface.connect = </CalmPresentation/Materials/BaseMaterial/Preview.outputs:surface>
            def Shader "Preview"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.82, 0.88, 0.90)
                float inputs:metallic = 0
                float inputs:roughness = 0.82
                token outputs:surface
            }}
        }}
    }}

    def Xform "SoftHeadContext"
    {{
        def Sphere "Head" (
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {{
            double radius = 0.1
            rel material:binding = </CalmPresentation/Materials/ShellMaterial>
            double3 xformOp:scale = (0.88, 1.12, 1.0)
            double3 xformOp:translate = (0, 0.035, 0)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        }}
        def Cylinder "Neck" (
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {{
            uniform token axis = "Y"
            double height = 0.07
            double radius = 0.038
            rel material:binding = </CalmPresentation/Materials/ShellMaterial>
            double3 xformOp:translate = (0, -0.085, 0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }}
        def Torus "OrientationRing" (
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {{
            uniform token axis = "Y"
            double majorRadius = 0.118
            double minorRadius = 0.0022
            rel material:binding = </CalmPresentation/Materials/BaseMaterial>
            double3 xformOp:translate = (0, 0.035, 0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }}
        def Sphere "FocusPoint" (
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {{
            double radius = 0.009
            rel material:binding = </CalmPresentation/Materials/AccentMaterial>
            double3 xformOp:translate = (0.035, 0.055, 0.094)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }}
    }}

    def Xform "CalmBase"
    {{
        def Cylinder "Platform" (
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {{
            uniform token axis = "Y"
            double height = 0.008
            double radius = 0.145
            rel material:binding = </CalmPresentation/Materials/BaseMaterial>
            double3 xformOp:translate = (0, -0.126, 0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }}
    }}
}}
'''


class ArtifactStore:
    """Constrained artifact writer/reader rooted at one configured directory."""

    def __init__(self, output_root: Path):
        self.root = output_root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._secure_directory(self.root)

    @staticmethod
    def _secure_directory(path: Path) -> None:
        metadata = path.stat()
        if not stat.S_ISDIR(metadata.st_mode):
            raise RuntimeError("artifact path is not a directory")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise RuntimeError("artifact directory is not owned by the service user")
        os.chmod(path, 0o700)
        verified = path.stat()
        if stat.S_IMODE(verified.st_mode) != 0o700:
            raise RuntimeError("artifact directory permissions are not private")

    def _job_dir(self, job_id: str) -> Path:
        if not JOB_ID_PATTERN.fullmatch(job_id):
            raise ValueError("invalid job ID")
        candidate = self.root / job_id
        if candidate.is_symlink():
            raise RuntimeError("artifact job directory must not be a symbolic link")
        target = candidate.resolve()
        if not target.is_relative_to(self.root):
            raise ValueError("artifact path escaped output root")
        return target

    @staticmethod
    def _atomic_write(path: Path, payload: bytes) -> None:
        temporary = path.with_name(f".{path.name}.{os.getpid()}.{secrets.token_hex(8)}.tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            os.chmod(path, 0o600)
            if stat.S_IMODE(path.stat().st_mode) != 0o600:
                raise RuntimeError("artifact file permissions are not private")
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass

    def materialize(
        self,
        job_id: str,
        asset_id: str,
        title: str,
        tier: str,
        recipe: dict[str, Any],
        recipe_sha256: str,
    ) -> dict[str, Any]:
        directory = self._job_dir(job_id)
        directory.mkdir(mode=0o700, exist_ok=True)
        self._secure_directory(directory)
        usda = build_usda(asset_id, title, tier, recipe_sha256).encode("utf-8")
        sidecar_document = {
            "schema_version": "1.0",
            "artifact_role": "abstract_procedural_review_draft",
            "display_authorized": False,
            "review_gate": "specialist_and_human_factors_review_required_before_patient_display",
            "source_asset_mutated": False,
            "recipe": recipe,
        }
        sidecar = json.dumps(sidecar_document, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        self._atomic_write(directory / "scene.usda", usda)
        self._atomic_write(directory / "recipe.json", sidecar)
        return {
            "scene": {"href": f"/v1/artifacts/{job_id}/scene.usda", "bytes": len(usda)},
            "recipe": {"href": f"/v1/artifacts/{job_id}/recipe.json", "bytes": len(sidecar)},
        }

    def read(self, job_id: str, filename: str) -> tuple[bytes, str]:
        if filename not in {"scene.usda", "recipe.json"}:
            raise ValueError("unknown artifact")
        path = (self._job_dir(job_id) / filename).resolve()
        if not path.is_relative_to(self.root) or not path.is_file():
            raise FileNotFoundError(filename)
        media_type = "model/vnd.usda" if filename.endswith(".usda") else "application/json"
        return path.read_bytes(), media_type
