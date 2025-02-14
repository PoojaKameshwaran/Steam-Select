import ast
import snowflake.connector

# Snowflake connection details
SNOWFLAKE_ACCOUNT = "el02762"
SNOWFLAKE_USER = "SruthiGandla"
SNOWFLAKE_PASSWORD = "Northeastern@0923"
SNOWFLAKE_DATABASE = "STEAM_FULL"
SNOWFLAKE_SCHEMA = "RAW_DATA"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_TABLE = "AUS_USER_REVIEWS"

# Function to parse the custom dictionary format
def parse_reviews(file_path):
    records = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:  # Ensure line is not empty
                try:
                    record = ast.literal_eval(line)  # Convert string to dictionary
                    records.append(record)
                except Exception as e:
                    print(f"Error parsing line: {line}\nError: {e}")
    return records

# Function to insert data into Snowflake
def load_to_snowflake(records):
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {SNOWFLAKE_TABLE} (
            user_id STRING,
            user_url STRING,
            item_id STRING,
            posted STRING,
            last_edited STRING,
            helpful STRING,
            recommend BOOLEAN,
            review STRING
        )
    """)
    
    # Insert records
    for record in records:
        user_id = record.get("user_id", "")
        user_url = record.get("user_url", "")
        for review in record.get("reviews", []):
            cursor.execute(f"""
                INSERT INTO {SNOWFLAKE_TABLE} (user_id, user_url, item_id, posted, last_edited, helpful, recommend, review)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                user_url,
                review.get("item_id", ""),
                review.get("posted", ""),
                review.get("last_edited", ""),
                review.get("helpful", ""),
                review.get("recommend", False),
                review.get("review", "")
            ))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Data successfully loaded into Snowflake.")

# Main execution
if __name__ == "__main__":
    file_path = r"C:\Users\pooja\Desktop\NEU\Spring '25\IE 7374\aus_user_reviews.json"
    records = parse_reviews(file_path)
    if records:
        load_to_snowflake(records)
    else:
        print("No valid records found in the file.")