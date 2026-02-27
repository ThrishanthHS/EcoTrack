import pandas as pd
import ast

# ==============================
# STEP 1: Load Dataset
# ==============================
df = pd.read_csv("data_Carbon Emission.csv")

print("Initial Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

# ==============================
# STEP 2: Clean Column Names
# ==============================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\nCleaned column names:")
print(df.columns)

# ==============================
# STEP 3: Handle Missing Values
# ==============================
print("\nMissing values before handling:")
print(df.isnull().sum())

# Vehicle type may be missing for public transport / walking
df["vehicle_type"] = df["vehicle_type"].fillna("none")

print("\nMissing values after handling:")
print(df.isnull().sum())

# ==============================
# STEP 4: Convert List-like Columns
# ==============================
def parse_list(value):
    try:
        return ast.literal_eval(value)
    except:
        return []

df["recycling"] = df["recycling"].apply(parse_list)
df["cooking_with"] = df["cooking_with"].apply(parse_list)

print("\nParsed list columns:")
print(df[["recycling", "cooking_with"]].head())

# ==============================
# STEP 5: Feature Engineering
# ==============================

# Recycling features
recycle_types = ["metal", "plastic", "glass", "paper"]

for r in recycle_types:
    df[f"recycle_{r}"] = df["recycling"].apply(
        lambda x: 1 if r.capitalize() in x else 0
    )

# Cooking features
cooking_types = ["stove", "oven", "microwave", "grill", "airfryer"]

for c in cooking_types:
    df[f"cook_{c}"] = df["cooking_with"].apply(
        lambda x: 1 if c.capitalize() in x else 0
    )

# Drop original list columns
df.drop(columns=["recycling", "cooking_with"], inplace=True)

# ==============================
# STEP 6: Separate Features & Target
# ==============================
X = df.drop("carbonemission", axis=1)
y = df["carbonemission"]

print("\nFinal feature shape:", X.shape)
print("Target shape:", y.shape)

# ==============================
# STEP 7: Save Cleaned Dataset
# ==============================
df.to_csv("data_prep.csv", index=False)

print("\n Cleaned data.csv")
print(" Data preparation completed successfully!")
