import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

def tally(df,noc):
    df.drop_duplicates(subset=['Team','NOC','Games','Year','Season','City','Sport','Event','Medal'],inplace=True)
    medals=df.groupby('NOC')[['Gold','Silver','Bronze']].sum().sort_values(['Gold','Silver','Bronze'],ascending=False).reset_index()

    medals=pd.merge(medals,noc,on='NOC',how='left')
    medals=medals[['region','NOC','Gold','Silver','Bronze']]
    medals.rename(columns={'region':'Region'},inplace=True)

    return medals

def years_and_countries(df):
    years=df['Year'].unique().tolist()
    years.sort()
    years.insert(0,'Overall')

    countries=df['region'].dropna().unique().tolist()
    countries.sort()
    countries.insert(0,'Overall')

    return years,countries

def fetch_medal_tally(year,country,df,noc):
    if year=='Overall' and country=='Overall':
        medals=tally(df,noc)
        medals['Total']=medals['Gold']+medals['Silver']+medals['Bronze']
        return medals
        
    elif year=='Overall' and country!='Overall':
        df.drop_duplicates(subset=['Team','NOC','Games','Year','Season','City','Sport','Event','Medal'],inplace=True)
        medals=df.query('region==@country')
        medals=medals.groupby('Year')[['Gold','Silver','Bronze']].sum().sort_values('Year',ascending=False).reset_index()
        medals.rename(columns={'region':'Region'},inplace=True)
        medals['Total']=medals['Gold']+medals['Silver']+medals['Bronze']
        return medals
        #medals=medals[['region','NOC','Year','Event','Gold','Silver','Bronze']]
        #medals.rename(columns={'region':'Region'},inplace=True)

    elif year!='Overall' and country=='Overall':
        df.drop_duplicates(subset=['Team','NOC','Games','Year','Season','City','Sport','Event','Medal'],inplace=True)
        medals=df.query('Year==@year')
        #medals=medals.groupby('NOC')[['Gold','Silver','Bronze']].sum().sort_values(['Gold','Silver','Bronze'],ascending=False).reset_index()
        #medals=pd.merge(medals,noc,on='NOC',how='left')
        #medals=medals[['region','NOC','Gold','Silver','Bronze']]
        #medals.rename(columns={'region':'Region'},inplace=True)

    else:
        df.drop_duplicates(subset=['Team','NOC','Games','Year','Season','City','Sport','Event','Medal'],inplace=True)
        medals=df.query('region==@country and Year==@year')
        #medals=medals[['region','NOC','Year','Event','Gold','Silver','Bronze']]
        #medals.rename(columns={'region':'Region'},inplace=True)
        
    medals=medals.groupby('region')[['Gold','Silver','Bronze']].sum().sort_values(['Gold','Silver','Bronze'],ascending=False).reset_index()
    medals.rename(columns={'region':'Region'},inplace=True)
    medals['Total']=medals['Gold']+medals['Silver']+medals['Bronze']
    return medals

def data_over_time(df,data):
    ndf=df.groupby('Year')[data].nunique().reset_index()
    return ndf

def goat(df,sport):
    df=df.dropna(subset=['Medal'])
    if sport=='Overall':
        x=df.groupby('Name')['Medal'].count().sort_values(ascending=False).reset_index()
        x=pd.merge(x,df[['Name','Sport','region']].drop_duplicates(),on='Name',how='left')
    else:
        df=df.query('Sport==@sport')
        x=df.groupby('Name')['Medal'].count().sort_values(ascending=False).reset_index()
        x=pd.merge(x,df[['Name','Sport','region']].drop_duplicates(),on='Name',how='left')

    x.rename(columns={'region':'Region'},inplace=True)
    return x.head(10)

def country_wise_analysis(df,country):
    ndf=df.drop_duplicates(subset=['Team','NOC','Games','Year','Season','City','Sport','Event','Medal'])
    cwa=ndf.pivot_table(index='region',columns='Year',values='Medal',aggfunc='count').fillna(0).astype(int)
    req=cwa.loc[country].reset_index()
    req.rename(columns={f'{country}':'Medals'},inplace=True)
    return req

def heatmap_for_sports(df,country):
    sports=df['Sport'].unique().tolist()
    sports.sort()
    df=df.query('region==@country')
    x=df.pivot_table(index='Sport',columns='Year',values='Medal',aggfunc='count').fillna(0).astype(int)
    x=x.reindex(sports,fill_value=-1).astype(int)
    return x

def top_players_per_country(df,country):
    df=df.query('region==@country')
    goat=df.groupby('Name')['Medal'].count().sort_values(ascending=False).reset_index()
    goat=pd.merge(goat,df[['Name','Sport','region']].drop_duplicates(),on='Name',how='left')
    return goat[goat['Medal']!=0].head(10)
    
def age_distribution(df):
    athlete_df=df.sort_values(['Year'])#.drop_duplicates(subset=['Name','region'])
    debut=athlete_df.drop_duplicates(subset=['Name','region'])['Age'].dropna()
    gold=athlete_df.query('Medal=="Gold"')['Age'].dropna()
    silver=athlete_df.query('Medal=="Silver"')['Age'].dropna()
    bronze=athlete_df.query('Medal=="Bronze"')['Age'].dropna()

    fig=ff.create_distplot([bronze,silver,gold,debut],['Bronze Medalist','Silver Medalist','Gold Medalist','Debut'],show_hist=False,show_rug=False)
    return fig

def age_distribution_wrt_sport(df,sport):
    ndf=df.drop_duplicates(subset=['Name','region','Sport'])
    sports=df['Sport'].sort_values().unique()
    x=ndf.groupby('Sport')['Name'].count()>100
    famous=sports[x]
    d={}
    for i in famous:
        sp=df.query('Sport==@i and Medal=="Gold"')['Age'].dropna()
        d[i]=sp
    
    if sport=='Overall':
        fig=ff.create_distplot(list(d.values()),list(famous),show_hist=False,show_rug=False)
        return fig
    else:
        fig=ff.create_distplot([d[sport]],[sport],show_hist=False,show_rug=False)
        return fig
    
def height_weight(df,sport):
    ndf=df.copy()
    ndf['Medal'].fillna('No Medal',inplace=True)
    ndf.dropna(subset=['Height','Weight'],inplace=True)

    hw=ndf.query('Sport==@sport')
    fig,ax=plt.subplots()
    ax=sns.scatterplot(x=hw['Weight'],y=hw['Height'],hue=hw['Medal'],style=hw['Sex'],s=10)
    return fig

def gender_participation(df):
    part=df.pivot_table(index='Sex',columns='Year',values='Name',aggfunc='count')
    part.fillna(0,inplace=True)
    part=part.astype(int)
    upd_part=pd.DataFrame(np.array(part).T)
    upd_part.rename(columns={0:'Females',1:'Males'},inplace=True)
    upd_part['Years']=part.columns
    fig=px.line(upd_part,x='Years',y=['Males','Females'])
    fig.update_layout(yaxis_title='Partcipation')
    return fig
