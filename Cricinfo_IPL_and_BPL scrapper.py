import urllib
from bs4 import BeautifulSoup
import ssl
import pandas as pd
from collections import OrderedDict

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

main_url = 'http://www.espncricinfo.com/scores/series/%d/season/%d/%s'

def extract_tournament_stats(seasons,id_,tournament):
    
    main_url = 'http://www.espncricinfo.com/scores/series/%d/season/%d/%s'
    data_list = []
    for season in range(seasons[0],seasons[1]):
            
        url =main_url%(id_,seasons[0],tournament)
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

ipl_df = extract_tournament_stats(seasons = (2018,2019),id_ = 8048,tournament = 'ipl')
bbl_df = extract_tournament_stats(seasons = (2012,2019),id_ = 8044,tournament = 'big-bash-league')
    
'''
# Things to do 

1. Parse scores properly
2. Remove DL matches
3. Team1 should be score of team batted first and not home team
'''

import re

ipl_df['Win Margin'] = ipl_df['result'].apply(lambda x:int(re.findall('\d+',x)[0]))
ipl_df['Wickets_Runs'] = ipl_df['result'].apply(lambda x:(re.findall(r"(runs|wickets|wicket|run)",x))[0] if len(re.findall(r"(runs|wickets|wicket|run)",x))>0 else None)
ipl_df['DL Applied'] = ipl_df['result'].apply(lambda x: 1 if len(re.findall(r"(DL|D/L)",x))>0 else 0)
#ipl_df['Balls'] = ipl_df['result'].apply(lambda x:re.findall('balls|ball',x))
ipl_df['Balls_Left'] = ipl_df['result'].apply(lambda x:int(re.findall('\d+',x)[1]) if len(re.findall('\d+',x))==2 else None)

def close_win(x,wicket,balls,runs):
    if (x[1]=='wicket' or x[1]=='wickets'):
        return int(x[0]<=wicket or x[2]<=balls)
    elif (x[1]=='runs' or x[1]=='run'):
        return int(x[0]<=runs)
    else:
        return 0

ipl_df['Close'] = ipl_df[['Win Margin','Wickets_Runs','Balls_Left']].apply(lambda x : 
    close_win(x,wicket = 2,balls = 6,runs = 10),axis = 1)
ipl_df['season'].groupby(['season'].mean(''))


