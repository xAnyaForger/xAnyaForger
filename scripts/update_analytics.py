"""Refresh Neural Arcade and genuine GitHub analytics. Stdlib only."""
from pathlib import Path
from datetime import date,timedelta
import argparse,json,os,urllib.request
from calendar_data import parse_calendar
from telemetry import languages
from stats_layouts import activity,streaks
from neural_arcade import render as arcade
from row_layouts import top_row,streak_row,activity_card,languages_card

ROOT=Path(__file__).resolve().parents[1]

def get_json(url):
    headers={'User-Agent':'Derol-Chong-Profile-Analytics','Accept':'application/vnd.github+json'}
    token=os.getenv('GITHUB_TOKEN')
    if token: headers['Authorization']='Bearer '+token
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response: return json.load(response)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--html',type=Path); parser.add_argument('--metadata',type=Path); parser.add_argument('--as-of'); parser.add_argument('--username',default='xAnyaForger'); args=parser.parse_args()
    as_of=date.fromisoformat(args.as_of) if args.as_of else date.today()
    if args.html: html=args.html.read_text(encoding='utf-8')
    else:
        url=f'https://github.com/users/{args.username}/contributions?from={as_of.year}-01-01&to={as_of.year}-12-31'
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Derol-Chong-Analytics'}),timeout=30) as response: html=response.read().decode()
    days=parse_calendar(html,as_of)
    if args.metadata: metadata=json.loads(args.metadata.read_text(encoding='utf-8-sig'))
    else:
        repos=[]; page=1
        while True:
            chunk=get_json(f'https://api.github.com/users/{args.username}/repos?per_page=100&page={page}')
            repos+=chunk
            if len(chunk)<100: break
            page+=1
        langs={}
        for repo in repos:
            if repo.get('fork') or repo.get('private'): continue
            for lang,count in get_json(repo['languages_url']).items(): langs[lang]=langs.get(lang,0)+count
        metadata={'repositories':repos,'languages':langs}
    public=[repo for repo in metadata['repositories'] if not repo.get('private')]
    lookup={d['date']:d['count'] for d in days}; total=sum(lookup.values()); longest=run=0; start=None; longest_start=longest_end=None
    for day in days:
        if day['count']:
            if run==0: start=day['date']
            run+=1
            if run>longest: longest=run; longest_start=start; longest_end=day['date']
        else: run=0
    latest=as_of if lookup.get(as_of.isoformat()) else as_of-timedelta(days=1)
    cursor=latest; current=0
    while lookup.get(cursor.isoformat(),0)>0: current+=1; cursor-=timedelta(days=1)
    def span(a,b): return date.fromisoformat(a).strftime('%b %d')+' - '+date.fromisoformat(b).strftime('%b %d') if a else 'No active streak yet'
    data={'username':args.username,'as_of':as_of.isoformat(),'year':as_of.year,'public_repos':len(public),'stars':sum(repo['stargazers_count'] for repo in public),'languages':metadata['languages'],'days':days,'contributions':total,'active_days':sum(d['count']>0 for d in days),'current_streak':current,'longest_streak':longest,'current_range':span((cursor+timedelta(days=1)).isoformat(),latest.isoformat()) if current else 'No active streak today','longest_range':span(longest_start,longest_end)}
    assets=ROOT/'assets'; assets.mkdir(exist_ok=True)
    for mobile in [False,True]:
        suffix='-mobile' if mobile else ''
        for animated in [False,True]:
            motion='' if animated else '-still'
            for label,renderer in [('activity',activity),('languages',languages),('streak',streaks),('top-row',top_row),('streak-centered',streak_row)]:
                (assets/('analytics-'+label+suffix+motion+'.svg')).write_text(renderer(data,mobile,animated),encoding='utf-8')
            for label,renderer in [('arcade',arcade)]:
                (assets/('world-'+label+suffix+motion+'.svg')).write_text(renderer(data,mobile,animated),encoding='utf-8')
            if not mobile:
                for label,renderer in [('activity-card',activity_card),('languages-card',languages_card)]:
                    (assets/('analytics-'+label+motion+'.svg')).write_text(renderer(data,animated),encoding='utf-8')
    (assets/'analytics-data.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(f'Analytics: {len(public)} public repos, {data["stars"]} stars, {total} year contributions; streak {current}/{longest}.')

if __name__=='__main__': main()
