# steam_reviews_loader.py
import pandas as pd
import ast
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import json
import gzip

def read_json_file(file_path):
    data = []
    try:
        with gzip.open(file_path, 'rt', encoding='ISO-8859–1') as file:
            for line in file:
                data.append(ast.literal_eval(line))
    except Exception as e:

        # Fallback to regular file reading if not gzipped
        with open(file_path, 'r', encoding='ISO-8859–1') as file:
            for line in file:
                data.append(ast.literal_eval(line))
    return pd.DataFrame(data).fillna('None').astype(str)


def save_to_json(df, output_path, max_file_size_mb=200):
    try:
        # Convert DataFrame to list of dictionaries (one dictionary per row)
        data_list = df.to_dict(orient='records')
        
        # Estimate the size of each record by calculating the memory usage of the first row
        avg_record_size = len(json.dumps(data_list[0], ensure_ascii=False))  # Get size of first record
        bytes_per_mb = 1024 * 1024
        
        # Initialize variables for file handling
        file_count = 1
        current_file_size = 0
        output_file = f"{output_path}_part{file_count}.json"
        
        # Open the first output file
        f = open(output_file, 'w', encoding='utf-8')
        
        # Write the data to the files based on size
        for record in data_list:
            # Write each record to the current file
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")
            
            # Update current file size
            current_file_size += len(json.dumps(record, ensure_ascii=False)) + 1  # +1 for the newline
            
            # If the current file exceeds the desired size, close it and open a new one
            if current_file_size >= max_file_size_mb * bytes_per_mb:
                f.close()
                file_count += 1
                output_file = f"{output_path}_part{file_count}.json"
                f = open(output_file, 'w', encoding='utf-8')
                current_file_size = 0  # Reset file size for the new file
                
                # Print only when a new file is created
                print(f"New file created: {output_file}")
        
        # Close the last file
        f.close()
        print(f"Successfully saved all records.")

        return True
        
    except PermissionError:
        print(f"Permission denied: {output_path}")
    except OSError as e:
        print(f"OS error occurred: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        
    return False


if __name__ == "__main__":
    # This will run when file is executed directly
    # file_path = 'data/raw/steam_games_metadata/australian_user_reviews.json'
    # file_path = 'data/raw/steam_games_metadata/steam_games_item_metadata.json'
    # df = read_json_file(file_path)
    
    

    
    # file_path = 'data/raw/bundle_data/bundle_data.json'
    # df = read_json_file(file_path)
    # write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "BUNDLE_DATA")

    file_path = 'data/raw/steam_reviews/steam_new.json'
    df = read_json_file(file_path)
    # write_to_snowflake(df, "STEAM_FULL", "RAW_DATA", "REVIEWS_DATA")
    print(df.shape)
    # save_to_csv(df, 'containers/thisistheone.csv')
    # Saving as JSON
    save_to_json(df, 'containers/reviews.json')
