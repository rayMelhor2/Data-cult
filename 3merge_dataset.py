import pandas as pd
df1 = pd.read_csv("dataset.csv")
df2 = pd.read_csv("output.csv")
result_df = pd.merge(df1, df2[['Url', 'photo']], on='Url', how='left')
result_df = result_df.drop_duplicates(subset='Url', keep='first')
result_df.to_csv("dataset.csv", index=False)
print(result_df.head())
