"""Loaded automatically by Python's site hook when scripts/compat is on PYTHONPATH.

Patches reelsynth @ 0a8567b so legacy benches can call SeamN2N.from_state(...).
"""
from __future__ import annotations


def _bootstrap() -> None:
    try:
        import baselines.n2n_seam as n2n_seam  # noqa: WPS433 — intentional compat hook
    except ImportError:
        return
    from n2n_seam_compat import patch_seam_n2n_if_needed

    patch_seam_n2n_if_needed(n2n_seam)


_bootstrap()
