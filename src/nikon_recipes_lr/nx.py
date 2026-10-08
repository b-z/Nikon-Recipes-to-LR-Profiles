"""Prepare NX batch copies from the user's own chart, recipes and saved NX sidecar."""
import base64
import hashlib
import html
import re
import shutil
from pathlib import Path
from .np3 import parse_bytes


def inject(template,recipe):
    parse_bytes(recipe)
    b64=base64.b64encode(recipe).decode()
    lines=[b64[i:i+60] for i in range(0,len(b64),60)]
    block='&#xA;'.join(lines);size=len(b64)+len(lines)-1
    for tag in ('ExportData','CustomData'):
        template,count=re.subn(rf'(&lt;{tag}&gt;).*?(&lt;/{tag}&gt;)',lambda m:m[1]+block+m[2],template,flags=re.S)
        if count!=1:raise ValueError(f'Expected exactly one escaped {tag} in NX template')
        template,count=re.subn(rf'(&lt;{tag}Size&gt;)\d+(&lt;/{tag}Size&gt;)',lambda m:m[1]+str(size)+m[2],template)
        if count!=1:raise ValueError(f'Expected exactly one {tag}Size in NX template')
    decoded=html.unescape(template)
    for tag in ('ExportData','CustomData'):
        block=re.search(rf'<{tag}>(.*?)</{tag}>',decoded,re.S)
        if not block or base64.b64decode(''.join(block[1].split()),validate=True)!=recipe:
            raise ValueError('NX recipe injection round-trip failed')
    return template


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        for block in iter(lambda:stream.read(4*1024**2),b''):h.update(block)
    return h.hexdigest()


def prepare(source,template_path,recipe_paths,output):
    source=Path(source);output=Path(output);template=Path(template_path).read_text()
    if output.exists():raise FileExistsError('Use a new empty batch directory')
    prepared=[];names=set()
    for p in recipe_paths:
        path=Path(p);name=re.sub(r'[^\w.-]+','_',path.stem)
        if name.casefold() in names:raise ValueError('Duplicate recipe filenames')
        names.add(name.casefold());prepared.append((name,inject(template,path.read_bytes())))
    source_hash=sha256(source)
    output.mkdir(parents=True);(output/'NKSC_PARAM').mkdir()
    for name,sidecar in prepared:
        dest=output/f'{name}.NEF';shutil.copyfile(source,dest)
        if sha256(dest)!=source_hash:raise IOError('RAW copy checksum differs')
        (output/'NKSC_PARAM'/f'{dest.name}.nksc').write_text(sidecar)
    return [name for name,_ in prepared]
