"""GitHub analytics with real measurements, detailed instruments and vector type."""
from datetime import date,timedelta
import math
from art_common import *

def footer(w,h,data):
    return path(f'M36 {h-47}H{w-36}',LINE)+txt('xAnyaForger / PUBLIC GITHUB DATA',36,h-23,11,MUTED,'mono')+txt('UPDATED '+data['as_of'],w-36,h-23,11,MUTED,'mono','end')

def activity(data,mobile=False,animated=True):
    w,h=(640,760) if mobile else (1440,462)
    out=shell(w,h)+txt('A year of building.',38,76,43 if mobile else 49,WHITE)
    out+=txt(str(data['year'])+' / CONTRIBUTION HISTORY',39,105,15,CYAN,'mono')
    out+=txt(data['contributions'],40,208,91,CYAN)+txt('contributions',43,240,23,WHITE)
    items=[(data['public_repos'],'PUBLIC REPOS'),(data['stars'],'STARS EARNED'),(data['active_days'],'ACTIVE DAYS')]
    for i,(value,label) in enumerate(items):
        x=(42+i*190) if mobile else 43+i*113; y=328 if mobile else 327
        out+=txt(value,x,y,37,WHITE)+txt(label,x,y+26,13,MUTED,'mono')
    first=date(data['year'],1,1); end=date.fromisoformat(data['as_of']); days=data['days']
    chart_x,chart_y,chart_w,chart_h=(43,494,550,154) if mobile else (426,141,955,210)
    n=len(days); total=max(1,data['contributions']); running=0; points=[]
    for i,day in enumerate(days):
        running+=day['count']; points.append((chart_x+i/max(1,n-1)*chart_w,chart_y+chart_h-running/total*(chart_h-26)))
    out+=txt('Cumulative contributions',chart_x,chart_y-35,20,WHITE)
    for i in range(5):
        yy=chart_y+chart_h-i*(chart_h-26)/4
        out+=path(f'M{chart_x} {yy}H{chart_x+chart_w}',LINE,.8,extra='stroke-dasharray="2 7"')
        out+=txt(round(total*i/4),chart_x+chart_w,yy-7,13,MUTED,'mono','end')
    route='M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in points)
    if points:
        out+=f'<path d="{route}L{points[-1][0]} {chart_y+chart_h}H{chart_x}Z" fill="url(#area)"/>'+path(route,CYAN,2.5)
        for day,(xx,yy) in zip(days,points):
            if day['count']:
                out+=f'<circle cx="{xx}" cy="{yy}" r="3.4" fill="{MINT}"><title>{day["date"]}: {day["count"]} contributions</title></circle>'
        out+=ring(*points[-1],7,MINT,1.3)
        out+=pulse_route(route,12,0,MINT,animated,3.2)
    for m in [1,3,5,7,9,11]:
        d=date(data['year'],m,1)
        if d>end: continue
        x=chart_x+(d-first).days/max(1,n-1)*chart_w
        out+=path(f'M{x} {chart_y+chart_h+5}v5',MUTED)+txt(d.strftime('%b').upper(),x,chart_y+chart_h+25,13,MUTED,'mono')
    recent=sum(day['count'] for day in days[-30:])
    if mobile:
        out+=path('M42 383H598',LINE)+txt('LAST 30 DAYS',43,408,10,MUTED,'mono')+txt(str(recent)+' contributions',596,409,19,MINT,anchor='end')
        out+=txt('Jan 01 - '+end.strftime('%b %d'),43,688,12,MUTED,'mono')
    else:
        out+=txt('LAST 30 DAYS',chart_x,401,13,MUTED,'mono')+txt(str(recent)+' contributions',chart_x+170,402,19,MINT)
    out+=footer(w,h,data)
    defs='<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#4adfff" stop-opacity=".18"/><stop offset="1" stop-color="#4adfff" stop-opacity=".015"/></linearGradient>'
    return canvas(w,h,'Derol Chong - GitHub activity',f'{data["contributions"]} contributions, {data["active_days"]} active days, {data["public_repos"]} public repositories and {data["stars"]} stars. The cumulative curve uses actual contribution dates. The travelling highlight is decorative.',out,defs)

def compact_bytes(value):
    return f'{value/1000000:.2f} MB' if value>=1000000 else f'{value/1000:.1f} KB'

