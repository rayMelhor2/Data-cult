import pandas as pd

df1 = pd.read_csv('dataset2.csv')
df2 = pd.read_csv('output.csv')

merged_df = pd.merge(df1, df2, on='Url', how='left')

merged_df.to_csv('dataset2.csv')

