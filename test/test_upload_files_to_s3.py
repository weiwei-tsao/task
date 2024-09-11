import sys
import os

# Add the `src` directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import unittest
from unittest.mock import patch, MagicMock
from upload_files_to_s3 import upload_to_s3, upload_json_files_to_s3


class TestUploadFilesToS3(unittest.TestCase):

    @patch("boto3.client")
    @patch("os.path.basename")
    @patch("os.path.join")
    def test_upload_to_s3_success(
        self, mock_os_join, mock_os_basename, mock_boto_client
    ):
        # Mock the S3 client and method
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        # Mock the os.path functions
        mock_os_basename.return_value = "test_file.json"
        mock_os_join.return_value = "s3/path/test_file.json"

        # Call the function under test
        upload_to_s3("test_file.json", "test_bucket", "s3/path")

        # Verify that the file was uploaded to S3
        mock_s3.upload_file.assert_called_once_with(
            "test_file.json", "test_bucket", "s3/path/test_file.json"
        )

    @patch("boto3.client")
    @patch("os.path.basename")
    @patch("os.path.join")
    def test_upload_to_s3_failure(
        self, mock_os_join, mock_os_basename, mock_boto_client
    ):
        # Mock the S3 client and method to raise an exception
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = Exception("S3 upload failed")
        mock_boto_client.return_value = mock_s3

        # Mock the os.path functions
        mock_os_basename.return_value = "test_file.json"
        mock_os_join.return_value = "s3/path/test_file.json"

        # Call the function under test and verify that it handles the error
        with self.assertLogs(level="ERROR") as log:
            upload_to_s3("test_file.json", "test_bucket", "s3/path")
            self.assertIn("Error uploading test_file.json to S3", log.output[0])

    @patch("upload_files_to_s3.upload_to_s3")
    @patch("os.path.exists")
    @patch("os.path.join")
    def test_upload_json_files_to_s3(
        self, mock_os_join, mock_os_exists, mock_upload_to_s3
    ):
        # Mock the file paths and their existence
        mock_os_join.side_effect = lambda *args: "/".join(args)
        mock_os_exists.side_effect = (
            lambda path: "above_average_output.json" in path
            or "below_average_output.json" in path
        )

        # Call the function under test
        upload_json_files_to_s3()

        # Verify that both files were uploaded
        mock_upload_to_s3.assert_any_call(
            "json/2024-09-10/above_average_output.json",
            os.getenv("S3_BUCKET"),
            os.getenv("S3_PATH"),
        )
        mock_upload_to_s3.assert_any_call(
            "json/2024-09-10/below_average_output.json",
            os.getenv("S3_BUCKET"),
            os.getenv("S3_PATH"),
        )

    @patch("upload_files_to_s3.upload_to_s3")
    @patch("os.path.exists")
    @patch("os.path.join")
    def test_upload_json_files_to_s3_file_not_found(
        self, mock_os_join, mock_os_exists, mock_upload_to_s3
    ):
        # Mock the file paths and simulate file absence
        mock_os_join.side_effect = lambda *args: "/".join(args)
        mock_os_exists.side_effect = lambda path: False

        # Call the function under test
        with self.assertLogs(level="WARNING") as log:
            upload_json_files_to_s3()
            self.assertIn(
                "File json/2024-09-10/above_average_output.json not found",
                log.output[0],
            )

        # Ensure upload was never called since files don't exist
        mock_upload_to_s3.assert_not_called()


if __name__ == "__main__":
    unittest.main()
