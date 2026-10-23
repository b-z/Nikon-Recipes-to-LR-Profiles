import tempfile
import unittest
from pathlib import Path

from nikon_recipes_lr.cameras import ADOBE, FLEX_CAMERAS, REFERENCE, adobe_profile, camera_profile
from nikon_recipes_lr.profile import build_profile, identity, read_profile


class CameraPackTests(unittest.TestCase):
    def test_each_camera_gets_its_restriction_and_own_uuid(self):
        lut = identity(5)
        text = build_profile(lut, "KP160 by A [NRLR 1.0]", "A", base="Camera Flexible Color", camera="NIKON Z 8")
        text = text.replace("Calibrated approximation", "(RGB table on Camera Flexible Color, Nikon Z 8) Calibrated")
        uuids = set()
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "p.xmp"
            for camera in FLEX_CAMERAS:
                path.write_text(camera_profile(text, "KP160", camera), "utf-8")
                table, meta = read_profile(path)
                self.assertEqual(meta["camera"], camera.restriction)
                self.assertEqual(meta["base"], "Camera Flexible Color")
                self.assertTrue((table == lut).all() or abs(table - lut).max() < 1e-4)
                uuids.add(meta["uuid"])
        self.assertEqual(len(uuids), len(FLEX_CAMERAS))
        self.assertEqual(camera_profile(text, "KP160", REFERENCE), text)

    def test_adobe_pack_is_unrestricted_with_new_group(self):
        text = build_profile(identity(5), "KP160 by A [NRLR 0.2]", "A", group="Nikon Recipes LR 0.2/X", camera="")
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "p.xmp"
            path.write_text(adobe_profile(text, "KP160"), "utf-8")
            meta = read_profile(path)[1]
        self.assertEqual(meta["group"], "Nikon Recipes LR 1.0 Adobe/X")
        self.assertTrue(meta["name"].endswith("[NRLR 1.0 Adobe]"))
        self.assertEqual(ADOBE.slug, "adobe")


if __name__ == "__main__":
    unittest.main()
