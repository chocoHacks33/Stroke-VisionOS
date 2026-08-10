"""Dependency-free local HTTP transport."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from pathlib import Path
import secrets
import sys
import tempfile
import time
from typing import Any
from urllib.parse import urlsplit

from . import __version__
from .bindings import BindingError, EntityBindingCatalog
from .catalog import AssetCatalog, CatalogError
from .procedural import ArtifactStore, JOB_ID_PATTERN
from .profiles import AdaptationProfileCatalog, ProfileError
from .service import AdaptationService, ServiceError


MAX_REQUEST_BYTES = 16 * 1024
LOGGER = logging.getLogger("adaptive_asset_service")
UI_RESOURCES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/ui": ("index.html", "text/html; charset=utf-8"),
    "/ui/": ("index.html", "text/html; charset=utf-8"),
    "/ui/app.css": ("app.css", "text/css; charset=utf-8"),
    "/ui/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
UI_SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
        "form-action 'self'"
    ),
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Permissions-Policy": (
        "camera=(), microphone=(), geolocation=(), accelerometer=(), gyroscope=(), magnetometer=()"
    ),
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _profile_root() -> Path:
    return Path(__file__).with_name("runtime_profiles")


def _ui_resource(filename: str) -> bytes:
    """Read one packaged, allow-listed UI resource without URL-to-path mapping."""
    return (Path(__file__).with_name("static") / filename).read_bytes()


def log_event(**fields: Any) -> None:
    """Emit allow-listed metadata only; never serialize bodies or client addresses."""
    LOGGER.info(json.dumps(fields, sort_keys=True, separators=(",", ":")))


class AdaptiveHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], service: AdaptationService):
        self.service = service
        super().__init__(address, AdaptiveRequestHandler)

    def server_close(self) -> None:
        self.service.close()
        super().server_close()

    def handle_error(self, _request: object, _client_address: object) -> None:
        """Suppress stdlib tracebacks that disclose client addresses and paths."""
        exception_type = sys.exc_info()[0]
        log_event(
            event="connection_error",
            error_type=exception_type.__name__ if exception_type is not None else "unknown",
        )


class AdaptiveRequestHandler(BaseHTTPRequestHandler):
    server: AdaptiveHTTPServer
    protocol_version = "HTTP/1.1"
    server_version = "AdaptiveAssetService"
    sys_version = ""

    def log_message(self, _format: str, *args: Any) -> None:
        # BaseHTTPRequestHandler includes client IP and raw paths; structured logs
        # are emitted by _finish_log instead.
        return

    def _request_id(self) -> str:
        current = getattr(self, "_active_request_id", None)
        if current is None:
            current = secrets.token_hex(12)
            self._active_request_id = current
        return current

    def _send_bytes(
        self,
        status: int,
        payload: bytes,
        media_type: str,
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", media_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Request-ID", self._request_id())
        if self.close_connection:
            self.send_header("Connection", "close")
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _send_json(self, status: int, document: dict[str, Any]) -> None:
        payload = json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        self._send_bytes(status, payload, "application/json; charset=utf-8")

    def _error(self, error: ServiceError) -> None:
        self._send_json(error.status, error.body(self._request_id()))

    def _path(self) -> str:
        parsed = urlsplit(self.path)
        if parsed.query or parsed.fragment:
            raise ServiceError(400, "query_not_supported", "Query parameters and fragments are not supported")
        return parsed.path

    def _validate_bodyless_request(self) -> None:
        if self.headers.get("Transfer-Encoding") is not None:
            raise ServiceError(400, "transfer_encoding_not_supported", "Transfer-Encoding is not supported")
        content_lengths = self.headers.get_all("Content-Length", [])
        if len(content_lengths) > 1 or (content_lengths and "," in content_lengths[0]):
            raise ServiceError(400, "invalid_content_length", "Send at most one Content-Length header")
        if content_lengths:
            try:
                length = int(content_lengths[0])
            except ValueError as exc:
                raise ServiceError(400, "invalid_content_length", "Content-Length must be an integer") from exc
            if length != 0:
                raise ServiceError(400, "request_body_not_allowed", "GET requests must not contain a body")

    def _read_json(self) -> Any:
        if self.headers.get("Transfer-Encoding") is not None:
            raise ServiceError(
                400,
                "transfer_encoding_not_supported",
                "Transfer-Encoding is not supported; send one Content-Length header",
            )
        media_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if media_type != "application/json":
            raise ServiceError(415, "unsupported_media_type", "Content-Type must be application/json")
        content_lengths = self.headers.get_all("Content-Length", [])
        if not content_lengths:
            raise ServiceError(411, "length_required", "Content-Length is required")
        if len(content_lengths) != 1 or "," in content_lengths[0]:
            raise ServiceError(400, "invalid_content_length", "Send exactly one Content-Length header")
        raw_length = content_lengths[0]
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ServiceError(400, "invalid_content_length", "Content-Length must be an integer") from exc
        if length < 0 or length > MAX_REQUEST_BYTES:
            raise ServiceError(413, "request_too_large", f"Request body limit is {MAX_REQUEST_BYTES} bytes")
        body = self.rfile.read(length)
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ServiceError(400, "invalid_json", "Request body must be valid UTF-8 JSON") from exc

    def _finish_log(self, started: float, status: int, route: str, error_code: str | None = None) -> None:
        event: dict[str, Any] = {
            "event": "http_request",
            "request_id": self._request_id(),
            "method": self.command,
            "route": route,
            "status": status,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }
        if error_code:
            event["error_code"] = error_code
        log_event(**event)

    def do_GET(self) -> None:  # noqa: N802 - stdlib hook name
        self._active_request_id = secrets.token_hex(12)
        started = time.perf_counter()
        status = 500
        route = "unmatched"
        error_code: str | None = None
        try:
            self._validate_bodyless_request()
            path = self._path()
            if path in UI_RESOURCES:
                filename, media_type = UI_RESOURCES[path]
                route = "/ui" if filename == "index.html" else f"/ui/{filename}"
                status = 200
                self._send_bytes(
                    status,
                    _ui_resource(filename),
                    media_type,
                    extra_headers=UI_SECURITY_HEADERS,
                )
                return

            if path == "/healthz":
                route = "/healthz"
                status = 200
                self._send_json(
                    status,
                    {
                        "status": "ok",
                        "service": "adaptive-asset-service",
                        "version": __version__,
                        "catalog": {
                            "assets": self.server.service.catalog.asset_count,
                            "manifests": self.server.service.catalog.manifest_count,
                        },
                        "adaptation_mapping": {
                            "configured": self.server.service.executable_mapping_available,
                            "profiled_assets": (
                                self.server.service.profiles.asset_count
                                if self.server.service.profiles is not None
                                else 0
                            ),
                            "entity_mapped_assets": (
                                self.server.service.bindings.asset_count
                                if self.server.service.bindings is not None
                                else 0
                            ),
                        },
                        "diagnostic_inference": False,
                    },
                )
                return

            if path == "/v1/catalog":
                route = "/v1/catalog"
                status = 200
                self._send_json(
                    status,
                    {
                        "catalog": {
                            "assets": self.server.service.catalog.asset_count,
                            "manifests": self.server.service.catalog.manifest_count,
                        },
                        "assets": self.server.service.public_assets(),
                    },
                )
                return

            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[:2] == ["v1", "jobs"] and JOB_ID_PATTERN.fullmatch(parts[2]):
                route = "/v1/jobs/{job_id}"
                job = self.server.service.get_job(parts[2])
                if job is None:
                    raise ServiceError(404, "job_not_found", "Generation job was not found")
                status = 200
                self._send_json(status, {"request_id": self._request_id(), **job})
                return

            if (
                len(parts) == 4
                and parts[:2] == ["v1", "artifacts"]
                and JOB_ID_PATTERN.fullmatch(parts[2])
                and parts[3] in {"scene.usda", "recipe.json"}
            ):
                route = "/v1/artifacts/{job_id}/{filename}"
                job = self.server.service.get_job(parts[2])
                if job is None or job.get("status") != "awaiting_clinician_review":
                    raise ServiceError(404, "draft_not_ready", "Draft artifact is not ready for clinical review")
                try:
                    payload, media_type = self.server.service.artifacts.read(parts[2], parts[3])
                except (ValueError, FileNotFoundError) as exc:
                    raise ServiceError(404, "artifact_not_found", "Draft artifact was not found") from exc
                status = 200
                self._send_bytes(
                    status,
                    payload,
                    media_type,
                    extra_headers={
                        "Content-Disposition": f'attachment; filename="{parts[3]}"',
                        "X-Display-Authorized": "false",
                        "X-Clinical-Review-Required": "true",
                    },
                )
                return

            raise ServiceError(404, "route_not_found", "Route was not found")
        except ServiceError as exc:
            status, error_code = exc.status, exc.code
            self.close_connection = True
            self._error(exc)
        finally:
            self._finish_log(started, status, route, error_code)

    def do_POST(self) -> None:  # noqa: N802 - stdlib hook name
        self._active_request_id = secrets.token_hex(12)
        started = time.perf_counter()
        status = 500
        route = "unmatched"
        error_code: str | None = None
        try:
            path = self._path()
            if path not in {"/v1/visual-adaptations", "/v1/adaptations"}:
                raise ServiceError(404, "route_not_found", "Route was not found")
            route = "/v1/visual-adaptations"
            payload = self._read_json()
            status, response = self.server.service.adapt(payload, self._request_id())
            if path == "/v1/adaptations":
                response["endpoint_alias"] = {
                    "used": "/v1/adaptations",
                    "canonical": "/v1/visual-adaptations",
                }
            self._send_json(status, response)
        except ServiceError as exc:
            status, error_code = exc.status, exc.code
            # A rejected POST may leave unread attacker-controlled bytes in the
            # socket. Never reinterpret them as a pipelined request.
            self.close_connection = True
            self._error(exc)
        finally:
            self._finish_log(started, status, route, error_code)


def build_server(
    host: str,
    port: int,
    catalog_root: Path,
    output_root: Path,
    profile_path: Path | None = None,
    bindings_path: Path | None = None,
) -> AdaptiveHTTPServer:
    catalog = AssetCatalog(catalog_root)
    profiles = AdaptationProfileCatalog(profile_path, catalog) if profile_path is not None else None
    bindings = EntityBindingCatalog(bindings_path, catalog) if bindings_path is not None else None
    service = AdaptationService(catalog, ArtifactStore(output_root), profiles, bindings)
    return AdaptiveHTTPServer((host, port), service)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local adaptive asset presentation endpoint")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address; loopback is the safe default")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument(
        "--catalog-root",
        type=Path,
        default=_repo_root() / "RealityKitContent" / "Assets",
        help="Read-only root containing asset_manifest*.json",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(tempfile.gettempdir()) / "stroke-vision-adaptive-assets",
        help="Runtime directory for clinician-review drafts",
    )
    parser.add_argument(
        "--profile-map",
        type=Path,
        default=_profile_root() / "catalog_adaptation_profiles.json",
        help="Catalog-wide allowed-action and replacement profiles",
    )
    parser.add_argument(
        "--entity-bindings",
        type=Path,
        default=_profile_root() / "realitykit_entity_bindings.json",
        help="Exact package-revision-bound RealityKit entity selectors",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        LOGGER.warning(
            json.dumps(
                {
                    "event": "security_warning",
                    "message": "Service has no authentication; bind to loopback unless protected by an approved gateway.",
                },
                separators=(",", ":"),
            )
        )
    try:
        server = build_server(
            args.host,
            args.port,
            args.catalog_root,
            args.output_root,
            args.profile_map,
            args.entity_bindings,
        )
    except (CatalogError, ProfileError, BindingError, OSError, RuntimeError) as exc:
        raise SystemExit(f"startup failed: {exc}") from exc
    LOGGER.info(
        json.dumps(
            {
                "event": "service_started",
                "host": args.host,
                "port": server.server_port,
                "assets": server.service.catalog.asset_count,
                "executable_mapping": server.service.executable_mapping_available,
            },
            separators=(",", ":"),
        )
    )
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
