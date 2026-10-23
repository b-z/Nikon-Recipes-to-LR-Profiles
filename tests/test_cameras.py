import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from nikon_recipes_lr.cameras import (
    ADOBE,
    FLEX_CAMERAS,
    REFERENCE,
    SERIES,
    adobe_profile,
    camera_profile,
    table_of,
    table_sources,
)
from nikon_recipes_lr.profile import build_profile, identity, read_profile


def reference(lut):
    text = build_profile(
        lut,
        "KP160 by A [NRLR 1.0]",
        "A",
        group="Nikon Recipes LR 1.0/X",
        base="Camera Flexible Color",
        camera="NIKON Z 8",
        short_name="KP160 [NRLR 1.0]",
    )
    return text.replace("Calibrated approximation", "(RGB table on Camera Flexible Color, Nikon Z 8) Calibrated")


class CameraPackTests(unittest.TestCase):
    def test_each_camera_gets_its_restriction_series_and_own_uuid(self):
        lut = identity(5)
        text = reference(lut)
        uuids = set()
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "p.xmp"
            for camera in FLEX_CAMERAS:
                path.write_text(camera_profile(text, "KP160", camera), "utf-8")
                table, meta = read_profile(path)
                self.assertEqual(meta["camera"], camera.restriction)
                self.assertEqual(meta["base"], "Camera Flexible Color")
                self.assertEqual(meta["group"], f"Nikon Recipes LR {SERIES}/X")
                self.assertTrue(meta["name"].endswith(f"[NRLR {SERIES}]"))
                self.assertLess(abs(table - lut).max(), 1e-4)
                uuids.add(meta["uuid"])
        self.assertEqual(len(uuids), len(FLEX_CAMERAS))
        self.assertIn("Nikon Z f)", camera_profile(text, "KP160", FLEX_CAMERAS[2]))

    def test_table_source_replaces_only_the_table(self):
        lut = identity(5)
        other = np.clip(lut * 0.9 + 0.05, 0, 1)
        source = build_profile(other, "whatever", "B", base="Camera Flexible Color", camera="Nikon Z f")
        zf = next(c for c in FLEX_CAMERAS if c.slug == "zf")
        text = camera_profile(reference(lut), "KP160", zf, source)
        self.assertEqual(table_of(text), table_of(source))
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "p.xmp"
            path.write_text(text, "utf-8")
            table, meta = read_profile(path)
        self.assertLess(abs(table - other).max(), 1e-4)
        self.assertEqual(meta["camera"], "Nikon Z f")
        self.assertTrue(meta["name"].startswith("KP160 by A"))

    def test_table_sources_are_checked_against_the_manifest(self):
        source = build_profile(identity(5), "x", "B", base="Camera Flexible Color", camera="Nikon Z f")
        tid = table_of(source)[0]
        with tempfile.TemporaryDirectory() as t:
            root, manifests = Path(t) / "tables", Path(t) / "manifests"
            manifests.mkdir()
            for camera in FLEX_CAMERAS:
                if camera.fitted and camera != REFERENCE:
                    (root / camera.slug).mkdir(parents=True)
                    (root / camera.slug / "p.xmp").write_text(source, "utf-8")
                    row = dict(recipe="KP160", file="p.xmp", source_table_id=tid)
                    (manifests / f"{camera.slug}.json").write_text(json.dumps([row]), "utf-8")
            sources = table_sources(root, manifests)
            self.assertIn("zf", sources)
            self.assertNotIn(REFERENCE.slug, sources)
            (manifests / "zf.json").write_text(
                json.dumps([dict(recipe="KP160", file="p.xmp", source_table_id="0" * 32)])
            )
            with self.assertRaises(ValueError):
                table_sources(root, manifests)

    def test_adobe_pack_is_unrestricted_with_new_group(self):
        text = build_profile(identity(5), "KP160 by A [NRLR 0.2]", "A", group="Nikon Recipes LR 0.2/X", camera="")
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "p.xmp"
            path.write_text(adobe_profile(text, "KP160"), "utf-8")
            meta = read_profile(path)[1]
        self.assertEqual(meta["group"], f"Nikon Recipes LR {SERIES} Adobe/X")
        self.assertTrue(meta["name"].endswith(f"[NRLR {SERIES} Adobe]"))
        self.assertEqual(ADOBE.slug, "adobe")


if __name__ == "__main__":
    unittest.main()
