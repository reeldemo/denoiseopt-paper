#!/usr/bin/env python3
"""CLI preflight: verify n2n_seam compat shim after PYTHONPATH is set."""
from __future__ import annotations

import baselines.n2n_seam as n2n_seam  # noqa: E402
from n2n_seam_compat import preflight_seam_n2n_from_state

if __name__ == "__main__":
    preflight_seam_n2n_from_state(n2n_seam)
    print("OK n2n_seam compat: SeamN2N.from_state")
