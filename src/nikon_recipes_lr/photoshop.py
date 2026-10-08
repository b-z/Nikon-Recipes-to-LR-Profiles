"""Optional macOS Photoshop/Camera Raw adapter. Never installs profiles or restarts Photoshop."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from .profile import render_sidecar


def render(raw,output,profile=None,amount=1.,app='Adobe Photoshop 2026'):
    raw=Path(raw).resolve();output=Path(output).resolve()
    if not raw.is_file():raise FileNotFoundError(raw)
    if output.exists():raise FileExistsError(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='nikon-lr-render-') as directory:
        work=Path(directory);source=work/'input.NEF';target=work/'output.TIF'
        shutil.copyfile(raw,source)
        source.with_suffix('.xmp').write_text(render_sidecar(profile,amount), encoding='utf-8')
        code='''#target photoshop
var previousDialogs=app.displayDialogs;
app.displayDialogs=DialogModes.NO;
var doc=null;var answer="";
try {
 var o=new CameraRAWOpenOptions();o.settings=CameraRAWSettingsType.SELECTEDIMAGE;
 o.bitsPerChannel=BitsPerChannelType.SIXTEEN;o.colorSpace=ColorSpaceType.ADOBERGB;
 doc=app.open(new File(SOURCE),o);
 var t=new TiffSaveOptions();t.embedColorProfile=true;t.layers=false;
 doc.saveAs(new File(TARGET),t,true,Extension.NONE);
 doc.close(SaveOptions.DONOTSAVECHANGES);doc=null;answer="OK";
} catch(e) {
 if(doc){try{doc.close(SaveOptions.DONOTSAVECHANGES);}catch(e2){}}
 answer="ERR "+e.message;
} finally {app.displayDialogs=previousDialogs;}
answer;'''.replace('SOURCE',json.dumps(str(source))).replace('TARGET',json.dumps(str(target)))
        script=work/'render.jsx';script.write_text(code, encoding='utf-8')
        command=f'tell application {json.dumps(app)} to do javascript (read POSIX file {json.dumps(str(script))})'
        result=subprocess.run(['osascript','-e',command],capture_output=True,text=True,timeout=180)
        if result.returncode or result.stdout.strip()!='OK' or not target.exists():
            raise RuntimeError('Camera Raw render failed: '+(result.stdout+result.stderr).strip())
        # Read back the applied profile identity, not just the requested sidecar.
        settings=json.loads(subprocess.check_output(['exiftool','-j','-XMP-crs:all',str(target)]))[0]
        if settings.get('CameraProfile')!='Adobe Standard':
            raise RuntimeError('Camera Raw silently changed the requested base profile')
        if profile:
            from .profile import read_profile
            expected=read_profile(profile)[1]
            actual=settings.get('LookName')
            if settings.get('LookParametersRGBTable')!=expected['table_id'] or settings.get('LookUUID')!=expected['uuid'] or abs(float(settings.get('LookAmount',-1))-amount)>1e-5:
                raise RuntimeError('Camera Raw look fingerprint, UUID or Amount mismatch')
            if actual!=expected['name']:
                raise RuntimeError(f'Camera Raw look mismatch: requested {expected["name"]!r}, got {actual!r}')
        shutil.copyfile(target,output)
    return output
