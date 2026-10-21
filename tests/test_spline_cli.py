import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from nikon_recipes_lr.cli import main
from nikon_recipes_lr.profile import DEFAULT_GROUP, identity, read_profile
from nikon_recipes_lr.spline import SplineFitter, basis, bending, knots
from nikon_recipes_lr.tetrahedral import lookup

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class SplineTests(unittest.TestCase):
    def test_basis_is_partition_of_unity(self):
        rgb = np.random.default_rng(5).random((50, 3))
        a = basis(rgb, 6)
        np.testing.assert_allclose(np.asarray(a.sum(axis=1)).ravel(), 1)
        self.assertTrue((a.data >= 0).all())

    def test_bending_annihilates_affine_coefficients(self):
        k = 6
        t = knots(k)
        greville = np.array([t[i + 1 : i + 4].mean() for i in range(k)])
        grid = np.stack(np.meshgrid(greville, greville, greville, indexing="ij"), -1).reshape(-1, 3)
        affine = grid @ np.array([[0.7, 0.1, 0], [0.1, 0.8, 0.05], [0, 0.1, 0.9]]) + 0.02
        np.testing.assert_allclose(bending(k) @ affine, 0, atol=1e-10)

    def test_recovers_affine_look_and_stays_in_gamut(self):
        x = identity(7).reshape(-1, 3)
        fitter = SplineFitter(x, control_points=6, grid=9)
        table, coefficients, reports = fitter.fit(0.8 * x + 0.1, lam=0.001)
        self.assertEqual(table.shape, (9, 9, 9, 3))
        self.assertEqual(coefficients.shape, (6**3, 3))
        self.assertEqual(len(reports), 3)
        np.testing.assert_allclose(lookup(table, x), 0.8 * x + 0.1, atol=0.002)
        extreme = 0.8 * x + 0.1
        extreme[0] = [-2, 3, 3]
        bounded, _, _ = fitter.fit(extreme, lam=0.001)
        self.assertGreaterEqual(bounded.min(), 0)
        self.assertLessEqual(bounded.max(), 1)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            SplineFitter(np.array([[0.1, 0.2, 1.5]]))
        with self.assertRaises(ValueError):
            SplineFitter(identity(3).reshape(-1, 3), control_points=3)


class CliTests(unittest.TestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(list(argv))
        return json.loads(out.getvalue())

    def test_fit_and_audit_example(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "toy.xmp"
            report = Path(directory) / "toy.json"
            result = self.run_cli(
                "fit",
                "--adobe-samples", str(EXAMPLES / "adobe.json"),
                "--nx-samples", str(EXAMPLES / "toy-style.json"),
                "--name", "Toy affine look",
                "--author", "Project synthetic example",
                "--grid", "8",
                "--control-points", "6",
                "--output", str(profile),
                "--report", str(report),
            )  # fmt: skip
            self.assertEqual(result["method"], "spline")
            self.assertLess(result["mean_de"], 0.5)
            _, metadata = read_profile(profile)
            self.assertEqual(metadata["group"], DEFAULT_GROUP)
            self.assertEqual(metadata["camera"], "NIKON Z 8")
            audited = self.run_cli("audit", str(profile))
            self.assertEqual(audited["name"], "Toy affine look")
            with self.assertRaises(SystemExit):
                self.run_cli("audit", str(profile), "--output", str(report))

    def test_group_changes_uuid(self):
        with tempfile.TemporaryDirectory() as directory:
            table = Path(directory) / "t.npy"
            np.save(table, identity(4))
            uuids = []
            for group in ("A", "B"):
                output = Path(directory) / f"{group}.xmp"
                self.run_cli(
                    "export", str(table), "--name", "Look", "--author", "Me",
                    "--group", group, "--camera", "", "--output", str(output),
                )  # fmt: skip
                _, metadata = read_profile(output)
                self.assertEqual(metadata["camera"], "")
                uuids.append(metadata["uuid"])
            self.assertNotEqual(*uuids)


if __name__ == "__main__":
    unittest.main()
