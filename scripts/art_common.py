"""Shared self-contained vector lettering and geometry. Python stdlib at runtime."""
from pathlib import Path
from html import escape
import json, math

CYAN='#4adfff'; MINT='#60ffd1'; BLUE='#2d8bff'; WHITE='#daf5ff'
MUTED='#8bafc4'; LINE='#164457'; BG='#030b12'; PANEL='#06141e'; GOLD='#ffc477'
LETTERS=json.loads((Path(__file__).parent/'letterforms.json').read_text(encoding='utf-8'))

def txt(value,x,y,size=20,color=WHITE,font='display',anchor='start',limit=None):
    value=str(value); face=LETTERS[font]; factor=size/face['upem']
    length=sum(face['glyphs'].get(c,face['glyphs'][' '])['advance'] for c in value)*factor
    if limit and length>limit: factor*=limit/length; length=limit
    if anchor=='middle': x-=length/2
    elif anchor=='end': x-=length
    out=f'<g aria-label="{escape(value,quote=True)}" fill="{color}">'
    for c in value:
        glyph=face['glyphs'].get(c,face['glyphs'][' '])
        if glyph['path']: out+=f'<path transform="translate({x:.3f} {y:.3f}) scale({factor:.6f} {-factor:.6f})" d="{glyph["path"]}"/>'
        x+=glyph['advance']*factor
    return out+'</g>'

def path(d,color=LINE,width=1,extra=''):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>'

def ring(x,y,r,color=LINE,width=1,extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>'

def poly_arc(cx,cy,r,start,end):
    a,b=math.radians(start),math.radians(end)
    return f'M{cx+r*math.cos(a):.3f} {cy+r*math.sin(a):.3f}A{r} {r} 0 {int(end-start>180)} 1 {cx+r*math.cos(b):.3f} {cy+r*math.sin(b):.3f}'

def shell(w,h):
    return f'<rect width="{w}" height="{h}" fill="{BG}"/><path d="M24 12H{w-40}L{w-12} 40V{h-24}L{w-24} {h-12}H40L12 {h-40}V24Z" fill="{PANEL}" stroke="{LINE}"/><path d="M34 12H155M{w-12} {h-94}V{h-34}" stroke="{CYAN}" stroke-width="2"/>'

def canvas(w,h,title,desc,body,defs=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><defs>{defs}</defs>{body}</svg>'

def pulse_route(route,duration=4,delay=0,color=CYAN,animated=True,r=3):
    if not animated: return ''
    return f'<circle r="{r}" fill="{color}"><animateMotion path="{route}" dur="{duration}s" begin="-{delay}s" repeatCount="indefinite"/></circle>'

def appear(start,end,period=18):
    # Closed-loop time window, with a short fade at either edge.
    start=max(.01,start); end=min(period-.02,end)
    return f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{(start-.01)/period:.6f};{start/period:.6f};{end/period:.6f};{(end+.01)/period:.6f};1" dur="{period}s" repeatCount="indefinite"/>'
