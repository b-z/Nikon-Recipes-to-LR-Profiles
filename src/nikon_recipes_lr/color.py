"""Adobe RGB (1998) D65 to Lab and CIEDE2000, kL=kC=kH=1 by default."""
import numpy as np
G=563/256.
M_A2XYZ=np.array([[0.5767309,0.1855540,0.1881852],[0.2973769,0.6273491,0.0752741],[0.0270343,0.0706872,0.9911085]])
WP=M_A2XYZ.sum(1)

def lab(rgb):
    xyz=(np.power(np.clip(rgb,0,None),G))@M_A2XYZ.T/WP
    f=np.where(xyz>216/24389, np.cbrt(xyz), (24389/27*xyz+16)/116)
    return np.stack([116*f[...,1]-16, 500*(f[...,0]-f[...,1]), 200*(f[...,1]-f[...,2])],-1)


def de2000(L1,L2,kL=1.0,kC=1.0,kH=1.0):
    l1,a1,b1=np.moveaxis(np.asarray(L1),-1,0); l2,a2,b2=np.moveaxis(np.asarray(L2),-1,0)
    C1=np.hypot(a1,b1); C2=np.hypot(a2,b2); Cb=(C1+C2)/2
    Gf=0.5*(1-np.sqrt(Cb**7/(Cb**7+25.0**7+1e-12)))
    ap1,ap2=(1+Gf)*a1,(1+Gf)*a2
    Cp1,Cp2=np.hypot(ap1,b1),np.hypot(ap2,b2)
    hp1=np.degrees(np.arctan2(b1,ap1))%360; hp2=np.degrees(np.arctan2(b2,ap2))%360
    dL=l2-l1; dC=Cp2-Cp1
    dh=hp2-hp1; dh=np.where(dh>180,dh-360,np.where(dh<-180,dh+360,dh))
    dh=np.where((Cp1*Cp2)==0,0,dh)
    dH=2*np.sqrt(Cp1*Cp2)*np.sin(np.radians(dh)/2)
    Lb=(l1+l2)/2; Cpb=(Cp1+Cp2)/2
    hsum=hp1+hp2; hdiff=np.abs(hp1-hp2)
    hb=np.where((Cp1*Cp2)==0,hsum,np.where(hdiff<=180,hsum/2,
        np.where(hsum<360,(hsum+360)/2,(hsum-360)/2)))
    T=(1-0.17*np.cos(np.radians(hb-30))+0.24*np.cos(np.radians(2*hb))
       +0.32*np.cos(np.radians(3*hb+6))-0.20*np.cos(np.radians(4*hb-63)))
    Sl=1+0.015*(Lb-50)**2/np.sqrt(20+(Lb-50)**2); Sc=1+0.045*Cpb; Sh=1+0.015*Cpb*T
    Rt=-2*np.sqrt(Cpb**7/(Cpb**7+25.0**7+1e-12))*np.sin(np.radians(60*np.exp(-((hb-275)/25)**2)))
    return np.sqrt((dL/(kL*Sl))**2+(dC/(kC*Sc))**2+(dH/(kH*Sh))**2+Rt*(dC/(kC*Sc))*(dH/(kH*Sh)))
