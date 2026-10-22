"""Command-line interface. Every output path is supplied explicitly and never overwritten."""

import argparse
import json
from pathlib import Path

import numpy as np

from . import __version__
from .calibration import read_samples, sample_tiff
from .color import de2000, lab
from .profile import BASES, DEFAULT_CAMERA, DEFAULT_GROUP, build_profile, read_profile
from .tetrahedral import audit, lookup

DEFAULT_LAMBDA = {"spline": 0.001, "native": 0.5}


def _add_profile_options(parser):
    parser.add_argument("--name", required=True, help="Profile name shown in Lightroom")
    parser.add_argument("--author", required=True, help="Original recipe author, for attribution")
    parser.add_argument("--group", default=DEFAULT_GROUP, help=f"Profile Browser group (default: {DEFAULT_GROUP!r})")
    parser.add_argument("--camera", default=DEFAULT_CAMERA, help="Camera model restriction; empty string for none")
    parser.add_argument(
        "--base",
        choices=BASES,
        default="Adobe Standard",
        help="Base profile the Adobe chart samples were rendered with (default: Adobe Standard)",
    )
    parser.add_argument("--output", required=True, help="Output .xmp path")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nikon-recipes-lr", description="Calibrate Nikon recipes into Lightroom / Camera Raw enhanced profiles."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("inspect", help="Read NP3 metadata (not a slider translator)")
    p.add_argument("recipe", help="Path to an .NP3 file")

    p = sub.add_parser("fit", help="Fit paired chart samples and write an enhanced XMP profile")
    p.add_argument(
        "--adobe-samples", required=True, help="Camera Raw chart samples on the --base profile (.json or .npy)"
    )
    p.add_argument("--nx-samples", required=True, help="NX Studio chart samples of the recipe (.json or .npy)")
    p.add_argument(
        "--method",
        choices=("spline", "native"),
        default="spline",
        help="spline: smooth B-spline fit used for released profiles (default); native: direct 32³ table fit",
    )
    p.add_argument("--lambda", type=float, dest="lam", help="Smoothness weight (default: 0.001 spline, 0.5 native)")
    p.add_argument("--control-points", type=int, default=16, help="Spline control points per axis (default: 16)")
    p.add_argument("--grid", type=int, default=32, help="Output RGBTable grid size, 2..32 (default: 32)")
    p.add_argument("--report", help="Optional JSON report path")
    _add_profile_options(p)

    p = sub.add_parser("export", help="Wrap a saved (N,N,N,3) .npy table as an XMP profile")
    p.add_argument("lut", help="Path to an .npy table with values in 0..1")
    _add_profile_options(p)

    p = sub.add_parser("audit", help="Structural banding-risk audit of a profile (not a visibility verdict)")
    p.add_argument("profile")
    p.add_argument("--output", help="Optional JSON output path")

    p = sub.add_parser("sample", help="Sample chart patches from a 16-bit Adobe RGB TIFF")
    p.add_argument("tiff")
    p.add_argument("--metadata", required=True, help="Chart metadata JSON written by make-target")
    p.add_argument("--output", required=True)

    p = sub.add_parser("prepare-nx", help="Prepare an NX Studio batch: one RAW copy and sidecar per recipe")
    p.add_argument("--source", required=True, help="Chart RAW")
    p.add_argument("--template", required=True, help="Saved NX sidecar (.nksc) to use as a template")
    p.add_argument("--recipes", nargs="+", required=True, help="NP3 files")
    p.add_argument("--output", required=True, help="New, empty batch directory")

    p = sub.add_parser("make-target", help="Experimental: write a synthetic Z 8 chart NEF from a donor RAW")
    p.add_argument("--donor", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--confirm-donor-calibration", action="store_true")

    p = sub.add_parser(
        "sidecars",
        help="Write XMP sidecars that apply the profile matching the recipe recorded in each NEF",
        description="Reads the Picture Control name the camera stored in each NEF (needs ExifTool) and writes "
        "<name>.xmp next to it with the matching profile. Import the folder into Lightroom afterwards.",
    )
    p.add_argument("photos", nargs="+", help="NEF files or folders")
    p.add_argument("--profiles", required=True, help="Folder with the profiles, e.g. the unzipped release")
    p.add_argument("--amount", type=float, default=1.0, help="Profile Amount, 0..2 (default: 1)")
    p.add_argument("--recursive", action="store_true", help="Include subfolders")
    p.add_argument("--overwrite", action="store_true", help="Replace existing sidecars (their edits are lost)")
    p.add_argument("--dry-run", action="store_true", help="Report what would be written without writing")

    p = sub.add_parser("render", help="macOS only: render a RAW through Photoshop's Camera Raw")
    p.add_argument("raw")
    p.add_argument("--profile", help="XMP profile to apply")
    p.add_argument("--amount", type=float, default=1.0, help="Profile Amount, 0..2 (default: 1)")
    p.add_argument("--output", required=True, help="Output 16-bit TIFF")
    p.add_argument("--app", default="Adobe Photoshop 2026", help="Photoshop application name")
    p.add_argument("--base", choices=BASES, default="Adobe Standard", help="Base profile (default: Adobe Standard)")
    return parser


def _fit(args):
    from .fit import NativeFitter
    from .spline import SplineFitter

    lam = DEFAULT_LAMBDA[args.method] if args.lam is None else args.lam
    if not 2 <= args.grid <= 32 or not np.isfinite(lam) or lam < 0:
        raise ValueError("Invalid grid or regularization")
    x, y = read_samples(args.adobe_samples), read_samples(args.nx_samples)
    if x.shape != y.shape:
        raise ValueError("Paired sample shapes differ")
    valid = ~(((x > 0.999) | (x < 0.0005) | (y > 0.999) | (y < 0.0005)).any(1))
    if valid.sum() < 4:
        raise ValueError("Too few unclipped calibration pairs")
    if args.method == "spline":
        lut, _, solver = SplineFitter(x[valid], args.control_points, args.grid).fit(y[valid], lam)
    else:
        lut, solver = NativeFitter(x[valid], args.grid).fit(y[valid], lam)
    Path(args.output).write_text(
        build_profile(lut, args.name, args.author, group=args.group, camera=args.camera, base=args.base),
        encoding="utf-8",
    )
    error = de2000(lab(lookup(lut, x[valid])), lab(y[valid]))
    result = dict(
        profile=args.output,
        method=args.method,
        regularization=lam,
        samples=int(valid.sum()),
        mean_de=float(error.mean()),
        p95_de=float(np.percentile(error, 95)),
        evaluation="training chart, not independent validation",
        solver=solver,
        structure=audit(lut),
    )
    if args.report:
        Path(args.report).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def run(args):
    if args.command == "inspect":
        from .np3 import inspect

        return inspect(args.recipe)
    if args.command == "fit":
        return _fit(args)
    if args.command == "export":
        lut = np.load(args.lut, allow_pickle=False)
        text = build_profile(lut, args.name, args.author, group=args.group, camera=args.camera, base=args.base)
        Path(args.output).write_text(text, encoding="utf-8")
        return dict(profile=args.output)
    if args.command == "audit":
        lut, metadata = read_profile(args.profile)
        result = dict(name=metadata["name"], structure=audit(lut))
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result
    if args.command == "sample":
        rows = sample_tiff(args.tiff, args.metadata)
        Path(args.output).write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return dict(samples=len(rows), output=args.output)
    if args.command == "prepare-nx":
        from .nx import prepare

        return dict(recipes=prepare(args.source, args.template, args.recipes, args.output))
    if args.command == "make-target":
        from .target import generate

        return dict(metadata=str(generate(args.donor, args.output, args.confirm_donor_calibration)))
    if args.command == "sidecars":
        from .sidecar import write_sidecars

        return write_sidecars(args.photos, args.profiles, args.amount, args.overwrite, args.dry_run, args.recursive)
    if args.command == "render":
        from .photoshop import render

        return dict(output=str(render(args.raw, args.output, args.profile, args.amount, args.app, args.base)))
    raise AssertionError(args.command)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    for key in ("output", "report"):
        value = getattr(args, key, None)
        if value and Path(value).exists():
            parser.error(f"Refusing to overwrite {value}")
    try:
        result = run(args)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, f"error: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
