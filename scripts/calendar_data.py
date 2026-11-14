from html.parser import HTMLParser
from datetime import date
import re

class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.days={}; self.tips={}; self.tip=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='td' and attrs.get('data-date'):
            self.days[attrs['id']]={'date':attrs['data-date'],'level':int(attrs['data-level'])}
        if tag=='tool-tip': self.tip=attrs.get('for'); self.tips[self.tip]=''
    def handle_data(self,data):
        if self.tip: self.tips[self.tip]+=data
    def handle_endtag(self,tag):
        if tag=='tool-tip': self.tip=None

def parse_calendar(html,as_of):
    parser=CalendarParser(); parser.feed(html); days=[]
    for ident,entry in parser.days.items():
        tip=parser.tips.get(ident,'').strip()
        if tip.startswith('No contributions'): count=0
        else:
            match=re.match(r'([\d,]+) contributions?\b',tip)
            if not match: raise ValueError('Missing contribution count for '+entry['date'])
            count=int(match.group(1).replace(',',''))
        if date.fromisoformat(entry['date']).year==as_of.year and date.fromisoformat(entry['date'])<=as_of:
            days.append({**entry,'count':count})
    days.sort(key=lambda d:d['date'])
    expected=(as_of-date(as_of.year,1,1)).days+1
    if len(days)!=expected: raise ValueError(f'Expected {expected} year-to-date dates; received {len(days)}')
    return days
