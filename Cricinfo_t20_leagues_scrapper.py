'''
A look at number of close matches in IPL, BBL and PSL in all seasons.
'''

import urllib
from bs4 import BeautifulSoup
import ssl
import pandas as pd
from collections import OrderedDict
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

main_url = 'http://www.espncricinfo.com/scores/series/%d/season/%d/%s'

def extract_tournament_stats(seasons,id_,tournament):
    
    main_url = 'http://www.espncricinfo.com/scores/series/%d/season/%d/%s'
    data_list = []
    for season in range(seasons[0],seasons[1]):
            
        url =main_url%(id_,season,tournament)
        html  = urllib.request.urlopen(url, context = ctx).read()
        bs = BeautifulSoup(html,'lxml')
        a_container=bs.find_all('div',{'class' :'cscore_link cscore_link--button'})
        temp_data=OrderedDict()
                
        for idx,matches in enumerate(a_container):
            temp_data=OrderedDict()
            temp_data['season']= season
            home = a_container[idx].find('li', {'class':'cscore_item cscore_item--home'})
            temp_data['team1'] = home.find('span', {'class':'cscore_name cscore_name--long'}).text
            temp_data['score1'] = home.find('div', {'class':'cscore_score'}).text
            away = a_container[idx].find('li', {'class':'cscore_item cscore_item--away'})
            temp_data['team2'] = away.find('span', {'class':'cscore_name cscore_name--long'}).text
            temp_data['score2'] = away.find('div', {'class':'cscore_score'}).text
            temp_data['result'] = a_container[idx].find('span', {'class':'cscore_notes_game'}).text 
            data_list.append(temp_data)
    
        print('Tournament %s : Season %d appended'%(tournament,season))
    
    df=pd.DataFrame(data_list)

    return df


def close_win(x,wicket,balls,runs):
    if ('tied' in x[3].lower()):
        return 1
    elif (x[1]=='wicket' or x[1]=='wickets'):
        return int(x[0]<=wicket or x[2]<=balls)
    elif (x[1]=='runs' or x[1]=='run'):
        return int(x[0]<=runs)
    else:
        return 0


ipl_df = extract_tournament_stats(seasons = (2008,2019),id_ = 8048,tournament = 'ipl')
ipl_df['NoResult'] = ipl_df['result'].apply(lambda x:0 if len(re.findall('\d+',x)) >0 or 'tied' in x  else 1)
ipl_df = ipl_df[ipl_df['NoResult']==0]
ipl_df['Win Margin'] = ipl_df['result'].apply(lambda x:int(re.findall('\d+',x)[0]) if len(re.findall('\d+',x)) > 0 else 0)
ipl_df['Wickets_Runs'] = ipl_df['result'].apply(lambda x:(re.findall(r"(runs|wickets|wicket|run)",x))[0] if len(re.findall(r"(runs|wickets|wicket|run)",x))>0 else None)
ipl_df['DL Applied'] = ipl_df['result'].apply(lambda x: 1 if len(re.findall(r"(DL|D/L)",x))>0 else 0)
ipl_df['Balls_Left'] = ipl_df['result'].apply(lambda x:int(re.findall('\d+',x)[1]) if len(re.findall('\d+',x))==2 else None)

ipl_df['Close'] = ipl_df[['Win Margin','Wickets_Runs','Balls_Left','result']].apply(lambda x : 
    close_win(x,wicket = 2,balls = 6,runs = 10),axis = 1)
ipl= ipl_df.groupby('season')['Close'].mean()
ipl = pd.DataFrame(data = {'season':ipl.index,
                           'ipl_close':ipl.values * 100})

bbl_df = extract_tournament_stats(seasons = (2012,2019),id_ = 8044,tournament = 'big-bash-league')

