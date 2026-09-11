from __future__ import annotations

import ipaddress
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.metrics import increment_metric


@dataclass(frozen=True)
class RateLimitPolicy:
    name: str
    requests: int
    window_seconds: int


class RateLimitStore(Protocol):
    def hit(
        self,
        key: str,
        window_seconds: int,
    ) -> tuple[int, int]:
        """Return current hit count and retry-after seconds."""


class MemoryRateLimitStore:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def hit(
        self,
        key: str,
        window_seconds: int,
    ) -> tuple[int, int]:
        now = time.monotonic()
        bucket = self._hits[key]

        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()

        bucket.append(now)

        retry_after = max(
            1,
            int(window_seconds - (now - bucket[0])),
        )

        return len(bucket), retry_after


class RedisRateLimitStore:
    def __init__(
        self,
        redis_url: str | None,
        prefix: str,
    ) -> None:
        if not redis_url:
            raise RuntimeError(
                "RATE_LIMIT_REDIS_URL es obligatorio "
                "cuando RATE_LIMIT_BACKEND=redis."
            )

        try:
            from redis import Redis
        except ImportError as exc:
            raise RuntimeError(
                "Instale redis para usar "
                "RATE_LIMIT_BACKEND=redis."
            ) from exc

        self._client = Redis.from_url(
            redis_url,
            decode_responses=True,
        )

        self._prefix = prefix.rstrip(":")

    def hit(
        self,
        key: str,
        window_seconds: int,
    ) -> tuple[int, int]:
        redis_key = f"{self._prefix}:{key}"

        pipe = self._client.pipeline()
        pipe.incr(redis_key)
        pipe.ttl(redis_key)

        count, ttl = pipe.execute()

        if int(ttl) < 0:
            self._client.expire(
                redis_key,
                window_seconds,
            )
            ttl = window_seconds

        return (
            int(count),
            max(1, int(ttl)),
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limit por IP.

    Producción:
        Redis.

    Desarrollo:
        Memoria.

    Cuando el backend está detrás de proxies reversos,
    X-Forwarded-For/X-Real-IP solo se aceptan si la conexión
    inmediata proviene de una red incluida en
    TRUSTED_PROXY_NETWORKS.
    """

    def __init__(
        self,
        app,
        *,
        store: RateLimitStore,
        default_policy: RateLimitPolicy,
        login_policy: RateLimitPolicy,
        public_report_policy: RateLimitPolicy,
        upload_policy: RateLimitPolicy,
    ) -> None:
        super().__init__(app)

        self.store = store

        self.default_policy = default_policy
        self.login_policy = login_policy
        self.public_report_policy = public_report_policy
        self.upload_policy = upload_policy

    # ============================================================
    # UTILIDADES DE IP
    # ============================================================

    @staticmethod
    def _parse_ip(
        value: str | None,
    ) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
        """
        Convierte una representación de IP a objeto ipaddress.

        También normaliza IPv4 mapeadas como IPv6:

            ::ffff:192.168.1.10

        a:

            192.168.1.10
        """

        if not value:
            return None

        raw = str(value).strip().strip('"')

        if not raw:
            return None

        # IPv6 entre corchetes:
        # [2001:db8::1]
        if raw.startswith("[") and "]" in raw:
            raw = raw[1 : raw.index("]")]

        try:
            address = ipaddress.ip_address(raw)
        except ValueError:
            # Tolerar IPv4:puerto si algún proxy lo enviara.
            if raw.count(":") == 1 and "." in raw:
                host, port = raw.rsplit(":", 1)

                if port.isdigit():
                    try:
                        address = ipaddress.ip_address(host)
                    except ValueError:
                        return None
                else:
                    return None
            else:
                return None

        if (
            isinstance(address, ipaddress.IPv6Address)
            and address.ipv4_mapped is not None
        ):
            return address.ipv4_mapped

        return address

    @staticmethod
    def _trusted_proxy_networks():
        """
        Obtiene las redes proxy configuradas y validadas
        previamente por app.config.Settings.
        """

        from app.config import settings

        networks = []

        for value in getattr(
            settings,
            "TRUSTED_PROXY_NETWORKS",
            [],
        ):
            networks.append(
                ipaddress.ip_network(
                    value,
                    strict=False,
                )
            )

        return networks

    @staticmethod
    def _is_trusted_proxy(
        address: ipaddress.IPv4Address | ipaddress.IPv6Address,
        trusted_networks,
    ) -> bool:
        """
        Determina si una IP pertenece a alguna red
        explícitamente autorizada como proxy.
        """

        for network in trusted_networks:
            if address.version != network.version:
                continue

            if address in network:
                return True

        return False

    def _forwarded_client_ip(
        self,
        forwarded: str,
        trusted_networks,
    ) -> str | None:
        """
        Obtiene de forma segura la IP original desde
        X-Forwarded-For.

        La cadena se procesa de DERECHA A IZQUIERDA.

        Ejemplo:

            181.50.10.20, 10.0.3.5

        Si 10.0.3.5 pertenece a una red proxy confiable,
        se descarta y se devuelve:

            181.50.10.20

        Este enfoque evita confiar ciegamente en la primera
        dirección enviada por el cliente.
        """

        addresses = []

        for item in forwarded.split(","):
            address = self._parse_ip(item)

            if address is not None:
                addresses.append(address)

        if not addresses:
            return None

        # La dirección más a la derecha es el salto más cercano.
        # Eliminamos proxies confiables hasta encontrar al cliente.
        for address in reversed(addresses):
            if self._is_trusted_proxy(
                address,
                trusted_networks,
            ):
                continue

            return str(address)

        # Si absolutamente todas las IP del encabezado
        # pertenecen a redes proxy confiables, no tenemos
        # evidencia suficiente de una IP cliente.
        return None

    # ============================================================
    # IDENTIFICACIÓN DEL CLIENTE
    # ============================================================

    def _client_key(
        self,
        request: Request,
    ) -> str:
        """
        Determina la IP que se utilizará para el rate limit.

        Regla crítica de seguridad:

        Los encabezados X-Forwarded-For y X-Real-IP se ignoran
        completamente si la conexión inmediata NO viene desde
        TRUSTED_PROXY_NETWORKS.
        """

        trusted_networks = self._trusted_proxy_networks()

        peer_raw = (
            request.client.host
            if request.client
            else None
        )

        peer_ip = self._parse_ip(peer_raw)

        if peer_ip is None:
            return "unknown"

        # --------------------------------------------------------
        # La conexión directa NO viene de un proxy confiable.
        #
        # Nunca confiar en cabeceras Forwarded enviadas
        # directamente por un cliente.
        # --------------------------------------------------------

        if not self._is_trusted_proxy(
            peer_ip,
            trusted_networks,
        ):
            return str(peer_ip)

        # --------------------------------------------------------
        # X-FORWARDED-FOR
        # --------------------------------------------------------

        forwarded = request.headers.get(
            "x-forwarded-for"
        )

        if forwarded:
            client_ip = self._forwarded_client_ip(
                forwarded,
                trusted_networks,
            )

            if client_ip:
                return client_ip

        # --------------------------------------------------------
        # X-REAL-IP
        #
        # Se usa únicamente como fallback y solo si contiene una
        # IP que NO pertenece también a las redes de proxy.
        #
        # En nuestra arquitectura actual Nginx puede recibir aquí
        # la IP interna de Traefik; esa dirección no debe
        # convertirse en la identidad del usuario.
        # --------------------------------------------------------

        real_ip_header = request.headers.get(
            "x-real-ip"
        )

        real_ip = self._parse_ip(
            real_ip_header
        )

        if (
            real_ip is not None
            and not self._is_trusted_proxy(
                real_ip,
                trusted_networks,
            )
        ):
            return str(real_ip)

        # --------------------------------------------------------
        # Fallback seguro.
        #
        # Si no fue posible demostrar una IP cliente válida,
        # utilizamos la IP del peer inmediato.
        # --------------------------------------------------------

        return str(peer_ip)

    # ============================================================
    # POLÍTICAS POR ENDPOINT
    # ============================================================

    def _policy_for_path(
        self,
        method: str,
        path: str,
    ) -> RateLimitPolicy | None:
        if path in {
            "/health",
            "/",
        }:
            return None

        path_lower = path.lower()
        method_upper = method.upper()

        # --------------------------------------------------------
        # CORS preflight
        #
        # No representa una operación de negocio y no debe
        # consumir cuota del endpoint.
        # --------------------------------------------------------

        if method_upper == "OPTIONS":
            return None

        # --------------------------------------------------------
        # LOGIN
        # --------------------------------------------------------

        if path_lower.startswith(
            "/auth/login"
        ):
            return self.login_policy

        # --------------------------------------------------------
        # REPORTE ANÓNIMO SST
        #
        # El catálogo público es necesario para renderizar
        # el formulario.
        # --------------------------------------------------------

        if (
            method_upper == "GET"
            and path_lower
            == "/reporte-anonimo-sst/opciones"
        ):
            return None

        # La creación real del reporte sí utiliza
        # una política estricta.
        if (
            method_upper == "POST"
            and path_lower.startswith(
                "/reporte-anonimo-sst"
            )
        ):
            return self.public_report_policy

        # --------------------------------------------------------
        # UPLOADS / EVIDENCIAS
        # --------------------------------------------------------

        if (
            method_upper
            in {
                "POST",
                "PUT",
                "PATCH",
            }
            and (
                "upload" in path_lower
                or "evidencia" in path_lower
                or "archivo" in path_lower
                or path_lower.startswith(
                    "/uploads"
                )
            )
        ):
            return self.upload_policy

        # --------------------------------------------------------
        # POLÍTICA GENERAL
        # --------------------------------------------------------

        return self.default_policy

    # ============================================================
    # MIDDLEWARE
    # ============================================================

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[
            [Request],
            Awaitable[Response],
        ],
    ) -> Response:
        policy = self._policy_for_path(
            request.method,
            request.url.path,
        )

        if policy is None:
            return await call_next(request)

        client_key = self._client_key(
            request
        )

        key = (
            f"{policy.name}:"
            f"{client_key}"
        )

        count, retry_after = self.store.hit(
            key,
            policy.window_seconds,
        )

        if count > policy.requests:
            increment_metric(
                "rate_limit_exceeded_total"
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Demasiadas solicitudes. "
                        "Intente nuevamente en unos segundos."
                    ),
                    "code": "RATE_LIMIT_EXCEEDED",
                },
                headers={
                    "Retry-After": str(
                        retry_after
                    )
                },
            )

        return await call_next(request)


__all__ = [
    "MemoryRateLimitStore",
    "RateLimitMiddleware",
    "RateLimitPolicy",
    "RedisRateLimitStore",
]