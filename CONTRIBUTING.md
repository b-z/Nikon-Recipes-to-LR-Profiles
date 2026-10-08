# Contributing

Issues and pull requests are welcome. Use English for code, comments and primary documentation; Chinese or Japanese reports are welcome too.

1. Open a focused issue with a reproducible problem or proposed improvement. For banding, include recipe/version, camera, Amount, Adobe version and a small permitted crop or synthetic path. Full-resolution personal RAWs are optional.
2. Make one focused change, add meaningful regression tests, and run `python -m unittest discover -s tests -v` after installing with `python -m pip install -e .`.
3. Submit a pull request explaining changed behavior, measurements, limitations and data provenance. Contributions to this project's code/docs are under MIT; do not submit third-party code or photos without appropriate permission.

Useful work: additional Nikon-body calibration, smoothness/fidelity tradeoffs, trustworthy spatial/perceptual evaluation, portability, tests and translations. Do not claim a banding fix solely from chart ΔE or a single photo. Preserve all-face audits and record held-out versus training data.

Original NP3 collections, Adobe SDK source, Adobe base DCPs, vendor applications, private logs, Lightroom catalogs and Fuji simulation conversion are outside this repository. Use explicit input paths; do not introduce personal NAS/user directory defaults. Larger benchmark inputs belong in separate documented assets, not normal git history.

See [Chinese](docs/zh/CONTRIBUTING.md) and [Japanese](docs/ja/CONTRIBUTING.md) contribution notes. No separate CLA is required.
