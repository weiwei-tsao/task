import sys
import os

# Add the `src` directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import unittest
from unittest.mock import patch, MagicMock
from main import main_workflow


class TestMainWorkflow(unittest.TestCase):

    @patch("main.upload_json_files_to_s3")
    @patch("main.transform_xml_to_json")
    @patch("main.download_today_files")
    @patch("main.logging")
    def test_main_workflow_success(
        self, mock_logging, mock_download_files, mock_transform, mock_upload
    ):
        # Run the main workflow
        main_workflow()

        # Ensure each step is called once
        mock_download_files.assert_called_once()
        mock_transform.assert_called_once_with(
            "./downloads/file1.xml"
        )  # This can be replaced with the actual file path logic
        mock_upload.assert_called_once()

        # Check that logging was called
        mock_logging.info.assert_any_call(
            "Starting the process: Step 1 - Download files from SFTP server"
        )
        mock_logging.info.assert_any_call(
            "Starting the process: Step 2 - Transform XML files to JSON"
        )
        mock_logging.info.assert_any_call(
            "Starting the process: Step 3 - Upload JSON files to S3"
        )
        mock_logging.info.assert_any_call("Process completed successfully!")

    @patch("main.upload_json_files_to_s3")
    @patch("main.transform_xml_to_json")
    @patch("main.download_today_files")
    @patch("main.logging")
    def test_main_workflow_failure(
        self, mock_logging, mock_download_files, mock_transform, mock_upload
    ):
        # Simulate an error during one of the steps
        mock_transform.side_effect = Exception("Transformation error")

        # Run the main workflow
        with self.assertRaises(Exception):
            main_workflow()

        # Ensure the error is logged
        mock_logging.error.assert_called_with("An error occurred: Transformation error")


if __name__ == "__main__":
    unittest.main()