def languages(data,mobile=False,animated=True):
    extra=max(0,min(5,len(data['languages']))-2)*105
    w,h=(640,790+extra) if mobile else (1440,432+extra)
    out=shell(w,h)+txt('Repository languages',38,65,34 if mobile else 39,WHITE)
    out+=txt('COMPOSITION BY SOURCE BYTES',39,95,11,MUTED,'mono')
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
    out+=txt(compact_bytes(total),cx,cy+1,36,WHITE,anchor='middle')+txt('PUBLIC SOURCE',cx,cy+29,11,MUTED,'mono','middle')
    if animated:
        out+='<g>'+path(poly_arc(cx,cy,r+26,-115,-90),MINT,2)+f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/></g>'
    bx,by,bw=(48,477,544) if mobile else (483,177,885)
    for i,(name,value) in enumerate(langs[:5]):
        yy=by+i*105; color=colors[i%len(colors)]; share=value/max(1,total)
        out+=txt(name,bx,yy,29,color)+txt(f'{share*100:.1f}%',bx+bw,yy,29,WHITE,anchor='end')
        out+=f'<rect x="{bx}" y="{yy+17}" width="{bw}" height="7" fill="{LINE}"/><rect x="{bx}" y="{yy+17}" width="{max(1,bw*share)}" height="7" fill="{color}"/>'
        # The small hatch marks reveal the exact byte scale instead of inventing a skill level.
        for j in range(1,20): out+=path(f'M{bx+bw*j/20} {yy+15}v11',BG,2)
        out+=txt(f'{value:,} bytes',bx,yy+47,12,MUTED,'mono')
    if not langs: out+=txt('No public language data yet.',bx,by,20,MUTED)
    note_y=h-78
    out+=txt('Repository contents, not proficiency.',38 if mobile else 483,note_y,14,MUTED,'mono')+footer(w,h,data)
    return canvas(w,h,'Derol Chong - repository language composition','Public non-fork repository source bytes reported by GitHub: '+', '.join(f'{name}: {value:,} bytes' for name,value in langs)+'. These are not proficiency scores.',out)

def streaks(data,mobile=False,animated=True):
    w,h=(640,776) if mobile else (1440,370)
    out=shell(w,h)+txt('Keep the signal going.',38,64,35 if mobile else 40,WHITE)
    end=date.fromisoformat(data['as_of']); lookup={d['date']:d['count'] for d in data['days']}
    # An explicit two-week window makes breaks and the current run visible.
    dates=[end-timedelta(days=13-i) for i in range(14)]
    if mobile:
        out+=txt(data['current_streak'],42,183,78,CYAN)+txt('days / CURRENT STREAK',143,153,16,CYAN)
        out+=txt(data['current_range'],143,181,12,MUTED,'mono')
        out+=txt(data['longest_streak'],42,286,58,WHITE)+txt('days / LONGEST STREAK',143,254,16,WHITE)
        out+=txt(data['longest_range'],143,282,12,MUTED,'mono')
        gx,gy,step=67,442,82; rows=2
        out+=txt('The last 14 days',40,366,24,WHITE)
    else:
        out+=txt(data['current_streak'],42,183,79,CYAN)+txt('CURRENT STREAK / DAYS',44,214,11,CYAN,'mono')
        out+=txt(data['current_range'],43,243,12,MUTED,'mono')
        out+=txt(data['longest_streak'],277,173,56,WHITE)+txt('LONGEST / DAYS',278,204,10,MUTED,'mono')
        out+=txt(data['longest_range'],278,233,11,MUTED,'mono')
        gx,gy,step=543,175,62; rows=1
        out+=txt('The last 14 days',521,113,22,WHITE)
    for i,day in enumerate(dates):
        xx=gx+(i%7 if mobile else i)*step; yy=gy+(i//7)*145 if mobile else gy
        count=lookup.get(day.isoformat(),0); color=MINT if count else LINE
        if (i%7 if mobile else i)<(6 if mobile else 13):
            route=f'M{xx+20} {yy}H{xx+step-20}'
            next_count=lookup.get(dates[i+1].isoformat(),0)
            out+=path(route,MINT if count and next_count else LINE,2)
            if count and next_count: out+=pulse_route(route,2,0,WHITE,animated,2.2)
        out+=f'<path d="M{xx-17} {yy-10}L{xx} {yy-20}L{xx+17} {yy-10}V{yy+10}L{xx} {yy+20}L{xx-17} {yy+10}Z" fill="{color if count else PANEL}" stroke="{color}" stroke-width="1.4"><title>{day.isoformat()}: {count} contributions</title></path>'
        if count:
            out+=txt(count,xx,yy+6,17,BG,anchor='middle')
        else: out+=f'<circle cx="{xx}" cy="{yy}" r="2" fill="{LINE}"/>'
        out+=txt(day.strftime('%d'),xx,yy+45,11,MUTED,'mono','middle')
        if day==end: out+=txt('TODAY',xx,yy+66,9,CYAN,'mono','middle')
    out+=txt('Lit cells show actual daily contribution counts.',40,h-79,12,MUTED,'mono')+footer(w,h,data)
    return canvas(w,h,'Derol Chong - contribution streak timeline',f'Current streak {data["current_streak"]} days, {data["current_range"]}. Longest streak this year {data["longest_streak"]} days, {data["longest_range"]}. Each lit timeline node contains its genuine contribution count.',out)
