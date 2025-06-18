import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import preprocess,helper

df=pd.read_csv('athlete_events.csv')
noc=pd.read_csv('noc_regions.csv')

df=preprocess.process(df,noc)

st.sidebar.title('Olympic Analysis')

st.sidebar.image('https://imgs.search.brave.com/uia20pAAs02j7sHXRUg5IMFwCWItlGIU-s3jbAIoLOM/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zdGF0/aWMudmVjdGVlenku/Y29tL3N5c3RlbS9y/ZXNvdXJjZXMvdGh1/bWJuYWlscy8wNDYv/ODE4LzIzMC9zbWFs/bC9vbHltcGljLWxv/Z28tc3RhdHVlLWJh/Y2tncm91bmQtc3Vu/c2V0LXN1bnJpc2Ut/c2t5LWJlYXV0aWZ1/bC1oaWxscy1zaWxo/b3VldHRlLXNwb3J0/cy1mYW5zLWNvdW50/cnktY29tcGV0aXRp/b24tZnJlZS12ZWN0/b3IuanBn')

ch=st.sidebar.radio('Select an option',['Introduction','Medal Tally','Overall Analysis','Country-wise Analysis','Athlete-wise Analysis'])

if ch=='Introduction':

    st.title('🥇 Olympic Data Analysis')
    st.header('Welcome to the ultimate deep dive into Olympic history and performance.')
    st.subheader('This interactive dashboard allows you to explore:')
    st.subheader('🏅 Medal trends across countries, sports, and years')
    st.subheader('👥 Athlete demographics: height, weight, gender distribution')
    st.subheader('🌍 Nation-wise performance: how countries rise and fall in dominance')
    st.subheader('🎯 Sport-specific insights: which disciplines bring the most glory?')
    st.subheader('Whether you\'re a data enthusiast, a sports buff, or just curious about how nations perform on the world’s biggest stage, this app offers a dynamic and visual journey through over a century of Olympic legacy.')

elif ch=='Medal Tally':
    st.sidebar.header('Medal Tally')
    st.title('Medal Tally')
    years,countries=helper.years_and_countries(df)

    year=st.sidebar.selectbox('Select Year',years)
    country=st.sidebar.selectbox('Select Country',countries)


    medals=helper.fetch_medal_tally(year,country,df,noc)
    st.table(medals)

elif ch=='Overall Analysis':
    editions=df['Year'].unique().shape[0]-1
    countries=df['region'].unique().shape[0]
    hosts=df['City'].unique().shape[0]
    sports=df['Sport'].unique().shape[0]
    events=df['Event'].unique().shape[0]
    athletes=df['Name'].unique().shape[0]

    st.title('Top Stats')

    c1,c2,c3=st.columns(3)
    with c1:
        st.header('Edition')
        st.title(editions)
    with c2:
        st.header('Nations')
        st.title(countries)
    with c3:
        st.header('Hosts')
        st.title(hosts)
    
    c1,c2,c3=st.columns(3)
    with c1:
        st.header('Athletes')
        st.title(athletes)
    with c2:
        st.header('Sports')
        st.title(sports)
    with c3:
        st.header('Events')
        st.title(events)
    
    ndf=helper.data_over_time(df,'region')
    ndf.rename(columns={'region':'Region'},inplace=True)
    st.title('\nNations over the Years')
    fig=px.line(ndf,x='Year',y='Region')
    st.plotly_chart(fig)

    ndf=helper.data_over_time(df,'Event')
    st.title('\nEvents over the Years')
    fig=px.line(ndf,x='Year',y='Event')
    st.plotly_chart(fig)

    ndf=helper.data_over_time(df,'Name')
    ndf.rename(columns={'Name':'Athletes'},inplace=True)
    st.title('Athletes over the Years')
    fig=px.line(ndf,x='Year',y='Athletes')
    st.plotly_chart(fig)

    st.title('No. of Events over the Years across different Sports')
    ndf=df.drop_duplicates(['Year','Sport','Event'])
    ndf=ndf.pivot_table(index='Sport',columns='Year',values='Event',aggfunc='count').fillna(0).astype(int)
    fig,ax=plt.subplots(figsize=(20,20))
    ax=sns.heatmap(ndf,annot=True)
    st.pyplot(fig)

    st.title('\nSuccessfull Players of all Time')
    #c1,c3=st.columns(2)
    all_sports=df['Sport'].unique().tolist()
    all_sports.sort()
    all_sports.insert(0,'Overall')
    #with c1:
    sport=st.selectbox('Select Sport',all_sports)
    x=helper.goat(df,sport)
    st.table(x)

elif ch=='Country-wise Analysis':
    
    countries=df['region'].dropna().unique().tolist()
    countries.sort()
    st.sidebar.title('Country-wise Analysis')
    country=st.sidebar.selectbox('Select a Nation',countries)
    cwa=helper.country_wise_analysis(df,country)

    st.title(f'{country}\'s Medals over Time Plot')
    fig=px.line(cwa,x='Year',y='Medals')
    st.plotly_chart(fig)
    st.title(f'{country}\'s Medal Tally over the Years')
    st.table(cwa)

    st.title(f'{country}\'s Performance across Different Sports')
    heat=helper.heatmap_for_sports(df,country)
    mask=heat==-1
    fig,ax=plt.subplots(figsize=(20,20))
    ax=sns.heatmap(heat,annot=True,mask=mask)
    plt.grid(True)
    st.pyplot(fig)

    st.title(f"{country}\'s Top Athletes")
    goat_players=helper.top_players_per_country(df,country)
    st.table(goat_players)
    
elif ch=='Athlete-wise Analysis':
    fig=helper.age_distribution(df)
    #fig.update_layout(autosize=False,width=1000,height=600)
    st.title('Distribution of Age')
    st.plotly_chart(fig)

    ndf=df.drop_duplicates(subset=['Name','region','Sport'])
    sports=df['Sport'].sort_values().unique()
    x=ndf.groupby('Sport')['Name'].count()>100
    famous=sports[x].tolist()
    famous.insert(0,'Overall')

    st.title("Age Distribution of Gold Medalists wrt Sports")
    sport=st.selectbox('Select Sport',famous)
    fig=helper.age_distribution_wrt_sport(df,sport)
    st.plotly_chart(fig)

    st.title("Athlete Height-Weight Distribution")
    sport=st.selectbox("Select a Sport",famous[1:])
    fig=helper.height_weight(df,sport)
    st.pyplot(fig)

    st.title('Gender-wise Participation over the Years')
    fig=helper.gender_participation(df)
    st.plotly_chart(fig)

    