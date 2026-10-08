"""Bounded fit with regularization of every tetrahedral face. Input/output: encoded Adobe RGB."""
import numpy as np
import scipy.sparse as sp
from scipy.optimize import minimize
from scipy.sparse.linalg import cg
from .tetrahedral import design

def face_operator(n):
    grid = np.arange(n**3).reshape(n,n,n)
    blocks = []
    def block(offsets,shape,factor):
        vertices = [grid[tuple(slice(o,o+s) for o,s in zip(offset,shape))].ravel()
                    for offset in offsets]
        count = len(vertices[0])
        rows = np.arange(count)
        return sp.csr_matrix((np.r_[np.full(count,factor),np.full(count,-factor),
                                     np.full(count,-factor),np.full(count,factor)],
                              (np.tile(rows,4),np.concatenate(vertices))),shape=(count,n**3))
    for a,b in ((0,1),(0,2),(1,2)):
        other = next(i for i in range(3) if i not in (a,b))
        for side in (0,1):
            offsets = np.zeros((4,3),dtype=int)
            offsets[:,other] = side
            offsets[1,a] = 1
            offsets[2,b] = 1
            offsets[3,a] = offsets[3,b] = 1
            blocks.append(block(offsets,(n-1,)*3,np.sqrt(2)))
    for axis in range(3):
        shape = [n-1]*3
        shape[axis] = n-2
        prev = np.zeros(3,dtype=int)
        face_low = prev.copy();face_low[axis] = 1
        face_high = np.ones(3,dtype=int)
        following = face_high.copy();following[axis] = 2
        blocks.append(block((prev,face_low,face_high,following),shape,np.sqrt(2)))
    return sp.vstack(blocks,format='csr')


class NativeFitter:
    def __init__(self,x,n=32):
        x=np.asarray(x,float)
        if not 2<=n<=32 or x.ndim!=2 or x.shape[1]!=3 or len(x)==0 or not np.isfinite(x).all() or np.any((x<0)|(x>1)):
            raise ValueError('Expected finite Nx3 inputs in 0..1 and grid 2..32')
        self.n = n
        self.a = design(x,n)
        self.x = x
        g = np.linspace(0,1,n)
        self.identity = np.stack(np.meshgrid(g,g,g,indexing='ij'),axis=-1).reshape(-1,3)
        if np.max(abs(self.a@self.identity-x))>1e-12:
            raise ValueError('Native interpolation identity mismatch')
        self.r = face_operator(n)
        if np.max(abs(self.r@self.identity))>1e-12:
            raise ValueError('Face operator does not annihilate identity')
        self.data_h = self.a.T@self.a
        self.smooth_h = self.r.T@self.r

    def fit(self,target,lam):
        target=np.asarray(target,float)
        if target.shape!=self.x.shape or not np.isfinite(target).all() or not np.isfinite(lam) or lam<0:
            raise ValueError('Target shape/values or regularization are invalid')
        h = (self.data_h+lam**2*self.smooth_h+1e-3*sp.eye(self.n**3)).tocsr()
        scale = np.sqrt(h.diagonal())
        inv = sp.diags(1/scale)
        pre = (inv@h@inv).tocsr()
        rhs = self.a.T@(target-self.x)
        coefficients,reports = [],[]
        for c in range(3):
            b = rhs[:,c]/scale
            initial,info = cg(pre,b,rtol=1e-8,maxiter=5000)
            if info:
                raise RuntimeError(f'Native initialization CG failed: {info}')
            lo,hi = -self.identity[:,c]*scale,(1-self.identity[:,c])*scale
            initial = np.minimum(np.maximum(initial,lo),hi)
            def objective(z):
                hz = pre@z
                return .5*np.dot(z,hz)-np.dot(b,z),hz-b
            result = minimize(objective,initial,method='L-BFGS-B',jac=True,bounds=list(zip(lo,hi)),
                              options=dict(maxiter=2500,ftol=1e-12,gtol=1e-7,maxcor=20))
            if not result.success:
                raise RuntimeError(f'Native bounded solve failed: {result.message}')
            coefficients.append(self.identity[:,c]+result.x/scale)
            reports.append(dict(iterations=int(result.nit),status=str(result.message)))
        lut = np.stack(coefficients,axis=-1).reshape(self.n,self.n,self.n,3)
        if lut.min() < -1e-10 or lut.max()>1+1e-10:
            raise ValueError('Bounded native output left gamut')
        return np.rint(np.minimum(np.maximum(lut,0),1)*65535)/65535,reports
