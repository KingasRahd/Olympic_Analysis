import pandas as pd

def process(df,noc):
    df=pd.merge(df,noc,on='NOC',how='left')
    df=df[df['Season']=='Summer']
    df.drop_duplicates(inplace=True)

    medals=pd.get_dummies(df['Medal']).replace({True:1,False:0})
    df=pd.concat([df,medals],axis=1)
    df.reset_index(inplace=True,drop=True)
    return df
