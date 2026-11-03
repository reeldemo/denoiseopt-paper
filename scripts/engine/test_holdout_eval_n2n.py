#!/usr/bin/env python3
"""Unit test: holdout_eval.load_n2n uses baselines.n2n_seam.from_state (not SeamN2N.from_state)."""
from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# holdout_eval imports torch at module level; provide a minimal stub when torch is absent.
if "torch" not in sys.modules:
    torch_stub = types.ModuleType("torch")

    class _Device:
        def __init__(self, name: str) -> None:
            self.type = name

    torch_stub.device = lambda name: _Device(name.split(":")[0])  # type: ignore[attr-defined]
    torch_stub.load = MagicMock()
    torch_stub.manual_seed = MagicMock()
    torch_stub.cuda = MagicMock()

    def _no_grad():
        def decorator(fn):
            return fn

        return decorator

    torch_stub.no_grad = _no_grad  # type: ignore[attr-defined]
    sys.modules["torch"] = torch_stub

ENGINE = Path(__file__).resolve().parent
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

import holdout_eval  # noqa: E402


class TestLoadN2nFromState(unittest.TestCase):
    @patch.object(holdout_eval, "bootstrap_reelsynth")
    @patch.object(holdout_eval.torch, "load")
    def test_calls_module_from_state(self, mock_load, mock_boot) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ckpt = root / "brand/artifacts/n2n_seam_baselines/n2n_corrupt_corrupt.pt"
            ckpt.parent.mkdir(parents=True, exist_ok=True)
            ckpt.write_bytes(b"stub")
            mock_boot.return_value = root
            mock_load.return_value = {"state_dict": {"w": 1}}

            fake_n2n = MagicMock()
            fake_model = MagicMock()
            fake_n2n.from_state.return_value = fake_model

            fake_og = MagicMock()
            baselines_mod = types.ModuleType("baselines")
            baselines_mod.n2n_seam = fake_n2n
            with patch.dict(
                sys.modules,
                {
                    "overnight_gpu_rl_arch": fake_og,
                    "baselines": baselines_mod,
                    "baselines.n2n_seam": fake_n2n,
                },
            ):
                device = holdout_eval.torch.device("cpu")
                fn, path_str = holdout_eval.load_n2n(root, device)

            fake_n2n.from_state.assert_called_once_with({"w": 1}, device)
            fake_model.eval.assert_called_once()
            self.assertEqual(path_str, str(ckpt))
            self.assertIsNotNone(fn)


if __name__ == "__main__":
    unittest.main()
