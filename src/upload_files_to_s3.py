from datetime import datetime
import boto3
import os
import logging
from dotenv import load_dotenv

from utils import setup_logging

# Load configuration from environment variables
load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PATH = os.getenv("S3_PATH")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


# Setup logging
setup_logging()


# Function to upload a file to S3
def upload_to_s3(file_name, s3_bucket, s3_path):
    try:
        # Create an S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

        # Construct the full S3 key (S3 path + file name)
        s3_key = os.path.join(s3_path, os.path.basename(file_name))

        # Upload the file
        s3_client.upload_file(file_name, s3_bucket, s3_key)
        logging.info(f"Successfully uploaded {file_name} to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        logging.error(f"Error uploading {file_name} to S3: {e}")


# Main function to upload both JSON files
def upload_json_files_to_s3():
    # Get today's file folder (e.g., "2020-01-01")
    today = datetime.now().strftime("%Y-%m-%d")
    directory = os.path.join("json", today)

    # List of files to upload
    files_to_upload = [
        os.path.join(directory, "above_average_output.json"),
        os.path.join(directory, "below_average_output.json"),
    ]

    # Upload each file to S3
    for file in files_to_upload:
        if os.path.exists(file):
            upload_to_s3(file, S3_BUCKET, S3_PATH)
        else:
            logging.warning(f"File {file} not found. Skipping upload.")


# Call the upload function after transformation is complete
if __name__ == "__main__":
    upload_json_files_to_s3()
