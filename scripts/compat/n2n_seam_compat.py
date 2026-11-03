"""Reelsynth 0a8567b compat: expose module-level from_state as SeamN2N.from_state."""
from __future__ import annotations

from typing import Any


def patch_seam_n2n_if_needed(n2n_seam: Any) -> bool:
    """Patch SeamN2N.from_state when only n2n_seam.from_state exists (pin 0a8567b).

    Returns True if SeamN2N.from_state is callable after this function returns.
    Idempotent — safe to call multiple times.
    """
    mod_fn = getattr(n2n_seam, "from_state", None)
    if mod_fn is None or not callable(mod_fn):
        return False
    cls = getattr(n2n_seam, "SeamN2N", None)
    if cls is None:
        return False
    existing = getattr(cls, "from_state", None)
    if existing is not None and callable(existing):
        return True
    cls.from_state = staticmethod(mod_fn)  # type: ignore[method-assign]
    patched = getattr(cls, "from_state", None)
    return patched is not None and callable(patched)


def preflight_seam_n2n_from_state(n2n_seam: Any) -> None:
    if not patch_seam_n2n_if_needed(n2n_seam):
        raise RuntimeError("n2n_seam compat: could not install SeamN2N.from_state")
    if not hasattr(n2n_seam.SeamN2N, "from_state") or not callable(n2n_seam.SeamN2N.from_state):
        raise RuntimeError("n2n_seam compat: SeamN2N.from_state missing after shim")
