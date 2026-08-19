import pandas as pd

df = pd.read_csv("app/ml/data/phising_email1.csv")
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 3 rows:")
print(df.head(3))
print("\nLabel distribution:")
for col in df.columns:
    if "label" in col.lower() or "class" in col.lower() or "spam" in col.lower() or "type" in col.lower():
        print(df[col].value_counts())