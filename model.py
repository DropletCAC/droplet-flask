import pandas as pd 

df = pd.read_csv("dataset.csv")
df = df.drop(["STATION", "NAME", "DATE", "PGTM"], axis=1)
print(df)