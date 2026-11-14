"""A responsive 2-1-1 README arrangement using separate self-contained SVG rows."""
import re,math
import xml.etree.ElementTree as ET
from art_common import *
from stats_layouts import activity,streaks,metric_icon
from telemetry import languages,compact_bytes

def language_data(data):
    items=sorted(data['languages'].items(),key=lambda pair:-pair[1])
    items=items if len(items)<=5 else items[:4]+[('Other',sum(n for _,n in items[4:]))]
    return items,sum(data['languages'].values())

def card_height(data):
    return max(312,126+len(language_data(data)[0])*75)

def activity_card(data,animated=True):
    w,h=640,card_height(data)
    out=shell(w,h)+txt("Derol Chong's GitHub Stats",30,55,34,WHITE,limit=580)
    rows=[('star','Stars earned',data['stars']),('repo','Public repositories',data['public_repos']),('activity',str(data['year'])+' contributions',data['contributions']),('calendar','Active days',data['active_days'])]
    for i,(icon,label,value) in enumerate(rows):
        yy=107+i*49
        out+=metric_icon(icon,45,yy-8)+txt(label,70,yy,21,WHITE,limit=265)+txt(value,374,yy,25,CYAN,anchor='end')
    cx,cy,r=514,185,73
    out+=ring(cx,cy,r,LINE,7)+ring(cx,cy,r-12,LINE,1)
    out+='<g>'+path(poly_arc(cx,cy,r,-112,155),CYAN,7)+path(poly_arc(cx,cy,r,181,220),MINT,7)
    if animated:out+=f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/>'
    out+='</g>'+txt(data['contributions'],cx,cy+10,46,WHITE,anchor='middle')+txt(data['year'],cx,cy+36,16,MUTED,'mono','middle')
    return canvas(w,h,"Derol Chong's GitHub Stats",f"{data['stars']} stars, {data['public_repos']} public repositories, {data['contributions']} contributions in {data['year']} and {data['active_days']} active days. The animated count ring is decorative, not a rank.",out)

def languages_card(data,animated=True):
    w,h=640,card_height(data);items,total=language_data(data)
    out=shell(w,h)+txt('Repository languages',30,55,34,WHITE,limit=580)
    cx,cy,r=147,180,82;colors=[CYAN,MINT,BLUE,GOLD,'#d39aff']
    for i in range(72):
        a=math.radians(-90+i*5);inner=r+9;outer=inner+(5 if i%3==0 else 2)
        out+=path(f'M{cx+math.cos(a)*inner} {cy+math.sin(a)*inner}L{cx+math.cos(a)*outer} {cy+math.sin(a)*outer}',MUTED if i%6==0 else LINE,.8)
    out+=ring(cx,cy,r,LINE,12);cursor=-90
    for i,(name,value) in enumerate(items):
        extent=value/max(1,total)*360
        if extent>1.6:out+=path(poly_arc(cx,cy,r,cursor+.8,cursor+extent-.8),colors[i%len(colors)],12)
        cursor+=extent
    out+=txt(compact_bytes(total),cx,cy+1,32,WHITE,anchor='middle')+txt('Source code size',cx,cy+35,16,MUTED,anchor='middle')
    if animated:
        out+='<g>'+path(poly_arc(cx,cy,r+26,-115,-90),MINT,2)+f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/></g>'
    for i,(name,value) in enumerate(items):
        yy=149+i*75;fraction=value/max(1,total);color=colors[i%len(colors)]
        out+=txt(name,290,yy,27,color,limit=190)+txt(f'{fraction*100:.1f}%',608,yy,27,WHITE,anchor='end')
        out+=f'<rect x="290" y="{yy+17}" width="318" height="7" fill="{LINE}"/><rect x="290" y="{yy+17}" width="{318*fraction}" height="7" fill="{color}"/>'
        for j in range(1,12):out+=path(f'M{290+318*j/12} {yy+15}v11',BG,2)
    if not items:out+=txt('No language data yet.',290,149,24,MUTED,limit=318)
    return canvas(w,h,'Repository languages','Public non-fork repository source bytes, not proficiency. '+', '.join(f'{name}: {count:,} bytes' for name,count in items)+'.',out)

def nested(art,key,x,y,w,h):
    for name in sorted(set(re.findall(r'\bid="([^"]+)"',art)),key=len,reverse=True):
        art=art.replace('id="'+name+'"','id="'+key+name+'"').replace('url(#'+name+')','url(#'+key+name+')').replace('href="#'+name+'"','href="#'+key+name+'"')
    art=re.sub(r'aria-labelledby="([^"]+)"',lambda m:'aria-labelledby="'+' '.join(key+n for n in m[1].split())+'"',art)
    head,body=art.split('>',1)
    head=re.sub(r'\bwidth="[^"]+"',f'width="{w}"',head)
    head=re.sub(r'\bheight="[^"]+"',f'height="{h}"',head)
    return head.replace('<svg ',f'<svg x="{x}" y="{y}" ',1)+'>'+body

def top_row(data,mobile=False,animated=True):
    if mobile:
        first=activity(data,True,animated);second=languages(data,True,animated)
        first_h=int(ET.fromstring(first).attrib['height']);second_h=int(ET.fromstring(second).attrib['height'])
        w,h=640,first_h+12+second_h
        body=nested(first,'stats-',0,0,640,first_h)+nested(second,'languages-',0,first_h+12,640,second_h)
    else:
        w,h=1292,card_height(data)
        body=nested(activity_card(data,animated),'stats-',0,0,640,h)+nested(languages_card(data,animated),'languages-',652,0,640,h)
    return canvas(w,h,'Derol Chong - GitHub stats and languages','Two independent cards displayed side by side on desktop and stacked on mobile. Counts and source-byte percentages use public GitHub data.',body)

def streak_row(data,mobile=False,animated=True):
    if mobile:return streaks(data,True,animated)
    body=nested(streaks(data,True,animated),'streak-',262,0,768,336)
    return canvas(1292,336,'Derol Chong - centered contribution streaks',f"{data['contributions']} contributions in {data['year']}, current streak {data['current_streak']} days, longest streak {data['longest_streak']} days. A centered animated streak card.",body)
