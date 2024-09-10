from datetime import datetime
import logging
import os


def setup_logging(log_dir="./logs"):
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    log_filename = os.path.join(log_dir, f"sftp_xml_to_json_s3_{datetime.now().strftime("%Y%m%d%-H%M%S")}.log")
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(message)s')
