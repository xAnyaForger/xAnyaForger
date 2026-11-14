"""GitHub analytics with real measurements, detailed instruments and vector type."""
from datetime import date,timedelta
import math
from art_common import *

def footer(w,h,data):
    return ''


def compact_bytes(value):
    return f'{value/1000000:.2f} MB' if value>=1000000 else f'{value/1000:.1f} KB'

def languages(data,mobile=False,animated=True):
    extra=max(0,min(5,len(data['languages']))-2)*105
    w,h=(640,640+extra) if mobile else (1440,414+extra)
    out=shell(w,h)+txt('Repository languages',38,65,34 if mobile else 39,WHITE)
    raw_langs=sorted(data['languages'].items(),key=lambda item:-item[1]); total=sum(v for _,v in raw_langs)
    langs=raw_langs if len(raw_langs)<=5 else raw_langs[:4]+[('Other',sum(v for _,v in raw_langs[4:]))]
    cx,cy,r=(320,269,116) if mobile else (242,248,117)
    colors=[CYAN,MINT,BLUE,GOLD,'#d39aff']
    for i in range(120):
        a=-90+i*3; inner=r+13; outer=inner+(10 if i%5==0 else 4)
        rad=math.radians(a)
        out+=path(f'M{cx+inner*math.cos(rad)} {cy+inner*math.sin(rad)}L{cx+outer*math.cos(rad)} {cy+outer*math.sin(rad)}',LINE if i%10 else MUTED,1)
    out+=ring(cx,cy,r,LINE,15)
    cursor=-90
    for i,(name,value) in enumerate(langs):
        extent=value/max(1,total)*360
        if extent>0:
            out+=path(poly_arc(cx,cy,r,cursor+.8,cursor+extent-.8),colors[i%len(colors)],15)
        cursor+=extent
    out+=ring(cx,cy,r-25,LINE,.8,extra='stroke-dasharray="2 7"')
    out+=txt(compact_bytes(total),cx,cy+1,36,WHITE,anchor='middle')
    out+=txt('Source code size',cx,cy+35,18,MUTED,anchor='middle')
    if animated:
        out+='<g>'+path(poly_arc(cx,cy,r+26,-115,-90),MINT,2)+f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/></g>'
    bx,by,bw=(48,477,544) if mobile else (483,177,885)
    for i,(name,value) in enumerate(langs[:5]):
        yy=by+i*105; color=colors[i%len(colors)]; share=value/max(1,total)
        out+=txt(name,bx,yy,29,color)+txt(f'{share*100:.1f}%',bx+bw,yy,29,WHITE,anchor='end')
        out+=f'<rect x="{bx}" y="{yy+17}" width="{bw}" height="7" fill="{LINE}"/><rect x="{bx}" y="{yy+17}" width="{max(1,bw*share)}" height="7" fill="{color}"/>'
        # The small hatch marks reveal the exact byte scale instead of inventing a skill level.
        for j in range(1,20): out+=path(f'M{bx+bw*j/20} {yy+15}v11',BG,2)
    if not langs: out+=txt('No public language data yet.',bx,by,20,MUTED)
    return canvas(w,h,'Derol Chong - repository language composition','Public non-fork repository source bytes reported by GitHub: '+', '.join(f'{name}: {value:,} bytes' for name,value in langs)+'. These are not proficiency scores.',out)

