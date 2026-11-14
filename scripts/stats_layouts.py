"""Reference-shaped analytics in the existing HUD style, with genuine counts."""
from datetime import date
import math
from art_common import *

def metric_icon(kind,x,y):
    out=f'<g transform="translate({x} {y})">'
    if kind=='star':
        pts=[]
        for i in range(10):
            a=-math.pi/2+i*math.pi/5;r=11 if i%2==0 else 5
            pts.append(f'{r*math.cos(a):.2f},{r*math.sin(a):.2f}')
        out+='<polygon points="'+' '.join(pts)+'" fill="none" stroke="'+CYAN+'" stroke-width="1.7"/>'
    elif kind=='repo':
        out+=path('M-9 -11H8V10H-9ZM-4 -11V10M-7 14H9V-7',CYAN,1.7)
    elif kind=='activity':
        out+=ring(0,0,11,CYAN,1.7)+path('M-7 0H-3L0 -5L3 5L6 0H9',CYAN,1.7)
    else:
        out+=path('M-10 -8H10V11H-10ZM-10 -2H10M-5 -12V-5M5 -12V-5',CYAN,1.7)
        for xx in [-5,1,6]:out+=f'<rect x="{xx}" y="3" width="2" height="2" fill="{MINT}"/>'
    return out+'</g>'

def activity(data,mobile=False,animated=True):
    w,h=(640,356) if mobile else (1440,330)
    out=shell(w,h)+txt("Derol Chong's GitHub Stats",33 if mobile else 38,57 if mobile else 65,34 if mobile else 39,WHITE,limit=w-75)
    rows=[('star','Stars earned',data['stars']),('repo','Public repositories',data['public_repos']),('activity',str(data['year'])+' contributions',data['contributions']),('calendar','Active days',data['active_days'])]
    for i,(icon,label,value) in enumerate(rows):
        yy=116+i*62 if mobile else 126+i*49
        out+=metric_icon(icon,47 if mobile else 59,yy-8)
        out+=txt(label,72 if mobile else 94,yy,21 if mobile else 25,WHITE,limit=265 if mobile else 610)
        out+=txt(value,374 if mobile else 810,yy,25 if mobile else 29,CYAN,anchor='end')
    cx,cy,r=(514,205,75) if mobile else (1137,191,91)
    out+=ring(cx,cy,r,LINE,7)+ring(cx,cy,r-12,LINE,1)
    out+='<g>'+path(poly_arc(cx,cy,r,-112,155),CYAN,7)+path(poly_arc(cx,cy,r,181,220),MINT,7)
    if animated:out+=f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/>'
    out+='</g>'
    out+=txt(data['contributions'],cx,cy+10,46 if mobile else 56,WHITE,anchor='middle')
    out+=txt(data['year'],cx,cy+36,16 if mobile else 18,MUTED,'mono','middle')
    desc=f"Genuine public GitHub statistics: {data['stars']} stars, {data['public_repos']} repositories, {data['contributions']} contributions in {data['year']} and {data['active_days']} active days. The animated ring frames the real year contribution count; it is decorative, not a rank or performance score."
    return canvas(w,h,"Derol Chong's GitHub Stats",desc,out)

def flame(x,y,animated):
    out=f'<g transform="translate({x} {y})"><g>'
    if animated:out+='<animateTransform attributeName="transform" type="scale" values="1 1;.94 1.05;1 1" dur="1.8s" repeatCount="indefinite"/>'
    out+=f'<path d="M0 -20C1 -9 12 -7 10 3C9 13 0 18 -8 12C-16 6 -12 -3 -5 -8C-6 0 -1 1 1 -3C3 -8 0 -12 0 -20Z" fill="{CYAN}"/><path d="M-2 -2C-2 3 -9 6 -5 11C-1 15 5 10 4 6C3 3 0 2 -2 -2Z" fill="{PANEL}"/></g></g>'
    return out

def streaks(data,mobile=False,animated=True):
    w,h=(640,280) if mobile else (1440,314)
    out=shell(w,h)
    cols=[112,320,528] if mobile else [240,720,1200]
    for xx in ([216,424] if mobile else [480,960]):out+=path(f'M{xx} 38V{h-38}',LINE,1.6)
    left,center,right=cols;cy=105 if mobile else 130;r=57 if mobile else 70
    out+=txt(data['contributions'],left,118 if mobile else 137,48 if mobile else 56,WHITE,anchor='middle')
    out+=txt(str(data['year'])+' contributions',left,174 if mobile else 197,19 if mobile else 23,WHITE,anchor='middle',limit=194 if mobile else 420)
    end=date.fromisoformat(data['as_of'])
    out+=txt('Jan 01 - '+end.strftime('%b %d'),left,212 if mobile else 239,16 if mobile else 20,MUTED,anchor='middle')
    out+=ring(center,cy,r,LINE,5)
    arc=poly_arc(center,cy,r,-77,257)
    out+=f'<path d="{arc}" fill="none" stroke="{CYAN}" stroke-width="5.5" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0">'
    if animated:out+='<animate attributeName="stroke-dashoffset" from="100" to="0" dur="1.8s" fill="freeze"/>'
    out+='</path>'+flame(center,cy-r,animated)
    if animated:
        out+=f'<g><circle cx="{center+r}" cy="{cy}" r="3.5" fill="{MINT}"/><animateTransform attributeName="transform" type="rotate" from="0 {center} {cy}" to="360 {center} {cy}" dur="12s" repeatCount="indefinite"/></g>'
    out+=txt(data['current_streak'],center,cy+17,48 if mobile else 56,WHITE,anchor='middle')
    out+=txt('Current streak',center,207 if mobile else 246,20 if mobile else 23,CYAN,anchor='middle')
    out+=txt(data['current_range'],center,237 if mobile else 278,16 if mobile else 20,MUTED,anchor='middle',limit=193 if mobile else 420)
    out+=txt(data['longest_streak'],right,118 if mobile else 137,48 if mobile else 56,WHITE,anchor='middle')
    out+=txt('Longest streak',right,174 if mobile else 197,20 if mobile else 23,WHITE,anchor='middle')
    out+=txt(data['longest_range'],right,212 if mobile else 239,16 if mobile else 20,MUTED,anchor='middle',limit=193 if mobile else 420)
    desc=f"{data['contributions']} contributions in {data['year']}, through {data['as_of']}. Current streak: {data['current_streak']} days, {data['current_range']}. Longest streak within the displayed year: {data['longest_streak']} days, {data['longest_range']}. The ring draws on load, its marker orbits and its flame gently flickers; counts remain genuine."
    return canvas(w,h,'Derol Chong - contribution streaks',desc,out)
