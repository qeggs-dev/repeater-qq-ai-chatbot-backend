import ssl
from pydantic import BaseModel
from typing import Any, Literal

class ServerConfig(BaseModel):
    host: str | None = None
    port: int | None = None
    uds: str | None = None
    fd: int | None = None
    loop: Literal["none", "auto", "asyncio", "uvloop"] | str = "auto"
    http: Literal["auto", "h11", "httptools"] | str = "auto"
    ws: Literal["auto", "none", "websockets", "websockets-sansio", "wsproto"] | str = "auto"
    ws_max_size: int = 16 * 1024 * 1024
    ws_max_queue: int = 32
    ws_ping_interval: float | None = 20
    ws_ping_timeout: float | None = 20
    ws_per_message_deflate: bool = True
    lifespan: Literal["auto", "on", "off"] = "auto"
    env_file: str | None = None
    log_config: dict[str, Any] | str | None = None
    log_level: str | int | None = None
    access_log: bool = True
    use_colors: bool | None = None
    interface: Literal["auto", "asgi3", "asgi2", "wsgi"] = "auto"
    reload: bool | None = None
    reload_dirs: list[str] | str | None = None
    reload_delay: float = 0.25
    reload_includes: list[str] | str | None = None
    reload_excludes: list[str] | str | None = None
    workers: int | None = None
    proxy_headers: bool = True
    server_header: bool = True
    date_header: bool = True
    forwarded_allow_ips: list[str] | str | None = None
    root_path: str = ""
    limit_concurrency: int | None = None
    limit_max_requests: int | None = None
    backlog: int = 2048
    timeout_keep_alive: int = 5
    timeout_notify: int = 30
    timeout_graceful_shutdown: int | None = None
    timeout_worker_healthcheck: int = 5
    ssl_keyfile: str | None = None
    ssl_certfile: str | None = None
    ssl_keyfile_password: str | None = None
    ssl_version: int = ssl.PROTOCOL_TLS_SERVER
    ssl_cert_reqs: int = ssl.CERT_NONE
    ssl_ca_certs: str | None = None
    ssl_ciphers: str = "TLSv1"
    headers: list[tuple[str, str]] | None = None
    factory: bool = False
    h11_max_incomplete_event_size: int | None = None
    restart: bool = False
    run_server: bool = True
    asyncio_debug: bool = False