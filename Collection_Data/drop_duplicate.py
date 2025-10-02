import pandas as pd

df = pd.read_csv(
    "file_ghep.csv"
)
df_khong_trung = df.drop_duplicates()

df_khong_trung.to_csv("file_khong_trung.csv", index=False)
