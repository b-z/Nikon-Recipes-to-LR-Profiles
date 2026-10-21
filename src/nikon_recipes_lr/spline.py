"""Bounded smooth-spline fit used for the released profiles (Y8, since 0.2.0).

The RGB mapping is a C2 cubic tensor B-spline with ``control_points`` per axis,
fitted to paired chart samples with a curvature (bending-energy) penalty, then
sampled into the native 32³ RGBTable. The B-spline basis is nonnegative and sums
to one, so bounding the coefficients to 0..1 keeps every output in gamut without
clipping solved values.

Compared with :class:`nikon_recipes_lr.fit.NativeFitter`, which solves the 32³
table directly, the spline has far fewer degrees of freedom (16³ instead of
32³ per channel), which suppresses local waves between chart samples at some
cost in chart accuracy.
"""

import numpy as np
import scipy.sparse as sp
from scipy.interpolate import BSpline
from scipy.optimize import minimize

DEGREE = 3


def knots(control_points):
    """Clamped uniform knot vector for a cubic B-spline on 0..1."""
    if control_points < DEGREE + 1:
        raise ValueError(f"A cubic spline needs at least {DEGREE + 1} control points per axis")
    interior = np.linspace(0, 1, control_points - 2)[1:-1]
    return np.r_[np.zeros(DEGREE + 1), interior, np.ones(DEGREE + 1)]


def basis(rgb, control_points):
    """Sparse tensor B-spline basis: one row per RGB sample, 64 nonzeros per row."""
    rgb = np.asarray(rgb, float).reshape(-1, 3)
    t = knots(control_points)
    axes = [BSpline.design_matrix(np.clip(rgb[:, c], 0, 1), t, DEGREE).tocsr() for c in range(3)]
    count = len(rgb)
    k = control_points
    idx = [a.indices.reshape(count, 4) for a in axes]
    val = [a.data.reshape(count, 4) for a in axes]
    cols = ((idx[0][:, :, None, None] * k + idx[1][:, None, :, None]) * k + idx[2][:, None, None, :]).reshape(count, 64)
    values = (val[0][:, :, None, None] * val[1][:, None, :, None] * val[2][:, None, None, :]).reshape(count, 64)
    return sp.csr_matrix((values.ravel(), cols.ravel(), np.arange(count + 1) * 64), shape=(count, k**3))


def _derivative(count, degree, t):
    """Map B-spline coefficients to the coefficients of their derivative."""
    rows = np.arange(count - 1)
    scale = degree / (t[rows + degree + 1] - t[rows + 1])
    return sp.csr_matrix(
        (np.r_[-scale, scale], (np.r_[rows, rows], np.r_[rows, rows + 1])),
        shape=(count - 1, count),
    )


def bending(control_points):
    """Discrete second-derivative (thin-plate bending) operator on the coefficients."""
    k = control_points
    t = knots(k)
    d1 = _derivative(k, DEGREE, t)
    d2 = _derivative(k - 1, DEGREE - 1, t[1:-1]) @ d1
    ident = sp.eye(k, format="csr")

    def tensor(a, b, c):
        return sp.kron(sp.kron(a, b, format="csr"), c, format="csr")

    return sp.vstack(
        (
            tensor(d2, ident, ident),
            tensor(ident, d2, ident),
            tensor(ident, ident, d2),
            np.sqrt(2) * tensor(d1, d1, ident),
            np.sqrt(2) * tensor(d1, ident, d1),
            np.sqrt(2) * tensor(ident, d1, d1),
        ),
        format="csr",
    )


def table_grid(n):
    g = np.linspace(0, 1, n)
    return np.stack(np.meshgrid(g, g, g, indexing="ij"), -1)


class SplineFitter:
    """Fit Adobe RGB chart samples to a target look with a bounded smooth spline.

    ``x`` holds the Adobe Standard samples (N×3, encoded Adobe RGB 0..1). The
    expensive basis and penalty matrices are built once, so one fitter can be
    reused for many recipes measured on the same chart.
    """

    def __init__(self, x, control_points=16, grid=32):
        x = np.asarray(x, float)
        if x.ndim != 2 or x.shape[1] != 3 or len(x) == 0 or not np.isfinite(x).all():
            raise ValueError("Expected finite N×3 inputs")
        if np.any((x < 0) | (x > 1)):
            raise ValueError("Inputs must lie within 0..1")
        if not 2 <= grid <= 32:
            raise ValueError("RGBTable grid must be between 2 and 32")
        self.x = x
        self.control_points = k = control_points
        self.grid = grid
        self.a = basis(x, k)
        t = knots(k)
        greville = np.array([t[i + 1 : i + DEGREE + 1].mean() for i in range(k)])
        self.identity = np.stack(np.meshgrid(greville, greville, greville, indexing="ij"), -1).reshape(-1, 3)
        error = np.max(np.abs(self.a @ self.identity - x))
        if error > 1e-12:
            raise ValueError(f"Spline identity reproduction failed: {error}")
        penalty = bending(k)
        self.data_h = (self.a.T @ self.a) / len(x)
        self.smooth_h = (penalty.T @ penalty) / penalty.shape[0]
        self.table_a = basis(table_grid(grid), k)

    def fit(self, target, lam=0.001, mu=1e-5):
        """Return ``(table, coefficients, reports)``; ``table`` is quantized to 16 bits."""
        target = np.asarray(target, float)
        if target.shape != self.x.shape or not np.isfinite(target).all():
            raise ValueError("Target must be finite and match the input samples")
        if not (np.isfinite(lam) and lam >= 0 and np.isfinite(mu) and mu >= 0):
            raise ValueError("Regularization must be finite and nonnegative")
        k = self.control_points
        h = (self.data_h + lam**2 * self.smooth_h + mu / k**3 * sp.eye(k**3)).tocsr()
        rhs = self.a.T @ (target - self.x) / len(self.x)
        scale = np.sqrt(h.diagonal())
        inv = sp.diags(1 / scale)
        pre = (inv @ h @ inv).tocsr()
        coefficients, reports = [], []
        for c in range(3):
            b = rhs[:, c] / scale
            lo = -self.identity[:, c] * scale
            hi = (1 - self.identity[:, c]) * scale

            def objective(z, b=b):
                hz = pre @ z
                return 0.5 * np.dot(z, hz) - np.dot(b, z), hz - b

            result = minimize(
                objective,
                np.zeros(k**3),
                method="L-BFGS-B",
                jac=True,
                bounds=list(zip(lo, hi)),
                options=dict(maxiter=2500, ftol=1e-13, gtol=1e-8, maxcor=20),
            )
            if not result.success:
                raise RuntimeError(f"Bounded spline solve failed: {result.message}")
            coefficients.append(self.identity[:, c] + result.x / scale)
            reports.append(dict(iterations=int(result.nit), status=str(result.message)))
        coefficients = np.stack(coefficients, axis=-1)
        n = self.grid
        table = (self.table_a @ coefficients).reshape(n, n, n, 3)
        if table.min() < -1e-10 or table.max() > 1 + 1e-10:
            raise ValueError("Bounded spline left the output gamut")
        # Only floating-point roundoff is removed here; solved values are never clipped.
        table = np.rint(np.clip(table, 0, 1) * 65535) / 65535
        return table, coefficients, reports
