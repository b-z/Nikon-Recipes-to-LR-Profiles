"""Read paired chart samples and sample TIFF patches without 8-bit conversion."""
import json
import io
from PIL import ImageCms
from pathlib import Path
import numpy as np
import tifffile


def read_samples(path):
    path=Path(path)
    if path.suffix.lower()=='.npy':value=np.load(path,allow_pickle=False)
    else:
        rows=json.loads(path.read_text(encoding='utf-8'))
        value=np.array([r['measured'] for r in rows]) if rows and isinstance(rows[0],dict) else np.array(rows)
    if value.ndim!=2 or value.shape[1]!=3 or not np.isfinite(value).all() or np.any((value<0)|(value>1)):
        raise ValueError('Samples must be a finite Nx3 array in 0..1')
    return value.astype(float)


def sample_tiff(image_path,metadata_path,radius=4):
    if not 0<=radius<=16:raise ValueError('Patch radius must be 0..16')
    metadata=json.loads(Path(metadata_path).read_text(encoding='utf-8'))
    with tifffile.TiffFile(image_path) as tif:
        page=tif.pages[0]
        icc=page.tags.get(34675)
        if icc is None:raise ValueError('Missing ICC profile; export 16-bit Adobe RGB')
        profile_name=ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(io.BytesIO(icc.value))).strip()
        if 'adobe' not in profile_name.lower() or 'rgb' not in profile_name.lower():
            raise ValueError(f'Expected Adobe RGB ICC profile, got {profile_name!r}')
        # Sample pixels directly; the caller must supply the stated Adobe RGB export.
        try:image=tifffile.memmap(image_path)
        except ValueError:image=page.asarray()
    if image.dtype.kind!='u' or image.dtype.itemsize!=2 or image.ndim!=3 or image.shape[2]!=3:
        raise ValueError('Expected 16-bit RGB TIFF')
    sensor=metadata['sensor_size'];inset=metadata['inset']
    if list(image.shape[:2][::-1])==sensor:offset=(0,0)
    elif list(image.shape[:2][::-1])==metadata['active_size']:offset=inset
    else:raise ValueError('TIFF dimensions do not match chart metadata')
    output=[]
    for patch in metadata['patches']:
        x,y=np.rint(np.array(patch['center'])-offset).astype(int)
        if x-radius<0 or y-radius<0 or x+radius>=image.shape[1] or y+radius>=image.shape[0]:
            raise ValueError('Patch lies outside image')
        output.append(dict(label=patch['label'],measured=(np.mean(image[y-radius:y+radius+1,x-radius:x+radius+1],axis=(0,1))/65535).tolist()))
    del image
    return output
