import os
import shutil

def clean_up_files_in_folder(folder_path):
    """
    Removes all files and subdirectories within the specified folder.

    :param folder_path: Path to the folder to be cleaned.
    """
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        return
    
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete file
                print(f"Deleted file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete subdirectory
                print(f"Cleaned up Staging directory: {file_path}")

    except Exception as e:
        print(f"Error while cleaning up files: {e}")

# Example usage
if __name__ == "__main__":
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the data file (assuming it's at root/data/processed)
    folder_to_clean = os.path.join(script_dir, '..', '..', 'data', 'processed')
    
    clean_up_files_in_folder(folder_to_clean)