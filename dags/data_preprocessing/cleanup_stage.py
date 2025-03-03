import os
import shutil
from custom_logging import get_logger

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = get_logger('Data_Cleaning')

# Set up project directories
RAW_DATA_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

def clean_up_files_in_folder():
    """
    Removes all files and subdirectories within the specified folder.

    :param folder_path: Path to the folder to be cleaned.
    """
    folder_path = PROCESSED_DATA_DIR
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist.")
        logger.info(f"Folder '{folder_path}' does not exist.")
        return
    
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete file
                print(f"Deleted file: {file_path}")
                logger.info(f"Deleted file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete subdirectory
                logger.info(f"Cleaned up Staging directory: {file_path}")


    except Exception as e:
        logger.info(f"Error while cleaning up files: {e}")

# Example usage
if __name__ == "__main__":
    
    clean_up_files_in_folder()