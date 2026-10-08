import json
import struct
import tempfile
import unittest
from unittest.mock import patch
import tifffile
from PIL import ImageCms
from nikon_recipes_lr.calibration import sample_tiff
from pathlib import Path
import numpy as np
from nikon_recipes_lr.color import lab,de2000
from nikon_recipes_lr.fit import NativeFitter,face_operator
from nikon_recipes_lr.np3 import parse_bytes
from nikon_recipes_lr.profile import identity,pack_table,unpack_table,build_profile,read_profile,render_sidecar
from nikon_recipes_lr.tetrahedral import lookup,audit,design
from nikon_recipes_lr.nx import inject


class CoreTests(unittest.TestCase):
    def test_tetrahedral_not_trilinear(self):
        lut=np.zeros((2,2,2,3));lut[1,1,1]=1
        np.testing.assert_allclose(lookup(lut,np.array([[.2,.5,.8],[.9,.3,.4]])),[[.2]*3,[.3]*3])

    def test_identity_and_design(self):
        points=np.r_[np.random.default_rng(1).random((100,3)),[[0,0,0],[1,1,1],[.5,.5,.5]]]
        np.testing.assert_allclose(lookup(identity(7),points),points,atol=2e-16)
        np.testing.assert_allclose(design(points,7)@identity(7).reshape(-1,3),points,atol=2e-16)

    def test_two_node_audit_and_invalid_inputs(self):
        result=audit(identity(2))
        self.assertEqual(result['external_face_jump']['count'],0)
        self.assertEqual(result['all_face_jump']['max'],0.)
        for points in (np.array([[np.nan,0,0]]),np.array([[1,2]])):
            with self.assertRaises(ValueError):lookup(identity(2),points)

    def test_exact_face_operator_energy(self):
        n=4;lut=np.random.default_rng(2).random((n,n,n,3))
        measured=audit(lut)['all_face_jump']
        energy=float(np.sum((face_operator(n)@lut.reshape(-1,3))**2))*(n-1)**2
        self.assertAlmostEqual(energy,measured['rms']**2*measured['count'],places=9)
        np.testing.assert_allclose(face_operator(n)@identity(n).reshape(-1,3),0,atol=1e-15)

    def test_ciede2000_reference_pairs_and_image_shape(self):
        a=np.array([[50,2.6772,-79.7751],[50,3.1571,-77.2803],[50,2.8361,-74.0200]])
        b=np.tile([50,0,-82.7485],(3,1))
        np.testing.assert_allclose(de2000(a,b),[2.0425,2.8615,3.4412],atol=.00005)
        image=np.random.default_rng(3).random((4,5,3))
        np.testing.assert_allclose(de2000(lab(image),lab(image)),np.zeros((4,5)))

    def test_rgbtable_roundtrip_fingerprint_and_xml(self):
        lut=np.random.default_rng(4).random((5,5,5,3));payload,tid=pack_table(lut)
        result,meta=unpack_table(payload)
        self.assertEqual(tid,meta['table_id']);np.testing.assert_allclose(result,lut,atol=.5/65535)
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'test.xmp';path.write_text(build_profile(lut,'Example & <look> 彩色 —','A "creator"'), encoding='utf-8')
            restored,m=read_profile(path);np.testing.assert_array_equal(result,restored)
            self.assertEqual(m['name'],'Example & <look> 彩色 —');self.assertEqual(m['camera'],'NIKON Z 8')
            self.assertIn('Amount="0.3"',render_sidecar(path,.3))
            text=path.read_text(encoding='utf-8').replace(tid,'F'*32);path.write_text(text, encoding='utf-8')
            with self.assertRaises(ValueError):read_profile(path)

    def test_reject_bad_table(self):
        for payload in ('!', '#####', '00000'):
            with self.assertRaises(ValueError):unpack_table(payload)
        lut=identity(3);lut[0,0,0,0]=np.nan
        with self.assertRaises(ValueError):pack_table(lut)

    def test_defensive_np3_and_nx_injection(self):
        recipe=b'NCP\0'+struct.pack('>II',0x100,4)+b'0310'+b'\0'*4
        records,trailer=parse_bytes(recipe);self.assertEqual(records,[(0x100,b'0310')])
        for bad in (b'',recipe[:-1],b'NCP\0'+struct.pack('>II',0x100,999)+b'\0'*4):
            with self.assertRaises(ValueError):parse_bytes(bad)
        template=''.join(f'&lt;{k}&gt;AAAA&lt;/{k}&gt;&lt;{k}Size&gt;4&lt;/{k}Size&gt;' for k in ('ExportData','CustomData'))
        self.assertIn('TkNQ',inject(template,recipe))
        with self.assertRaises(ValueError):inject('',recipe)

    def test_tiff_sampling_endianness_crop_and_profile_rejection(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'sample.TIF';meta=Path(t)/'chart.json'
            meta.write_text(json.dumps(dict(sensor_size=[10,10],active_size=[8,8],inset=[1,1],patches=[dict(label='p',center=[5,5])])), encoding='utf-8')
            icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
            for endian in ('<u2','>u2'):
                array=np.empty((8,8,3),dtype=endian);array[:]=[10000,20000,30000]
                tifffile.imwrite(path,array,photometric='rgb',extratags=[(34675,'B',len(icc),icc,False)],byteorder=endian[0])
                with self.assertRaises(ValueError):sample_tiff(path,meta,1)
                with patch('nikon_recipes_lr.calibration.ImageCms.getProfileDescription',return_value='Adobe RGB (1998)'):
                    sampled=sample_tiff(path,meta,1)
                np.testing.assert_allclose(sampled[0]['measured'],np.array([10000,20000,30000])/65535.)

    def test_bounded_fit_affine_and_repeatable(self):
        x=identity(4).reshape(-1,3);y=.8*x+.1
        fitter=NativeFitter(x,4);lut,_=fitter.fit(y,.1)
        np.testing.assert_allclose(lookup(lut,x),y,atol=.0003)
        lut2,_=fitter.fit(y,.1);np.testing.assert_array_equal(lut,lut2)
        extreme=y.copy();extreme[0]=[-2,3,3]
        bounded,_=fitter.fit(extreme,.1)
        self.assertGreaterEqual(bounded.min(),0);self.assertLessEqual(bounded.max(),1)


if __name__=='__main__':unittest.main()
