import logging
import os

from dotenv import load_dotenv
from transform_xml_to_json import transform_xml_to_json
from upload_files_to_s3 import upload_json_files_to_s3
from download_files_from_sftp import download_today_files
from utils import setup_logging

# Load configuration from environment variables
load_dotenv()

DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")


def main_workflow():
    # Setup logging
    setup_logging()

    try:
        # Step 1: Download today's files from the SFTP server
        logging.info("Starting the process: Step 1 - Download files from SFTP server")
        download_today_files()

        # Step 2: Locate and transform the downloaded XML files into JSON
        logging.info("Starting the process: Step 2 - Transform XML files to JSON")
        for file_name in os.listdir(DOWNLOAD_PATH):
            if file_name.endswith(".xml"):
                xml_file_path = os.path.join(DOWNLOAD_PATH, file_name)
                logging.info(f"Processing file: {xml_file_path}")
                transform_xml_to_json(xml_file_path)

        # Step 3: Upload the generated JSON files to S3
        logging.info("Starting the process: Step 3 - Upload JSON files to S3")
        upload_json_files_to_s3()

        logging.info("Process completed successfully!")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise  # Reraise the exception if necessary for higher-level handling


if __name__ == "__main__":
    main_workflow()
