"""NEURAL ARCADE: an original flat 2D circuit puzzle, Python stdlib only.

The agent is an illustrative character. Its story is not a training metric;
the calendar, counters, cache lights and activity rails use real input data.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import json
import math

from art_common import (
    CYAN, MINT, BLUE, WHITE, MUTED, LINE, BG, PANEL, GOLD,
    txt, path, ring, canvas, shell, pulse_route, appear,
)

PERIOD = 24


def rect(x, y, w, h, fill=PANEL, stroke=LINE, rx=0, extra=''):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" {extra}/>')


def poly(points, fill, stroke=LINE, width=1, extra=''):
    return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def timed(attr, values, times, animated=True, mode='linear', dur=PERIOD):
    if not animated:
        return ''
    return (f'<animate attributeName="{attr}" values="{values}" keyTimes="{times}" '
            f'dur="{dur}s" repeatCount="indefinite" calcMode="{mode}"/>')


def visible(start, end, animated=True, second=None):
    if not animated:
        return ''
    start=max(.02,start)
    if second is None:
        return appear(start, end, PERIOD)
    events = [(0, 0), (max(.001, start-.02), 0), (start, 1), (end, 1),
              (end+.02, 0), (second[0]-.02, 0), (second[0], 1),
              (second[1], 1), (min(23.999, second[1]+.02), 0), (24, 0)]
    return timed('opacity', ';'.join(str(v) for _, v in events),
                 ';'.join(f'{t/24:.6f}' for t, _ in events))


def clipped_panel(x, y, w, h, fill='#071a25', stroke=LINE, cut=12):
    return path(f'M{x+cut} {y}H{x+w}V{y+h-cut}L{x+w-cut} {y+h}H{x}V{y+cut}Z',
                stroke, 1, f'fill="{fill}"').replace('fill="none" ', '')


def floor_ticks(x, y, w, h):
    p = ''
    for xx in range(int(x+12), int(x+w), 32):
        p += path(f'M{xx} {y}v4M{xx} {y+h}v-4', '#1d4353', .7)
    for yy in range(int(y+12), int(y+h), 32):
        p += path(f'M{x} {yy}h4M{x+w} {yy}h-4', '#1d4353', .7)
    return p


def corner_marks(x, y, r, color=CYAN):
    d = f'M{x-r} {y-r+9}v-9h9M{x+r-9} {y-r}h9v9M{x+r} {y+r-9}v9h-9M{x-r+9} {y+r}h-9v-9'
    return path(d, color, 1.2)


def node(x, y, label=None, color=CYAN, radius=8):
    s = ring(x, y, radius+5, '#204452', 1) + ring(x, y, radius, color, 1.5)
    s += f'<circle cx="{x}" cy="{y}" r="2.4" fill="{color}"/>'
    if label:
        s += txt(label, x, y+radius+22, 10, MUTED, font='mono', anchor='middle')
    return s


def corridor(d, width=48, color='#173f50'):
    return (path(d, '#020a11', width+9, 'stroke-linejoin="round"') +
            path(d, color, width+2, 'stroke-linejoin="round"') +
            path(d, '#09202b', width-1, 'stroke-linejoin="round"') +
            path(d, '#204956', 1, 'stroke-dasharray="2 8"'))


def chevrons(x, y, direction='right', color=CYAN):
    shape = 'M-6 -5L0 0L-6 5M2 -5L8 0L2 5'
    rot = {'right': 0, 'down': 90, 'left': 180, 'up': -90}[direction]
    return f'<g transform="translate({x} {y}) rotate({rot})">{path(shape,color,1.2)}</g>'


def robot(animated=True, ghost=False):
    c = GOLD if ghost else MINT
    s = '<g>'
    if not ghost:
        # The thin cone makes the small character feel like a seeing, embodied agent.
        s += '<g opacity=".12">' + poly('13,-5 72,-30 72,30 13,5', CYAN, 'none')
        s += path('M72 -30Q88 0 72 30', CYAN, 1) + '</g>'
        s += ring(0, 0, 23, CYAN, .6, 'opacity=".32" stroke-dasharray="2 5"')
    s += path('M-8 12v7h-5M8 12v7h5', c, 2, 'stroke-linecap="square"')
    s += path('M-17 -3h-4v12h5M17 -3h4v12h-5', BLUE if not ghost else GOLD, 3)
    s += path('M0 -16v-7h5', c, 1.4)
    s += f'<circle cx="6" cy="-23" r="2.4" fill="{c}">'
    s += timed('opacity', '1;.25;1', '0;.5;1', animated and not ghost, dur=1.2) + '</circle>'
    s += poly('-11,-14 11,-14 16,-8 16,10 10,15 -10,15 -16,9 -16,-8', '#0b2633', c, 1.6)
    s += rect(-11, -8, 22, 12, '#071017', BLUE if not ghost else GOLD, 3)
    s += rect(-7, -4, 4, 4, c, 'none', 1) + rect(3, -4, 4, 4, c, 'none', 1)
    s += path('M-4 9h8', c, 1.5) + '</g>'
    return s


def launch(x, y, mobile=False):
    r = 38 if mobile else 45
    p = poly(' '.join(f'{x+math.cos(a)*r:.2f},{y+math.sin(a)*r:.2f}'
                     for a in [math.radians(22.5+45*i) for i in range(8)]), '#0a2935', '#286179', 1)
    p += ring(x, y, r-8, '#1c576a', 1) + ring(x, y, r-14, CYAN, 1, 'stroke-dasharray="3 8"')
    p += corner_marks(x, y, r+6, '#2b7b92')
    p += txt('A-01', x, y+r+30, 13, WHITE, font='mono', anchor='middle')
    p += txt('LAUNCH DOCK', x, y+r+45, 10, MUTED, font='mono', anchor='middle')
    return p


def blocked(x, y, vertical=False, animated=True):
    rot = 90 if vertical else 0
    p = f'<g transform="translate({x} {y}) rotate({rot})">'
    p += rect(-10, -31, 20, 62, '#34291d', GOLD)
    for yy in range(-26, 30, 11):
        p += path(f'M-8 {yy}l16 -8', GOLD, 4)
    p += rect(-16, -40, 32, 8, '#14303b', '#547078', 1)
    p += rect(-16, 32, 32, 8, '#14303b', '#547078', 1)
    p += '</g>'
    # A visibly physical wall, with a feedback pulse only while being encountered.
    if animated:
        p += f'<g opacity="0">{visible(4.7,6.0,animated)}'
        p += ring(x, y, 48, GOLD, 2, 'stroke-dasharray="4 5"') + '</g>'
    return p


def phase_gate(x, y, animated=True):
    p = rect(x-13, y-47, 26, 18, '#123242', BLUE, 2)
    p += rect(x-13, y+29, 26, 18, '#123242', BLUE, 2)
    p += path(f'M{x-22} {y-39}h-8v78h8M{x+22} {y-39}h8v78h-8', '#235568', 1)
    for yy in [-38, 38]:
        p += rect(x-7, y+yy-2, 14, 4, MINT, 'none')
    p += '<g opacity="1">'
    if animated:
        p += timed('opacity', '1;1;0;0;1', '0;.4458;.4625;.9916;1')
    else:
        p += '<g opacity=".12">'
    p += path(f'M{x-5} {y-27}v54M{x+5} {y-27}v54', CYAN, 2, 'stroke-dasharray="4 3"')
    if not animated:
        p += '</g>'
    p += '</g>'
    return p


def scanner(x, y, r=43, animated=True):
    points = ' '.join(f'{x+math.cos(math.radians(30+60*i))*r:.2f},{y+math.sin(math.radians(30+60*i))*r:.2f}' for i in range(6))
    p = poly(points, '#082932', '#2b798c', 1.2)
    p += ring(x, y, r-9, '#1a5b6a') + ring(x, y, r-16, CYAN, 1, 'stroke-dasharray="3 5"')
    p += path(f'M{x-17} {y}h34M{x} {y-17}v34', '#337182', .7)
    p += poly(f'{x-11},{y} {x},{y-11} {x+11},{y} {x},{y+11}', '#1e5a6b', CYAN, 1)
    p += '<g>'
    if animated:
        p += (f'<animateTransform attributeName="transform" type="rotate" from="0 {x} {y}" '
              f'to="360 {x} {y}" dur="8s" repeatCount="indefinite"/>')
    p += path(f'M{x} {y-r+5}v10M{x} {y+r-5}v-10', MINT, 3) + '</g>'
    return p


def memory_bank(x, y, data, mobile=False, animated=True):
    w, h = (100, 62) if mobile else (140, 70)
    p = clipped_panel(x-w/2, y-h/2, w, h, '#0a202c', '#326072', 8)
    active = int(data.get('active_days', sum(bool(d.get('count', 0)) for d in data.get('days', []))))
    for i in range(12):
        xx = x-w/2+14+(i%6)*(12 if mobile else 20)
        yy = y-h/2+14+(i//6)*19
        fill = MINT if i < min(12, active) else '#123341'
        p += rect(xx, yy, 7 if mobile else 11, 9, fill, 'none', 1,
                  extra='opacity=".82"' if i < active else '')
    p += txt('SIGNAL CACHE', x, y+h/2-8, 9, MUTED, font='mono', anchor='middle')
    for dx in [-1, 1]:
        p += path(f'M{x+dx*(w/2+5)} {y-14}v28', '#235165', 3)
    return p


def portal(x, y, r=46, animated=True, label_dy=28):
    p = corner_marks(x, y, r+13, '#255669')
    p += poly(' '.join(f'{x+math.cos(math.radians(22.5+45*i))*(r+4):.2f},{y+math.sin(math.radians(22.5+45*i))*(r+4):.2f}' for i in range(8)), '#081e2b', '#28677b', 2)
    p += ring(x, y, r-4, BLUE, 4) + ring(x, y, r-11, CYAN, 1)
    p += ring(x, y, r-18, '#1c4a60', 1)
    p += '<g>'
    if animated:
        p += (f'<animateTransform attributeName="transform" type="rotate" from="0 {x} {y}" '
              f'to="-360 {x} {y}" dur="24s" repeatCount="indefinite"/>')
    p += ring(x, y, r+2, MINT, 3, 'stroke-dasharray="18 61"') + '</g>'
    p += '<g opacity=".12">'
    if animated:
        p += timed('opacity', '.12;.12;.82;.82;.2;.2;.82;.82;.12',
                   '0;.62;.65;.74;.75;.94;.95;.985;1')
    p += f'<circle cx="{x}" cy="{y}" r="{r-14}" fill="{MINT}" filter="url(#arc-glow)"/>'
    p += '</g>'
    p += txt('EXIT / 01', x, y+r+label_dy, 12, WHITE, font='mono', anchor='middle')
    return p


def speech(x, y, animated=True):
    p = '<g opacity="0">' + visible(4.7, 5.9, animated)
    p += poly(f'{x-5},{y+28} {x-13},{y+40} {x-12},{y+27}', '#172222', GOLD, 1)
    p += rect(x-24, y-1, 48, 32, '#142330', GOLD, 5)
    p += txt('?!', x, y+22, 23, GOLD, anchor='middle')
    return p + '</g>' if animated else ''


def celebration(x, y, animated=True):
    p = '<g opacity="0">' + visible(15.8, 17.85, animated, (22.9, 23.65))
    if not animated:
        return ''
    for i, (dx, dy) in enumerate([(-65,-40),(-40,-68),(0,-76),(46,-64),(68,-30),(67,31),(28,66),(-42,63)]):
        c = MINT if i%2 else CYAN
        xx, yy = x+dx, y+dy
        p += path(f'M{xx-4} {yy}h8M{xx} {yy-4}v8', c, 1.8)
        p += rect(xx+8, yy-11, 3, 3, GOLD if i%3==0 else c, 'none')
    return p + '</g>'


def calendar(data, x, y, cell=7, gap=3, label=True, max_width=None):
    days = data.get('days', [])
    if not days:
        return txt('CONTRIBUTION SIGNAL NOT AVAILABLE', x, y+20, 11, MUTED, font='mono')
    first = date.fromisoformat(days[0]['date'])
    start = first - timedelta(days=first.weekday())
    step = cell+gap
    columns = max((date.fromisoformat(d['date'])-start).days//7 for d in days)+1
    width = (columns-1)*step+cell
    if max_width and width > max_width:
        scale=max_width/width
        step*=scale
        cell*=scale
    colors = ['#102836', '#16546d', '#217ea2', BLUE, MINT]
    p = ''
    months = set()
    for d in days:
        day = date.fromisoformat(d['date'])
        offset = (day-start).days
        week, row = divmod(offset, 7)
        level = min(4, max(0, int(d.get('level', 0))))
        if int(d.get('count', 0)) and level == 0:
            level = 1
        p += rect(x+week*step, y+row*step, cell, cell, colors[level], 'none', 1)
        if day.month not in months:
            months.add(day.month)
            if label:
                p += txt(day.strftime('%b').upper(), x+week*step, y-7, 8, MUTED, font='mono')
    return p


def status(x, y, width, animated=True, mobile=False):
    p = rect(x, y, width, 35 if mobile else 42, '#0b2634', '#21546b', 3)
    p += f'<circle cx="{x+14}" cy="{y+17}" r="3" fill="{MINT}"/>'
    rows = [('01 / SCOUT', .04, 4.65), ('02 / RETHINK', 4.68, 8.45),
            ('03 / REMEMBER', 8.48, 18.0), ('04 / REPLAY', 18.03, 23.96)]
    if animated:
        for text, a, b in rows:
            p += '<g opacity="0">' + visible(a,b,True)
            p += txt(text, x+27, y+23, 13 if mobile else 17, MINT, font='mono') + '</g>'
    else:
        p += txt('MEMORY / READY', x+27, y+23, 13 if mobile else 17, MINT, font='mono', limit=width-38)
    return p


def story_hud(x, y, w, h, animated=True):
    p = clipped_panel(x,y,w,h,'#071722','#245065')
    p += txt('PATHFINDER / A-01', x+22, y+29, 15, CYAN, font='mono')
    p += path(f'M{x+22} {y+43}H{x+w-22}', LINE, 1)
    p += txt('CURRENT PHASE', x+22, y+65, 10, MUTED, font='mono')
    p += status(x+20,y+77,w-40,animated)
    notes = [('01','SCOUT','A shortcut looks promising.',0,4.65,CYAN),
             ('02','RETHINK','Turns out: wall.',4.7,8.45,GOLD),
             ('03','REMEMBER','Keep the useful route.',8.5,18,MINT),
             ('04','REPLAY','Less guessing. More going.',18.05,23.95,CYAN)]
    for i,(n,title,sub,a,b,col) in enumerate(notes):
        yy = y+153+i*47
        if animated:
            p += '<g opacity="0">' + visible(a,b,True)
            p += rect(x+13,yy-23,w-26,43,'#0e2a36','none',3) + '</g>'
        p += txt(n,x+24,yy-5,12,col,font='mono')
        p += txt(title,x+58,yy-6,14,WHITE)
        p += txt(sub,x+58,yy+10,10,MUTED,font='mono',limit=w-77)
    p += path(f'M{x+22} {y+h-44}H{x+w-22}', LINE, 1)
    p += txt('AN ILLUSTRATED AGENT STORY',x+22,y+h-24,9,MUTED,font='mono',limit=w-44)
    p += txt('ACTIVITY SIGNALS ARE REAL.',x+22,y+h-9,9,MUTED,font='mono',limit=w-44)
    return p


def trajectory(points, animated=True):
    if not animated:
        x, y = points[12][1:]
        return f'<g transform="translate({x} {y})">{robot(False)}</g>'
    coords = ';'.join(f'{x} {y}' for _,x,y in points)
    times = ';'.join(f'{t/24:.6f}' for t,_,_ in points)
    p = '<g transform="translate(0 0)">'
    p += f'<animateTransform attributeName="transform" type="translate" values="{coords}" keyTimes="{times}" dur="24s" repeatCount="indefinite"/>'
    p += timed('opacity','1;1;0;0;1;1;0;0;1','0;.74;.75;.7504;.767;.98;.99;.9904;1')
    p += robot(True) + '</g>'
    return p


def route_layer(good, bad, animated=True):
    p = path(good, BLUE, 2, 'opacity=".22"')
    p += f'<g opacity="{0 if animated else .55}">'
    if animated:
        p += visible(5.0, 23.8)
    p += path(bad,GOLD,2,'stroke-dasharray="3 8" opacity=".52"') + '</g>'
    p += f'<path d="{good}" pathLength="1000" fill="none" stroke="{MINT}" stroke-width="3" stroke-linejoin="round" opacity=".85" '
    p += f'stroke-dasharray="1000" stroke-dashoffset="{1000 if animated else 0}">'
    p += timed('stroke-dashoffset','1000;1000;0;0;1000','0;.35417;.6625;.986;1',animated)
    p += '</path>'
    return p


def desktop(data, animated=True):
    w,h=1440,700
    p = shell(w,h)
    p += txt('WORLD 01 / DEROL CHONG',42,33,11,CYAN,font='mono')
    p += txt('NEURAL ARCADE',40,86,53,WHITE)
    p += txt('A small agent. A bad shortcut. A better way through.',43,115,16,MUTED)
    p += txt('EXPLORE / REMEMBER / REPLAY',1394,38,12,MINT,font='mono',anchor='end')
    p += txt('xAnyaForger',1394,73,25,WHITE,anchor='end')
    p += txt('CIRCUIT FACILITY  /  24s LOOP',1394,101,11,MUTED,font='mono',anchor='end')

    # The facility has inhabited islands, recesses and service tracks, rather than an empty grid.
    p += clipped_panel(40,146,1048,404,'#04131d','#2b5364',16)
    p += '<path d="M40 146H1088V550H40Z" fill="url(#arc-grid)" opacity=".6"/>'
    p += floor_ticks(40,146,1048,404)
    p += txt('SECTOR 01 / OPEN CIRCUIT',60,169,10,MUTED,font='mono')
    p += txt('MISSION: UNLOCK THE EXIT',1067,169,10,CYAN,font='mono',anchor='end')

    # Service traces and deeply drawn landmarks establish the floor plan.
    p += path('M65 194H178L204 220V274M72 471H210V502H450M660 195V279H705M679 488H946V440H1055', '#164255', 2)
    p += path('M65 201H170L196 227V274M72 478H202V509H450M668 195V272H705M679 495H953V447H1055', '#0b2b3d', 1)
    p += path('M620 445H694V406H847V467H884M850 275H888V253H1029', '#123d50', 2)
    p += pulse_route('M65 194H178L204 220V274', 4, 1, BLUE, animated, 2)
    p += pulse_route('M679 488H946V440H1055', 7, 3, CYAN, animated, 2)

    # Three environmental islands with specific, non-code functions.
    p += clipped_panel(81,185,114,72,'#09202a','#1a4c5c',8)
    p += ring(110,219,17,'#2f7a90',1) + ring(110,219,9,CYAN,1)
    p += path('M110 198v8M110 232v8M89 219h8M123 219h8',CYAN,1)
    p += txt('BOOT',140,215,12,WHITE) + txt('ARRAY',140,232,10,MUTED,font='mono')
    for i in range(5):
        p += rect(92+i*20,248,11,3,CYAN if i<3 else '#1e3d4b','none')
    p += clipped_panel(598,397,245,79,'#071e29','#1a495a',8)
    p += txt('ROUTE MEMORY',613,418,12,MUTED,font='mono')
    for i in range(8):
        yy=440+(i%3)*6
        p += path(f'M{615+i*25} {yy}h11l5 -8', MINT if i<5 else '#255362',1.2)
    p += txt('STORE THE TURN. SKIP THE WALL.',613,462,9,'#688fa4',font='mono')
    p += clipped_panel(910,442,137,73,'#08212b','#214b5c',8)
    p += txt('SIGNAL',925,463,11,MUTED,font='mono')
    for i in range(8):
        hh=8+(i*11+int(data.get('contributions',0)))%24
        p += rect(924+i*13,500-hh,7,hh,CYAN if i%3 else BLUE,'none',1, 'opacity=".65"')

    good='M135 330H290V446H520V330H760V220H930V330H1010'
    bad='M290 330V220H540'
    full='M135 330H290V220H570M290 330V446H520V330H760V220H930V330H1010'
    p += corridor(full)
    # Secondary branches read as optional puzzle rooms; all turn back into the main facility.
    p += corridor('M520 330V265H650',28,'#123244')
    p += corridor('M760 330H853V385',28,'#123244')
    p += node(650,265,None,BLUE,7) + node(853,385,None,BLUE,7)
    p += txt('AUX / 02',650,247,9,MUTED,font='mono',anchor='middle')
    p += txt('IDLE RELAY',853,410,9,MUTED,font='mono',anchor='middle')

    p += launch(135,330)
    p += node(290,330,None,CYAN,17)
    p += ring(290,330,26,'#296273',1,'stroke-dasharray="3 6"')
    p += txt('DECISION NODE',290,385,10,MUTED,font='mono',anchor='middle')
    p += txt('THE SHORTCUT',405,192,12,GOLD,font='mono',anchor='middle')
    p += blocked(570,220,False,animated)
    p += txt('NO THROUGH ROUTE',585,275,9,GOLD,font='mono',anchor='middle')
    p += chevrons(365,220,'right','#6a6550')
    p += memory_bank(405,446,data,False,animated)
    p += txt('ACTIVITY-POWERED CACHE',405,510,10,MUTED,font='mono',anchor='middle')
    p += phase_gate(631,330,animated)
    p += txt('PHASE GATE',631,288,10,MUTED,font='mono',anchor='middle')
    p += scanner(760,220,44,animated)
    p += txt('VISION ARRAY',760,189,10,MUTED,font='mono',anchor='middle')
    p += node(930,220,None,BLUE,12)
    p += txt('FINAL TURN',944,194,9,MUTED,font='mono',anchor='middle')
    p += portal(1010,330,46,animated)
    p += route_layer(good,bad,animated)
    for x,y,direction in [(290,408,'down'),(487,446,'right'),(520,369,'up'),(699,330,'right'),(760,280,'up'),(874,220,'right'),(930,282,'down')]:
        p += chevrons(x,y,direction,'#36828c')
    if animated:
        p += '<g opacity="0">' + visible(5.8,23.7)
        p += f'<g transform="translate(540 220)" opacity=".32">{robot(False,True)}</g></g>'
    else:
        p += f'<g transform="translate(540 220)" opacity=".28">{robot(False,True)}</g>'
    p += speech(539,162,animated)
    points=[(0,135,330),(.8,135,330),(2.3,290,330),(3.2,290,220),(4.9,540,220),(5.7,540,220),
            (7,290,220),(7.8,290,330),(8.5,290,330),(9.5,290,446),(10.9,520,446),
            (11.8,520,330),(13,760,330),(13.7,760,220),(14.7,930,220),(15.3,930,330),
            (15.9,1010,330),(18,1010,330),(18.01,135,330),(18.4,135,330),
            (19,290,330),(19.4,290,446),(20.2,520,446),(20.7,520,330),(21.3,760,330),
            (21.7,760,220),(22.2,930,220),(22.6,930,330),(23,1010,330),(23.75,1010,330),
            (23.76,135,330),(24,135,330)]
    p += trajectory(points,animated)
    p += celebration(1010,330,animated)
    p += '<g opacity="0">' + visible(15.9,17.8,animated,(22.95,23.65)) + txt('NICE.',1010,253,15,MINT,font='mono',anchor='middle') + '</g>' if animated else ''
    p += txt('01 / FIND A WAY',61,532,9,'#598298',font='mono')
    p += txt('02 / LEAVE A TRACE',424,532,9,'#598298',font='mono')
    p += txt('03 / DO IT AGAIN, BETTER',1065,532,9,'#598298',font='mono',anchor='end')
    p += story_hud(1110,146,286,404,animated)

    p += clipped_panel(40,572,1356,101,'#051721','#214b5c')
    p += txt('REAL GITHUB SIGNAL',60,596,11,CYAN,font='mono')
    p += txt(data.get('contributions',0),59,647,45,WHITE,limit=72)
    p += txt('CONTRIBUTIONS',141,624,12,MUTED,font='mono')
    p += txt(f"{data.get('year',date.today().year)} / ACTIVITY ENERGY",141,646,10,MUTED,font='mono')
    p += calendar(data,370,596,7,3,max_width=465)
    p += path('M865 587V659',LINE,1)
    p += txt(f"{data.get('active_days',0)} ACTIVE DAYS",892,609,18,MINT)
    p += txt(f"{data.get('public_repos',0)} REPOSITORIES  /  {data.get('stars',0)} STARS",892,637,11,MUTED,font='mono')
    p += txt('DARK = QUIET DAY',1170,611,9,MUTED,font='mono')
    for i,c in enumerate(['#102836','#16546d','#217ea2',BLUE,MINT]):
        p += rect(1170+i*15,626,10,10,c,'none',1)
    p += txt(f"UPDATED {data.get('as_of','')}",1373,659,9,'#597f93',font='mono',anchor='end')
    return canvas(w,h,'Neural Arcade — Derol Chong',
                  'An original 2D circuit puzzle. A tiny agent tries a blocked shortcut, remembers a useful route, unlocks an exit, and replays it. This illustrative story is driven by real GitHub contribution counts, calendar cells, cache lights and activity signals; it does not represent actual reinforcement learning or measured agent performance.',p,defs())


def mobile(data, animated=True):
    w,h=640,1000
    p=shell(w,h)
    p+=txt('WORLD 01 / DEROL CHONG',28,32,10,CYAN,font='mono')
    p+=txt('NEURAL ARCADE',26,76,38,WHITE)
    p+=txt('A small agent finds a better way through.',29,101,14,MUTED)
    p+=txt(f"{data.get('contributions',0)} CONTRIBUTIONS  /  {data.get('active_days',0)} ACTIVE DAYS",29,124,12,MINT,font='mono',limit=580)
    p+=clipped_panel(28,147,584,632,'#04131d','#2b5364',14)
    p+='<path d="M28 147H612V779H28Z" fill="url(#arc-grid)" opacity=".6"/>'
    p+=floor_ticks(28,147,584,632)
    p+=txt('SECTOR 01 / OPEN CIRCUIT',45,171,10,MUTED,font='mono')
    p+=status(354,157,240,animated,True)

    # A portrait-native floor plan, with the story descending through the facility.
    p+=path('M47 199H170V269H208M47 625H75V710H235M378 373H554V563H595M372 730H578V751', '#164255',2)
    p+=path('M47 206H162V277H208M54 625H82V703H235M378 381H546V563H595', '#0d2d3d',1)
    p+=pulse_route('M378 373H554V563H595',6,2,BLUE,animated,2)
    p+=clipped_panel(400,408,140,75,'#0a202b','#1e4c60',8)
    p+=txt('SIGNAL ARRAY',414,430,10,MUTED,font='mono')
    for i in range(8):
        hh=7+(i*11+int(data.get('contributions',0)))%23
        p+=rect(416+i*14,469-hh,7,hh,CYAN if i%3 else BLUE,'none',1,'opacity=".65"')
    p+=clipped_panel(181,588,104,70,'#071d27','#1e4c60',8)
    p+=txt('MEMORY',195,609,10,MUTED,font='mono')
    for i in range(4):
        p+=path(f'M{195+i*18} {632+(i%2)*5}h8l4 -8',MINT if i<3 else '#265362',1.2)
    p+=txt('KEEP THE TURN.',195,648,8,'#648b9d',font='mono')

    good='M105 235H280V380H120V535H350V680H520'
    bad='M280 235H480V310'
    full='M105 235H480V340M280 235V380H120V535H350V680H520'
    p+=corridor(full,44)
    p+=corridor('M350 535V413H325',24,'#123244')
    p+=node(325,413,None,BLUE,7)
    p+=txt('AUX / 02',325,393,9,MUTED,font='mono',anchor='middle')
    p+=launch(105,235,True)
    p+=node(280,235,None,CYAN,16)+ring(280,235,24,'#296273',1,'stroke-dasharray="3 6"')
    p+=txt('DECISION',280,205,10,MUTED,font='mono',anchor='middle')
    p+=txt('SHORTCUT?',427,211,11,GOLD,font='mono',anchor='middle')
    p+=blocked(480,340,True,animated)
    p+=txt('NOPE.',536,346,11,GOLD,font='mono')
    p+=memory_bank(120,456,data,True,animated)
    p+=txt('ACTIVITY CACHE',120,509,9,MUTED,font='mono',anchor='middle')
    p+=phase_gate(235,535,animated)
    p+=txt('PHASE GATE',235,486,9,MUTED,font='mono',anchor='middle')
    p+=scanner(350,535,43,animated)
    p+=txt('VISION ARRAY',350,598,10,MUTED,font='mono',anchor='middle')
    p+=portal(520,680,42,animated,label_dy=16)
    p+=route_layer(good,bad,animated)
    for x,y,direction in [(280,321,'down'),(207,380,'left'),(120,414,'down'),(189,535,'right'),(350,638,'down'),(445,680,'right')]:
        p+=chevrons(x,y,direction,'#36828c')
    p+=chevrons(392,235,'right','#6a6550')
    if animated:
        p+='<g opacity="0">'+visible(5.8,23.7)+f'<g transform="translate(480 310)" opacity=".3">{robot(False,True)}</g></g>'
    else:
        p+=f'<g transform="translate(480 310)" opacity=".28">{robot(False,True)}</g>'
    p+=speech(537,269,animated)
    points=[(0,105,235),(.8,105,235),(2.3,280,235),(3.2,480,235),(4.9,480,310),(5.7,480,310),
            (7,480,235),(7.8,280,235),(8.5,280,235),(9.5,280,380),(10.9,120,380),
            (11.8,120,535),(13,350,535),(13.7,350,610),(14.7,350,680),(15.3,450,680),
            (15.9,520,680),(18,520,680),(18.01,105,235),(18.4,105,235),
            (19,280,235),(19.4,280,380),(20.2,120,380),(20.7,120,535),(21.3,350,535),
            (21.7,350,610),(22.2,350,680),(22.6,450,680),(23,520,680),(23.75,520,680),
            (23.76,105,235),(24,105,235)]
    p+=trajectory(points,animated)
    p+=celebration(520,680,animated)
    if animated:
        p+='<g opacity="0">'+visible(15.9,17.8,True,(22.95,23.65))+txt('NICE.',520,610,14,MINT,font='mono',anchor='middle')+'</g>'
    p+=path('M48 750H591',LINE,1)
    p+=txt('SCOUT',49,733,10,CYAN,font='mono')
    p+=txt('RETHINK',147,733,10,GOLD,font='mono')
    p+=txt('REMEMBER',269,733,10,MINT,font='mono')
    p+=txt('REPLAY',415,733,10,CYAN,font='mono')
    p+=path('M98 729h32m-5-4 5 4-5 4M211 729h39m-5-4 5 4-5 4M344 729h51m-5-4 5 4-5 4', '#376175',1)
    p+=txt('ILLUSTRATED AGENT STORY / REAL ACTIVITY SIGNALS',49,767,9,MUTED,font='mono',limit=540)

    p+=clipped_panel(28,802,584,160,'#051721','#214b5c',12)
    p+=txt('REAL GITHUB SIGNAL',47,827,11,CYAN,font='mono')
    p+=txt(data.get('contributions',0),46,874,40,WHITE,limit=125)
    p+=txt('CONTRIBUTIONS',47,896,9,MUTED,font='mono')
    p+=txt(str(data.get('year',date.today().year)),47,919,12,WHITE,font='mono')
    p+=calendar(data,198,857,6,2,max_width=395)
    p+=path('M47 932H593',LINE,1)
    p+=txt(f"{data.get('public_repos',0)} REPOS / {data.get('stars',0)} STARS",47,949,10,MUTED,font='mono')
    p+=txt(f"UPDATED {data.get('as_of','')}",591,949,9,MUTED,font='mono',anchor='end')
    p+=txt('xAnyaForger / EXPLORE. REMEMBER. REPLAY.',320,982,10,MUTED,font='mono',anchor='middle')
    return canvas(w,h,'Neural Arcade — mobile circuit facility',
                  'A portrait-native 2D circuit facility. A tiny illustrative agent tests a blocked shortcut, backtracks, remembers a route, unlocks a portal and replays the successful path. Calendar cells, counters and cache lights use real GitHub contribution data. The story does not claim real agent training or performance.',p,defs())


def defs():
    return ('<pattern id="arc-grid" width="24" height="24" patternUnits="userSpaceOnUse">'
            '<path d="M24 0H0V24" fill="none" stroke="#11303d" stroke-width=".5"/>'
            '<circle cx="0" cy="0" r=".8" fill="#275062"/></pattern>'
            '<filter id="arc-glow" x="-50%" y="-50%" width="200%" height="200%">'
            '<feGaussianBlur stdDeviation="3"/></filter>')


def render(data, mobile=False, animated=True):
    """Return one self-contained SVG; static output contains no animation nodes."""
    return globals()['mobile' if mobile else 'desktop'](data,animated)


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'assets'/'analytics-data.json').read_text(encoding='utf-8'))
    for is_mobile, is_animated, name in [
        (False,True,'world-arcade.svg'),(False,False,'world-arcade-still.svg'),
        (True,True,'world-arcade-mobile.svg'),(True,False,'world-arcade-mobile-still.svg')]:
        output=render(data,mobile=is_mobile,animated=is_animated)
        (root/'assets'/name).write_text(output,encoding='utf-8')
        print(name,len(output))
