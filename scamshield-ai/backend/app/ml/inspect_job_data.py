import pandas as pd

df = pd.read_csv("app/ml/data/job_postings.csv")
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 3 rows:")
print(df.head(3))
print("\nLabel distribution:")
for col in df.columns:
    if "fraud" in col.lower() or "label" in col.lower() or "class" in col.lower():
        print(df[col].value_counts())