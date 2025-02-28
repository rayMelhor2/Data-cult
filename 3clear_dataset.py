import pandas as pd

df = pd.read_csv('dataset.csv')
for i in range(len(df['Description'])):
    if df['Description'][i] == 'False' or df['Description'][i] == '' or df['Description'][i] == 'nan' or df['Description'][i] == 'NaN' or type(df['Description'][i]) == float:
        df = df.drop(i)
df = df.reset_index(drop=True)
df.to_csv('dataset2.csv')