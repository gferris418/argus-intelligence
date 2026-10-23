"""Verify ATLAS remote capability-v2 tokens against the pinned integration projection."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from collections.abc import Callable
from pathlib import Path
from threading import Lock
from typing import Any, Protocol

import yaml


ROOT = Path(__file__).resolve().parents[1]
CURRENT_INTEGRATION_PATH = ROOT / "contracts" / "atlas" / "current-integration.yaml"


class CapabilityError(ValueError):
    pass


class CapabilityReplayError(CapabilityError):
    pass


class ReplayGuard(Protocol):
    def consume(self, jti: str, exp: int, now: int) -> bool: ...


class InMemoryReplayGuard:
    """Process-local replay guard; remote clusters should supply a shared atomic store."""

    def __init__(self) -> None:
        self._seen: dict[str, int] = {}
        self._lock = Lock()

    def consume(self, jti: str, exp: int, now: int) -> bool:
        with self._lock:
            expired = [key for key, deadline in self._seen.items() if deadline < now]
            for key in expired:
                del self._seen[key]
            if jti in self._seen:
                return False
            self._seen[jti] = exp
            return True


def load_remote_capability_policy(path: Path = CURRENT_INTEGRATION_PATH) -> dict[str, Any]:
    descriptor = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(descriptor, dict) or descriptor.get("status") != "CURRENT":
        raise CapabilityError("ATLAS integration projection must be CURRENT")
    policy = descriptor.get("contract", {}).get("remote_capability")
    if not isinstance(policy, dict):
        raise CapabilityError("ATLAS integration projection lacks remote capability policy")
    required = {
        "version", "algorithm", "issuer", "subject", "audience", "capability", "scope",
        "one_time", "max_ttl_seconds", "max_clock_skew_seconds",
    }
    if not required.issubset(policy):
        raise CapabilityError("ATLAS remote capability policy is incomplete")
    if policy.get("one_time") is not True:
        raise CapabilityError("ATLAS remote capability policy must require one-time use")
    return dict(policy)


def _b64url_decode(value: str) -> bytes:
    try:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode((value + padding).encode("ascii"))
    except Exception as exc:
        raise CapabilityError("invalid capability encoding") from exc


def _intent_hash(intent: str) -> str:
    if not isinstance(intent, str) or not intent.strip():
        raise CapabilityError("intent must be a non-empty string")
    return hashlib.sha256(intent.encode("utf-8")).hexdigest()


def _validate_secret(secret: bytes) -> bytes:
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise CapabilityError("capability secret must be at least 32 bytes")
    return secret


def verify_remote_capability(
    token: str,
    secret_resolver: Callable[[str], bytes | None],
    *,
    task_id: str,
    intent: str,
    replay_guard: ReplayGuard,
    now: int,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(token, str):
        raise CapabilityError("capability must be a string")
    parts = token.split(".")
    if len(parts) != 3:
        raise CapabilityError("capability must have exactly three segments")
    if not callable(secret_resolver):
        raise CapabilityError("secret_resolver must be callable")
    if not callable(getattr(replay_guard, "consume", None)):
        raise CapabilityError("replay_guard must provide consume(jti, exp, now)")
    if isinstance(now, bool) or not isinstance(now, int) or now < 0:
        raise CapabilityError("now must be a non-negative integer timestamp")

    try:
        header = json.loads(_b64url_decode(parts[0]).decode("utf-8"))
        claims = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CapabilityError("capability contains invalid JSON") from exc
    if not isinstance(header, dict) or not isinstance(claims, dict):
        raise CapabilityError("capability segments must decode to objects")

    effective_policy = dict(policy or load_remote_capability_policy())
    if header.get("alg") != effective_policy["algorithm"] or header.get("typ") != "ATLAS-CAP":
        raise CapabilityError("unsupported capability header")
    key_id = header.get("kid")
    if not isinstance(key_id, str) or not key_id:
        raise CapabilityError("capability key id is required")
    secret = secret_resolver(key_id)
    if secret is None:
        raise CapabilityError("unknown capability key id")
    secret = _validate_secret(secret)

    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    expected = hmac.new(secret, signing_input, hashlib.sha256).digest()
    supplied = _b64url_decode(parts[2])
    if not hmac.compare_digest(expected, supplied):
        raise CapabilityError("capability signature mismatch")

    required_claims = {
        "v", "iss", "sub", "aud", "capability", "scope", "task_id",
        "intent_hash", "iat", "exp", "jti",
    }
    if not required_claims.issubset(claims):
        raise CapabilityError("capability is missing required claims")
    expected_claims = {
        "v": effective_policy["version"],
        "iss": effective_policy["issuer"],
        "sub": effective_policy["subject"],
        "aud": effective_policy["audience"],
        "capability": effective_policy["capability"],
        "scope": effective_policy["scope"],
    }
    for key, expected_value in expected_claims.items():
        if claims.get(key) != expected_value:
            raise CapabilityError(f"capability {key} mismatch")
    if claims["task_id"] != task_id:
        raise CapabilityError("capability task mismatch")
    if claims["intent_hash"] != _intent_hash(intent):
        raise CapabilityError("capability intent mismatch")

    issued_at = claims["iat"]
    expires_at = claims["exp"]
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (issued_at, expires_at)):
        raise CapabilityError("capability timestamps must be integers")
    max_ttl = int(effective_policy["max_ttl_seconds"])
    if expires_at <= issued_at or expires_at - issued_at > max_ttl:
        raise CapabilityError("capability lifetime exceeds policy")
    max_skew = int(effective_policy["max_clock_skew_seconds"])
    if now < issued_at - max_skew:
        raise CapabilityError("capability is not yet valid")
    if now > expires_at:
        raise CapabilityError("capability has expired")

    jti = claims["jti"]
    if not isinstance(jti, str) or not jti:
        raise CapabilityError("capability jti is required")
    if not replay_guard.consume(jti, expires_at, now):
        raise CapabilityReplayError("capability replay detected")
    return dict(claims)


__all__ = [
    "CapabilityError",
    "CapabilityReplayError",
    "InMemoryReplayGuard",
    "ReplayGuard",
    "load_remote_capability_policy",
    "verify_remote_capability",
]