bbl_df['NoResult'] = bbl_df['result'].apply(lambda x:0 if len(re.findall('\d+',x)) >0 or 'tied' in x  else 1)
bbl_df = bbl_df[bbl_df['NoResult']==0]
bbl_df['Win Margin'] = bbl_df['result'].apply(lambda x:int(re.findall('\d+',x)[0]) if len(re.findall('\d+',x)) > 0 else 0)
bbl_df['Wickets_Runs'] = bbl_df['result'].apply(lambda x:(re.findall(r"(runs|wickets|wicket|run)",x))[0] if len(re.findall(r"(runs|wickets|wicket|run)",x))>0 else None)
bbl_df['DL Applied'] = bbl_df['result'].apply(lambda x: 1 if len(re.findall(r"(DL|D/L)",x))>0 else 0)
bbl_df['Balls_Left'] = bbl_df['result'].apply(lambda x:int(re.findall('\d+',x)[1]) if len(re.findall('\d+',x))==2 else None)

bbl_df['Close'] = bbl_df[['Win Margin','Wickets_Runs','Balls_Left','result']].apply(lambda x : 
    close_win(x,wicket = 2,balls = 3,runs = 5),axis = 1)
bbl = bbl_df.groupby('season')['Close'].mean()
bbl = pd.DataFrame(data = {'season':bbl.index,
                           'bbl_close':bbl.values * 100})
    
ib =ipl.merge(bbl,on='season',how ='left')

cpl_df = extract_tournament_stats(seasons = (2013,2019),id_ = 18816,tournament = 'cpl')

cpl_df['NoResult'] = cpl_df['result'].apply(lambda x:0 if len(re.findall('\d+',x)) >0 or 'tied' in x  else 1)
cpl_df = cpl_df[cpl_df['NoResult']==0]
cpl_df['Win Margin'] = cpl_df['result'].apply(lambda x:int(re.findall('\d+',x)[0]) if len(re.findall('\d+',x)) > 0 else 0)
cpl_df['Wickets_Runs'] = cpl_df['result'].apply(lambda x:(re.findall(r"(runs|wickets|wicket|run)",x))[0] if len(re.findall(r"(runs|wickets|wicket|run)",x))>0 else None)
cpl_df['DL Applied'] = cpl_df['result'].apply(lambda x: 1 if len(re.findall(r"(DL|D/L)",x))>0 else 0)
cpl_df['Balls_Left'] = cpl_df['result'].apply(lambda x:int(re.findall('\d+',x)[1]) if len(re.findall('\d+',x))==2 else None)

cpl_df['Close'] = cpl_df[['Win Margin','Wickets_Runs','Balls_Left','result']].apply(lambda x : 
    close_win(x,wicket = 2,balls = 3,runs = 5),axis = 1)
cpl = cpl_df.groupby('season')['Close'].mean()
cpl = pd.DataFrame(data = {'season':cpl.index,
                           'cpl_close':cpl.values * 100})

ibc =ib.merge(cpl,on='season',how ='left')
    
    
psl_df = extract_tournament_stats(seasons = (2016,2019),id_ = 18898,tournament = 'psl')

psl_df['NoResult'] = psl_df['result'].apply(lambda x:0 if len(re.findall('\d+',x)) >0 or 'tied' in x  else 1)
psl_df = psl_df[psl_df['NoResult']==0]
psl_df['Win Margin'] = psl_df['result'].apply(lambda x:int(re.findall('\d+',x)[0]) if len(re.findall('\d+',x)) > 0 else 0)
psl_df['Wickets_Runs'] = psl_df['result'].apply(lambda x:(re.findall(r"(runs|wickets|wicket|run)",x))[0] if len(re.findall(r"(runs|wickets|wicket|run)",x))>0 else None)
psl_df['DL Applied'] = psl_df['result'].apply(lambda x: 1 if len(re.findall(r"(DL|D/L)",x))>0 else 0)
psl_df['Balls_Left'] = psl_df['result'].apply(lambda x:int(re.findall('\d+',x)[1]) if len(re.findall('\d+',x))==2 else None)

psl_df['Close'] = psl_df[['Win Margin','Wickets_Runs','Balls_Left','result']].apply(lambda x : 
    close_win(x,wicket = 2,balls = 3,runs = 5),axis = 1)
psl = psl_df.groupby('season')['Close'].mean()
psl = pd.DataFrame(data = {'season':psl.index,
                           'psl_close':psl.values * 100})
    
ibcp =ibc.merge(psl,on='season',how ='left')
    
