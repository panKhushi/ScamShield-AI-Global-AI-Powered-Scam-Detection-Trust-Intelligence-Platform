import pandas as pd

csv_path = "app/ml/data/phishing.csv"
df = pd.read_csv(csv_path)

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nLabel/class/result value counts:")
for col in df.columns:
    if "label" in col.lower() or "class" in col.lower() or "result" in col.lower():
        print(f"\n{col}:")
        print(df[col].value_counts())