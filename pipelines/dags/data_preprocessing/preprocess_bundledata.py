import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
from load_data_from_snowflake import read_from_snowflake

  # Import the function to fetch data

# Load BUNDLE_DATA table from Snowflake
df = read_from_snowflake(
    database="STEAM_FULL",
    schema="RAW_DATA",
    table_name="BUNDLE_DATA"
)

if df is None or df.empty:
    print("No data loaded from Snowflake. Exiting script.")
    exit()

# ----------------- Data Preprocessing -----------------
print("\n📌 Initial Data Info:")
print(df.info())

# 1️⃣ Remove duplicate rows
#df.drop_duplicates(inplace=True)

# 2️⃣ Handle missing values
missing_values = df.isnull().sum()
print("\n🔍 Missing Values Before Cleaning:")
print(missing_values)



print("\n📌 Fixing Data Types...")

# 1️⃣ Convert `bundle_final_price` & `bundle_price` to float
df["bundle_final_price"] = df["bundle_final_price"].replace('[\$,]', '', regex=True).astype(float)
df["bundle_price"] = df["bundle_price"].replace('[\$,]', '', regex=True).astype(float)

# Convert `bundle_discount` to float (some values are decimals)
df["bundle_discount"] = df["bundle_discount"].str.replace('%', '').astype(float)

# If you want it as an integer (rounded):
df["bundle_discount"] = df["bundle_discount"].round().astype(int)


# 3️⃣ Convert `bundle_id` to integer
df["bundle_id"] = df["bundle_id"].astype(int)

# 4️⃣ Convert `items` column (currently a JSON-like string) into a list of dictionaries
df["items"] = df["items"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# ----------------- Verify Fixed Data -----------------
print("\n✅ Data Types After Fixing:")
print(df.dtypes)
df.columns = df.columns.str.lower().str.replace(" ", "_")

print(df.describe())

# 4️⃣ Add new features (Feature Engineering)
if "release_date" in df.columns:
   df["release_year"] = pd.to_datetime(df["release_date"], errors='coerce').dt.year
   
#Extract total number of items in each bundle

df["total_items"] = df["items"].apply(lambda x: len(x) if isinstance(x, list) else 0)

#Extract unique game genres from bundles

df["unique_genres"] = df["items"].apply(lambda x: list(set([item["genre"] for item in x if "genre" in item])) if isinstance(x, list) else [])

#Count unique genres per bundle

df["num_unique_genres"] = df["unique_genres"].apply(len)

#Outliers
#Q1 = df["bundle_final_price"].quantile(0.25)
#Q3 = df["bundle_final_price"].quantile(0.75)
#IQR = Q3 - Q1
#lower_bound = Q1 - 1.5 * IQR
#upper_bound = Q3 + 1.5 * IQR

#df_filtered = df[(df["bundle_final_price"] >= lower_bound) & (df["bundle_final_price"] <= upper_bound)]

print(df)


# Identify Most Common Genres

from collections import Counter

all_genres = [genre for sublist in df["unique_genres"] for genre in sublist]
genre_counts = pd.DataFrame(Counter(all_genres).most_common(), columns=["Genre", "Count"])

plt.figure(figsize=(10,5))
sns.barplot(x=genre_counts["Genre"][:10], y=genre_counts["Count"][:10])
plt.xticks(rotation=45)
plt.xlabel("Genre")
plt.ylabel("Number of Bundles")
plt.title("Top 10 Most Common Game Genres in Bundles")
plt.show()

#Visualize Price Distribution

plt.figure(figsize=(8,5))
sns.histplot(df["bundle_final_price"], bins=30, kde=True)
plt.xlabel("Final Bundle Price ($)")
plt.ylabel("Frequency")
plt.title("Distribution of Bundle Prices")
plt.show()

