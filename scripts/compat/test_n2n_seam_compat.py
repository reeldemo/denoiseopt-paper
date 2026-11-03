#!/usr/bin/env python3
"""Unit tests for n2n_seam_compat (no reelsynth / torch required)."""
from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from n2n_seam_compat import patch_seam_n2n_if_needed, preflight_seam_n2n_from_state


class TestN2nSeamCompat(unittest.TestCase):
    def test_patches_missing_class_from_state(self) -> None:
        mod_fn = MagicMock(return_value="model")

        class SeamN2N:
            pass

        n2n_seam = SimpleNamespace(from_state=mod_fn, SeamN2N=SeamN2N)
        self.assertFalse(hasattr(SeamN2N, "from_state"))
        self.assertTrue(patch_seam_n2n_if_needed(n2n_seam))
        self.assertTrue(hasattr(SeamN2N, "from_state") and callable(SeamN2N.from_state))
        out = SeamN2N.from_state({"w": 1}, "cpu")
        mod_fn.assert_called_once_with({"w": 1}, "cpu")
        self.assertEqual(out, "model")

    def test_idempotent_when_already_patched(self) -> None:
        mod_fn = MagicMock(return_value="model")

        class SeamN2N:
            pass

        n2n_seam = SimpleNamespace(from_state=mod_fn, SeamN2N=SeamN2N)
        patch_seam_n2n_if_needed(n2n_seam)
        first = SeamN2N.from_state
        self.assertTrue(patch_seam_n2n_if_needed(n2n_seam))
        self.assertIs(SeamN2N.from_state, first)

    def test_preflight_raises_when_no_module_fn(self) -> None:
        class SeamN2N:
            pass

        n2n_seam = SimpleNamespace(SeamN2N=SeamN2N)
        with self.assertRaises(RuntimeError):
            preflight_seam_n2n_from_state(n2n_seam)


if __name__ == "__main__":
    unittest.main()
