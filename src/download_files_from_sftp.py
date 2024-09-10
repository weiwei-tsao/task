"""
Workflow
- create the SFTP server connection and
- retrieve all the files and
- determine if the file has been modified in today and
- copy them to local folder and delete in the server
"""

import logging
import paramiko
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os

from utils import setup_logging

# Load configuration from environment variables
load_dotenv()

SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_USER = os.getenv("SFTP_USER")
SFTP_PASSWORD = os.getenv("SFTP_PASSWORD")
SFTP_PATH = os.getenv("SFTP_PATH")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")

# Ensure the local download directory exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Setup logging
setup_logging()


# Create sftp connection
def create_sftp_connection():
    try:
        transport = paramiko.Transport((SFTP_HOST, 22))  # Port 22 is default for SFTP
        transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        logging.info("SFTP connection established.")
        return sftp
    except Exception as e:
        logging.error(f"Failed to connect to SFTP: {e}")
        return None


# Retrieve files from the sftp server in the pathname
def get_files_from_sftp(sftp, pathname):
    try:
        file_list = sftp.listdir_attr(pathname)  # Retrieve files with attributes
        logging.info(f"Files retrieved from SFTP server {pathname}.")
        return file_list
    except Exception as e:
        logging.error(f"Failed to list files: {e}")
        return []


# Check if a file is modified today
def is_modified_today(file_attr):
    last_modified_time = file_attr.st_mtime
    file_date = datetime.fromtimestamp(last_modified_time).date()
    today_date = datetime.now().date()

    logging.info(f"File date: {file_date}, Today date: {today_date}")

    return file_date == today_date


# Download and delete the files from the SFTP server
def download_and_delete_file(sftp, file_attr):
    try:
        file_path = os.path.join(SFTP_PATH, file_attr.filename)
        local_file_path = os.path.join(DOWNLOAD_PATH, file_attr.filename)

        # Download the file using streaming for large files
        with open(local_file_path, "wb") as local_file:
            sftp.getfo(file_path, local_file)  # Stream the file content

        logging.info(f"File {file_attr.filename} downloaded to {local_file_path}.")

        # Delete the file from the SFTP server after downloading
        sftp.remove(file_path)
        logging.info(f"File {file_attr.filename} deleted from SFTP server.")
    except Exception as e:
        logging.error(f"Error downloading or deleting file: {e}")


# Main function to execute the process of Step 1
def download_today_files():

    # create the connection
    sftp = create_sftp_connection()

    if not sftp:
        return

    # get all the files on the server
    file_list = get_files_from_sftp(sftp, SFTP_PATH)

    # identify files modified today
    today_files = [file_attr for file_attr in file_list if is_modified_today(file_attr)]

    if not today_files:
        logging.info("No file found for today.")
    else:
        # Download files in parallel using threads
        with ThreadPoolExecutor(max_workers=4) as executor:
            for file_attr in today_files:
                executor.submit(download_and_delete_file, sftp, file_attr)

    sftp.close()  # Close the SFTP connection after the task is done
    logging.info("SFTP connection closed.")


if __name__ == "__main__":
    download_today_files()
