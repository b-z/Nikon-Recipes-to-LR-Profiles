import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

from nikon_recipes_lr import sidecar
from nikon_recipes_lr.profile import CRS, build_profile, identity, import_sidecar, read_profile


def fake_picture_controls(names):
    return lambda raws: [(raw, names.get(raw.name)) for raw in raws]


class SidecarTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.profiles = root / "profiles"
        self.photos = root / "photos"
        self.profiles.mkdir()
        self.photos.mkdir()
        lut = identity(5)
        (self.profiles / "NikonRecipes_KP160.xmp").write_text(build_profile(lut, "KP160 by A [NRLR 0.2]", "A"), "utf-8")
        (self.profiles / "NikonRecipes_A-X+rossandhisjpegs.xmp").write_text(build_profile(lut, "A-X", "B"), "utf-8")
        (self.profiles / "mine.xmp").write_text(build_profile(lut, "MyLook", "Me"), "utf-8")
        for name in ("a.NEF", "b.NEF", "c.nef", "d.NEF", "notes.txt"):
            (self.photos / name).write_bytes(b"")

    def tearDown(self):
        self.tmp.cleanup()

    def test_release_names_are_unique_and_cover_known_recipes(self):
        names = sidecar.release_picture_controls()
        self.assertEqual(len(names), 236)
        self.assertEqual(len(set(names.values())), 236)
        self.assertEqual(names["KP160"], "KP160")
        self.assertTrue(all(len(n) <= 19 for n in names.values()))

    def test_index_uses_release_file_names_and_custom_profile_names(self):
        index = sidecar.profile_index(self.profiles)
        self.assertEqual(index["KP160"].name, "NikonRecipes_KP160.xmp")
        self.assertEqual(index["A-X rossandhisjpegs"].name, "NikonRecipes_A-X+rossandhisjpegs.xmp")
        self.assertEqual(index["MyLook"].name, "mine.xmp")
        (self.profiles / "copy.xmp").write_text(build_profile(identity(5), "MyLook", "Me", group="Other"), "utf-8")
        with self.assertRaises(ValueError):
            sidecar.profile_index(self.profiles)

    def test_import_sidecar_sets_only_profile_and_look(self):
        text = import_sidecar(self.profiles / "NikonRecipes_KP160.xmp", 0.5)
        desc = ET.fromstring(text).find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
        settings = {k.split("}")[1] for k in desc.attrib}
        self.assertEqual(
            settings,
            {"Version", "ProcessVersion", "HasSettings", "CameraProfile", "LensProfileEnable", "LensProfileSetup"},
        )
        self.assertEqual(desc.get(f"{{{CRS}}}CameraProfile"), "Adobe Standard")
        meta = read_profile(self.profiles / "NikonRecipes_KP160.xmp")[1]
        self.assertIn(f'crs:UUID="{meta["uuid"]}"', text)
        self.assertIn('crs:Amount="0.5"', text)
        self.assertIn(f"crs:Table_{meta['table_id']}=", text)
        with self.assertRaises(ValueError):
            import_sidecar(self.profiles / "NikonRecipes_KP160.xmp", 2.5)

    def test_write_sidecars(self):
        names = {"a.NEF": "KP160", "b.NEF": "MyLook", "c.nef": "Standard", "d.NEF": None}
        (self.photos / "b.xmp").write_text("user edits", "utf-8")
        with mock.patch.object(sidecar, "picture_controls", fake_picture_controls(names)):
            dry = sidecar.write_sidecars([self.photos], self.profiles, dry_run=True)
            self.assertFalse((self.photos / "a.xmp").exists())
            result = sidecar.write_sidecars([self.photos], self.profiles)
            self.assertEqual([Path(w["raw"]).name for w in dry["written"]], ["a.NEF"])
            self.assertEqual([Path(w["raw"]).name for w in result["written"]], ["a.NEF"])
            self.assertEqual(result["no_profile"], {"Standard": 1})
            self.assertEqual([Path(p).name for p in result["no_picture_control"]], ["d.NEF"])
            self.assertEqual((self.photos / "b.xmp").read_text("utf-8"), "user edits")
            self.assertIn("NikonRecipes_KP160", result["written"][0]["profile"])
            replaced = sidecar.write_sidecars([self.photos / "b.NEF"], self.profiles, overwrite=True)
            self.assertEqual(len(replaced["written"]), 1)
            self.assertIn('crs:Name="MyLook"', (self.photos / "b.xmp").read_text("utf-8"))
        with self.assertRaises(ValueError):
            sidecar.raw_files([self.photos / "notes.txt"])


class BaseProfileTests(unittest.TestCase):
    def test_flexible_color_base_is_kept_in_profile_and_sidecar(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "flex.xmp"
            path.write_text(build_profile(identity(5), "Flex", "A", base="Camera Flexible Color"), "utf-8")
            meta = read_profile(path)[1]
            self.assertEqual(meta["base"], "Camera Flexible Color")
            self.assertIn('crs:CameraProfile="Camera Flexible Color"', import_sidecar(path))
            with self.assertRaises(ValueError):
                build_profile(identity(5), "Bad", "A", base="Camera Standard")


if __name__ == "__main__":
    unittest.main()
