"""Portable CLI. Every generated output path is supplied explicitly."""
import argparse
import json
from pathlib import Path
import numpy as np
from .calibration import read_samples,sample_tiff
from .fit import NativeFitter
from .profile import build_profile,read_profile
from .tetrahedral import lookup,audit
from .color import lab,de2000


def main():
    parser=argparse.ArgumentParser(description='Calibrate Nikon recipes into Lightroom enhanced profiles')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('inspect',help='Read NP3 metadata; not an exact slider translator');p.add_argument('recipe')
    p=sub.add_parser('fit',help='Fit paired Adobe RGB samples and emit an enhanced XMP profile')
    p.add_argument('--adobe-samples',required=True);p.add_argument('--nx-samples',required=True)
    p.add_argument('--name',required=True);p.add_argument('--author',required=True);p.add_argument('--output',required=True)
    p.add_argument('--grid',type=int,default=32);p.add_argument('--lambda',type=float,default=.5,dest='lam')
    p.add_argument('--camera',default='NIKON Z 8');p.add_argument('--report')
    p=sub.add_parser('export');p.add_argument('lut');p.add_argument('--name',required=True);p.add_argument('--author',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('audit',help='All native tetrahedral faces; not a visibility verdict');p.add_argument('profile');p.add_argument('--output')
    p=sub.add_parser('sample');p.add_argument('tiff');p.add_argument('--metadata',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('prepare-nx');p.add_argument('--source',required=True);p.add_argument('--template',required=True);p.add_argument('--recipes',nargs='+',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('make-target');p.add_argument('--donor',required=True);p.add_argument('--output',required=True);p.add_argument('--confirm-donor-calibration',action='store_true')
    p=sub.add_parser('render');p.add_argument('raw');p.add_argument('--profile');p.add_argument('--amount',type=float,default=1.);p.add_argument('--output',required=True);p.add_argument('--app',default='Adobe Photoshop 2026')
    args=parser.parse_args()
    for key in ('output','report'):
        value=getattr(args,key,None)
        if value and Path(value).exists():parser.error(f'Refusing to overwrite {value}')
    try:
        if args.command=='inspect':
            from .np3 import inspect
            result=inspect(args.recipe)
        elif args.command=='fit':
            if not 2<=args.grid<=32 or not np.isfinite(args.lam) or args.lam<0:raise ValueError('Invalid grid or regularization')
            x,y=read_samples(args.adobe_samples),read_samples(args.nx_samples)
            if x.shape!=y.shape:raise ValueError('Paired sample shapes differ')
            valid=~(((x>.999)|(x<.0005)|(y>.999)|(y<.0005)).any(1))
            if valid.sum()<4:raise ValueError('Too few unclipped calibration pairs')
            lut,solver=NativeFitter(x[valid],args.grid).fit(y[valid],args.lam)
            Path(args.output).write_text(build_profile(lut,args.name,args.author,camera=args.camera))
            error=de2000(lab(lookup(lut,x[valid])),lab(y[valid]))
            result=dict(profile=args.output,samples=int(valid.sum()),mean_de=float(error.mean()),p95_de=float(np.percentile(error,95)),
                        evaluation='training chart, not independent validation',solver=solver,structure=audit(lut))
            if args.report:Path(args.report).write_text(json.dumps(result,indent=2))
        elif args.command=='export':
            lut=np.load(args.lut,allow_pickle=False);Path(args.output).write_text(build_profile(lut,args.name,args.author));result=dict(profile=args.output)
        elif args.command=='audit':
            lut,m=read_profile(args.profile);result=dict(name=m['name'],structure=audit(lut))
            if args.output:Path(args.output).write_text(json.dumps(result,indent=2))
        elif args.command=='sample':
            rows=sample_tiff(args.tiff,args.metadata);Path(args.output).write_text(json.dumps(rows,indent=2));result=dict(samples=len(rows),output=args.output)
        elif args.command=='prepare-nx':
            from .nx import prepare
            result=dict(recipes=prepare(args.source,args.template,args.recipes,args.output))
        elif args.command=='make-target':
            from .target import generate
            result=dict(metadata=str(generate(args.donor,args.output,args.confirm_donor_calibration)))
        elif args.command=='render':
            from .photoshop import render
            result=dict(output=str(render(args.raw,args.output,args.profile,args.amount,args.app)))
        print(json.dumps(result,indent=2,ensure_ascii=False))
    except (ValueError,RuntimeError,OSError) as exc:parser.exit(1,f'{exc}\n')
