"""Read-only, traversal-safe, revision-aware manifest index."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, BinaryIO


ASSET_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


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
    manifest_path: Path
    package_name: str
    package_bytes: int
    package_sha256: str
    package_integrity: str
    package_path: Path

    def public_dict(self) -> dict[str, str | int]:
        return {
            "asset_id": self.asset_id,
            "title": self.title,
            "module": self.module,
            "description": self.description,
            "clinical_review_status": self.clinical_review_status,
            "package_name": self.package_name,
            "package_bytes": self.package_bytes,
            "package_sha256": self.package_sha256,
            "package_integrity": self.package_integrity,
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

    @property
    def asset_ids(self) -> frozenset[str]:
        return frozenset(self._assets)

    def get(self, asset_id: str) -> CatalogAsset | None:
        if not valid_asset_id(asset_id):
            return None
        return self._assets.get(asset_id)

    def public_assets(self) -> list[dict[str, str | int]]:
        """Return a stable, path-free catalog view."""
        return [self._assets[asset_id].public_dict() for asset_id in sorted(self._assets)]

    def current_package_revision(self, asset_id: str) -> tuple[int, str] | None:
        """Re-observe one package so a selection never relies on a stale startup digest."""
        asset = self.get(asset_id)
        if asset is None:
            return None
        try:
            resolved = asset.package_path.resolve(strict=True)
            if resolved != asset.package_path or not resolved.is_file():
                raise CatalogError(f"asset {asset_id} package binding changed after startup")
            revision = self._stable_package_revision(resolved)
        except (OSError, RuntimeError) as exc:
            raise CatalogError(f"asset {asset_id} package became unreadable after startup") from exc
        return revision

    @staticmethod
    def _hash_open_file(handle: BinaryIO) -> str:
        digest = hashlib.sha256()
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _file_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int]:
        return (
            metadata.st_dev,
            metadata.st_ino,
            metadata.st_size,
            metadata.st_mtime_ns,
            metadata.st_ctime_ns,
        )

    @classmethod
    def _stable_package_revision(cls, path: Path) -> tuple[int, str]:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            sha256 = cls._hash_open_file(handle)
            after_handle = os.fstat(handle.fileno())
            after_path = path.stat()
        identity = cls._file_identity(before)
        if (
            before.st_size <= 0
            or identity != cls._file_identity(after_handle)
            or identity != cls._file_identity(after_path)
        ):
            raise CatalogError("package changed while its revision was observed")
        return before.st_size, sha256

    @classmethod
    def _package_record(
        cls,
        manifest_path: Path,
        asset_id: str,
        record: dict[str, Any],
        digest_cache: dict[Path, tuple[int, str]],
    ) -> tuple[Path, int, str, str]:
        package = record.get("usdz")
        if (
            not isinstance(package, str)
            or not package
            or "\\" in package
            or Path(package).is_absolute()
            or ".." in Path(package).parts
        ):
            raise CatalogError(f"asset {asset_id} in {manifest_path.name} has no safe USDZ path")
        try:
            package_path = (manifest_path.parent / package).resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise CatalogError(
                f"asset {asset_id} in {manifest_path.name} has no readable USDZ package"
            ) from exc
        if not package_path.is_relative_to(manifest_path.parent) or not package_path.is_file():
            raise CatalogError(f"asset {asset_id} in {manifest_path.name} has an unsafe USDZ package")
        if package_path.suffix.lower() != ".usdz":
            raise CatalogError(f"asset {asset_id} in {manifest_path.name} does not reference a USDZ package")

        cached = digest_cache.get(package_path)
        if cached is None:
            try:
                cached = cls._stable_package_revision(package_path)
            except OSError as exc:
                raise CatalogError(
                    f"asset {asset_id} in {manifest_path.name} has no readable USDZ package"
                ) from exc
            digest_cache[package_path] = cached
        package_bytes, package_sha256 = cached
        if package_bytes <= 0:
            raise CatalogError(f"asset {asset_id} in {manifest_path.name} has an empty USDZ package")

        expected_bytes = record.get("usdz_bytes")
        if expected_bytes is not None:
            if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
                raise CatalogError(f"asset {asset_id} in {manifest_path.name} has invalid usdz_bytes")
            if expected_bytes != package_bytes:
                raise CatalogError(f"asset {asset_id} in {manifest_path.name} has a USDZ byte-count mismatch")

        expected_sha256 = record.get("usdz_sha256")
        if expected_sha256 is not None:
            if not isinstance(expected_sha256, str) or not SHA256_PATTERN.fullmatch(expected_sha256):
                raise CatalogError(f"asset {asset_id} in {manifest_path.name} has invalid usdz_sha256")
            if expected_sha256 != package_sha256:
                raise CatalogError(f"asset {asset_id} in {manifest_path.name} has a USDZ SHA-256 mismatch")

        if expected_bytes is not None and expected_sha256 is not None:
            integrity = "verified_against_manifest"
        elif expected_bytes is not None or expected_sha256 is not None:
            integrity = "partially_verified_against_manifest"
        else:
            integrity = "observed_without_manifest_digest"
        return package_path, package_bytes, package_sha256, integrity

    def reload(self) -> None:
        assets: dict[str, CatalogAsset] = {}
        manifest_count = 0
        digest_cache: dict[Path, tuple[int, str]] = {}
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
                package_path, package_bytes, package_sha256, package_integrity = self._package_record(
                    resolved,
                    asset_id,
                    record,
                    digest_cache,
                )
                assets[asset_id] = CatalogAsset(
                    asset_id=asset_id,
                    title=str(record.get("title", asset_id)),
                    module=str(record.get("module", manifest_module)),
                    description=str(record.get("description", "")),
                    clinical_review_status=str(record.get("clinical_review_status", manifest_status)),
                    manifest_name=resolved.name,
                    manifest_path=resolved,
                    package_name=package_path.name,
                    package_bytes=package_bytes,
                    package_sha256=package_sha256,
                    package_integrity=package_integrity,
                    package_path=package_path,
                )
        if not assets:
            raise CatalogError("catalog contains no assets")
        self._assets = assets
        self._manifest_count = manifest_count
