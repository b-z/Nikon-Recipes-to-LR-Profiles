"""Adobe RGBTable reference tetrahedral interpolation and exact face audit.

Source: Adobe dng_reference.cpp RefRGBtoRGBTable3D, Android DNG SDK mirror,
commit de700ad461e35af50b28b861943a0b0753b10929. Fractions are sorted B,G,R
on equal values, matching the reference comparison branches.
"""
import itertools
import numpy as np
import scipy.sparse as sp


def vertices(rgb,n):
    rgb = np.asarray(rgb,float)
    if rgb.ndim<1 or rgb.shape[-1]!=3 or not np.isfinite(rgb).all() or not 2<=n<=32:
        raise ValueError('Expected finite RGB values and grid 2..32')
    scaled = np.clip(rgb.reshape(-1,3),0,1)*(n-1)
    lo = np.minimum(np.floor(scaled).astype(int),n-2)
    fraction = scaled-lo
    order = np.argsort(fraction,axis=1,kind='stable')[:,::-1]
    f = np.take_along_axis(fraction,order,axis=1)
    v1 = lo.copy()
    v1[np.arange(len(lo)),order[:,0]] += 1
    v2 = lo+1
    v2[np.arange(len(lo)),order[:,2]] -= 1
    v3 = lo+1
    weights = np.stack((1-f[:,0],f[:,0]-f[:,1],f[:,1]-f[:,2],f[:,2]),axis=1)
    corners = np.stack((lo,v1,v2,v3),axis=1)
    return corners,weights


def lookup(lut,rgb):
    rgb = np.asarray(rgb,float)
    corners,weights = vertices(rgb,len(lut))
    values = lut[corners[...,0],corners[...,1],corners[...,2]]
    return np.sum(values*weights[...,None],axis=1).reshape(rgb.shape)


def design(rgb,n):
    corners,weights = vertices(rgb,n)
    cols = (corners[...,0]*n+corners[...,1])*n+corners[...,2]
    count = len(cols)
    return sp.csr_matrix((weights.ravel(),cols.ravel(),np.arange(count+1)*4),shape=(count,n**3))


def stats(a):
    a = np.asarray(a).ravel()
    if a.size==0:return dict(mean=0.,rms=0.,p95=0.,p99=0.,max=0.,count=0)
    if not np.isfinite(a).all():
        raise ValueError('Nonfinite tetrahedral audit')
    return dict(mean=float(a.mean()),rms=float(np.sqrt(np.mean(a*a))),p95=float(np.percentile(a,95)),
                p99=float(np.percentile(a,99)),max=float(a.max()),count=int(len(a)))


def audit(lut):
    lut=np.asarray(lut,float)
    n = len(lut)
    if lut.shape!=(n,n,n,3) or not 2<=n<=32 or not np.isfinite(lut).all():
        raise ValueError('Expected a finite (N,N,N,3) table, grid 2..32')
    permutations = list(itertools.permutations(range(3)))
    jacobians = {}
    def corner(offset):
        return lut[tuple(slice(v,v+n-1) for v in offset)]
    for p in permutations:
        v = np.zeros(3,dtype=int)
        values = [corner(v)]
        for axis in p:
            v = v.copy()
            v[axis] += 1
            values.append(corner(v))
        j = np.empty((n-1,n-1,n-1,3,3))
        for i,axis in enumerate(p):
            j[...,axis] = (values[i+1]-values[i])*(n-1)
        jacobians[p] = j
    internal = []
    seen = set()
    for p in permutations:
        for swap in (0,1):
            q = list(p)
            q[swap],q[swap+1] = q[swap+1],q[swap]
            q = tuple(q)
            pair = tuple(sorted((p,q)))
            if pair in seen:
                continue
            seen.add(pair)
            internal.append(np.linalg.norm(jacobians[p]-jacobians[q],axis=(-1,-2)).ravel())
    external = []
    for axis in range(3):
        others = [a for a in range(3) if a!=axis]
        for p in itertools.permutations(others):
            left = [slice(None)]*3
            right = [slice(None)]*3
            left[axis],right[axis] = slice(None,-1),slice(1,None)
            delta = (jacobians[(axis,*p)][tuple(left)]-
                     jacobians[(*p,axis)][tuple(right)])
            external.append(np.linalg.norm(delta,axis=(-1,-2)).ravel())
    internal,external = np.concatenate(internal),np.concatenate(external)
    gain = np.concatenate([np.linalg.svd(j.reshape(-1,3,3),compute_uv=False)[:,0]
                           for j in jacobians.values()])
    return dict(internal_face_jump=stats(internal),external_face_jump=stats(external),
                all_face_jump=stats(np.r_[internal,external]),local_gain=stats(gain),
                interpolation='tetrahedral',grid=n)
