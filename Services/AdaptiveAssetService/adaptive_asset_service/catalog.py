"""Read-only, traversal-safe manifest index."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


ASSET_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


class CatalogError(RuntimeError):
    """The catalog could not be indexed safely."""


@dataclass(frozen=True)
class CatalogAsset:
    asset_id: str
    title: str
    module: str
    description: str
    clinical_review_status: str
    manifest_name: str
    package_name: str | None

    def public_dict(self) -> dict[str, str | None]:
        return {
            "asset_id": self.asset_id,
            "title": self.title,
            "module": self.module,
            "description": self.description,
            "clinical_review_status": self.clinical_review_status,
            "package_name": self.package_name,
        }


def valid_asset_id(value: Any) -> bool:
    """Asset IDs are identifiers, never file paths."""
    return (
        isinstance(value, str)
        and bool(ASSET_ID_PATTERN.fullmatch(value))
        and ".." not in value
        and "/" not in value
        and "\\" not in value
    )


class AssetCatalog:
    """Indexes every ``asset_manifest*.json`` under a fixed catalog root."""

    def __init__(self, catalog_root: Path):
        root = catalog_root.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise CatalogError(f"catalog root is not a directory: {root}")
        self.root = root
        self._assets: dict[str, CatalogAsset] = {}
        self._manifest_count = 0
        self.reload()

    @property
    def asset_count(self) -> int:
        return len(self._assets)

    @property
    def manifest_count(self) -> int:
        return self._manifest_count

    def get(self, asset_id: str) -> CatalogAsset | None:
        if not valid_asset_id(asset_id):
            return None
        return self._assets.get(asset_id)

    def reload(self) -> None:
        assets: dict[str, CatalogAsset] = {}
        manifest_count = 0
        for manifest_path in sorted(self.root.rglob("asset_manifest*.json")):
            resolved = manifest_path.resolve(strict=True)
            if not resolved.is_relative_to(self.root) or not resolved.is_file():
                raise CatalogError("manifest escaped the configured catalog root")
            try:
                document = json.loads(resolved.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise CatalogError(f"invalid manifest {resolved.name}: {exc}") from exc
            records = document.get("assets") if isinstance(document, dict) else None
            if not isinstance(records, list):
                raise CatalogError(f"manifest {resolved.name} has no assets array")
            manifest_count += 1
            manifest_module = str(document.get("module", document.get("kit", "unspecified")))
            manifest_status = str(document.get("clinical_review_status", "not_recorded"))
            for record in records:
                if not isinstance(record, dict) or not valid_asset_id(record.get("id")):
                    raise CatalogError(f"manifest {resolved.name} contains an invalid asset ID")
                asset_id = record["id"]
                if asset_id in assets:
                    raise CatalogError(f"duplicate asset ID in catalog: {asset_id}")
                package = record.get("usdz")
                package_name = Path(package).name if isinstance(package, str) else None
                assets[asset_id] = CatalogAsset(
                    asset_id=asset_id,
                    title=str(record.get("title", asset_id)),
                    module=str(record.get("module", manifest_module)),
                    description=str(record.get("description", "")),
                    clinical_review_status=str(record.get("clinical_review_status", manifest_status)),
                    manifest_name=resolved.name,
                    package_name=package_name,
                )
        if not assets:
            raise CatalogError("catalog contains no assets")
        self._assets = assets
        self._manifest_count = manifest_count
