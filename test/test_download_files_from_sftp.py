import sys
import os

# Add the `src` directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


# tests/test_download_files_from_sftp.py
import unittest
from unittest.mock import ANY, patch, MagicMock
from download_files_from_sftp import (
    create_sftp_connection,
    get_files_from_sftp,
    is_modified_today,
    download_and_delete_file,
    download_today_files,
)
from datetime import datetime
import paramiko

SAMPLE_XML_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<Users>
    <User>
        <UserID>1</UserID>
        <UserName>Alice</UserName>
        <UserAge>30</UserAge>
        <EventTime>2024-09-10T10:00:00</EventTime>
    </User>
</Users>
"""


# Test create_sftp_connection
class TestCreateSFTPConnection(unittest.TestCase):
    @patch("paramiko.Transport")
    def test_create_sftp_connection_success(self, mock_transport):
        mock_sftp = MagicMock(spec=paramiko.SFTPClient)
        mock_transport.return_value = MagicMock()
        with patch("paramiko.SFTPClient.from_transport", return_value=mock_sftp):
            sftp = create_sftp_connection()
            self.assertIsNotNone(sftp)

    @patch("paramiko.Transport")
    def test_create_sftp_connection_fail(self, mock_transport):
        mock_transport.side_effect = Exception("Connection failed")
        sftp = create_sftp_connection()
        self.assertIsNone(sftp)


# Test get_files_from_sftp to return XML files
class TestGetFilesFromSFTP(unittest.TestCase):

    @patch("paramiko.SFTPClient.listdir_attr")
    def test_get_files_from_sftp_success(self, mock_listdir):
        mock_sftp = MagicMock()

        # Create a mock file attribute object
        mock_file_attr = MagicMock()
        mock_file_attr.filename = "file1.xml"

        # Mock listdir_attr to return a list of file attributes
        mock_listdir.return_value = [mock_file_attr]

        files = get_files_from_sftp(mock_sftp, "/data")

        # Ensure the correct file list is returned
        self.assertEqual(files, [mock_file_attr])

    @patch("paramiko.SFTPClient.listdir_attr")
    def test_get_files_from_sftp_fail(self, mock_listdir):
        mock_sftp = MagicMock()
        mock_listdir.side_effect = Exception("Failed to list files")

        files = get_files_from_sftp(mock_sftp, "/data")

        # Ensure an empty list is returned on failure
        self.assertEqual(files, [])


# Test is_modified_today
class TestIsModifiedToday(unittest.TestCase):

    def test_is_modified_today_true(self):
        mock_file_attr = MagicMock()
        mock_file_attr.st_mtime = datetime.now().timestamp()
        result = is_modified_today(mock_file_attr)
        self.assertTrue(result)

    def test_is_modified_today_false(self):
        mock_file_attr = MagicMock()
        mock_file_attr.st_mtime = datetime.now().timestamp() - 86400  # Yesterday
        result = is_modified_today(mock_file_attr)
        self.assertFalse(result)


# Test download_and_delete_file function with XML content
class TestDownloadAndDeleteFile(unittest.TestCase):
    @patch("paramiko.SFTPClient.getfo")
    @patch("paramiko.SFTPClient.remove")
    def test_download_and_delete_file_success(self, mock_remove, mock_getfo):
        mock_sftp = MagicMock()
        mock_file_attr = MagicMock()
        mock_file_attr.filename = "file1.xml"

        # Mock the getfo call to write the sample XML content
        mock_getfo.side_effect = lambda remote, local_file: local_file.write(
            SAMPLE_XML_CONTENT
        )

        # Call the function
        download_and_delete_file(mock_sftp, mock_file_attr)

        # Ensure getfo is called once
        mock_getfo.assert_called_once_with(os.path.join("/data", "file1.xml"), ANY)
        mock_remove.assert_called_once_with(os.path.join("/data", "file1.xml"))


# Test download_today_files
class TestDownloadTodayFiles(unittest.TestCase):
    @patch("download_files_from_sftp.ThreadPoolExecutor")
    @patch("download_files_from_sftp.create_sftp_connection")
    @patch("download_files_from_sftp.get_files_from_sftp")
    @patch("download_files_from_sftp.is_modified_today")
    def test_download_today_files(
        self, mock_is_modified_today, mock_get_files, mock_create_sftp, mock_executor
    ):
        # Mock SFTP connection and files
        mock_sftp = MagicMock()
        mock_create_sftp.return_value = mock_sftp
        mock_file_attr = MagicMock()
        mock_file_attr.st_mtime = datetime.now().timestamp()
        mock_get_files.return_value = [mock_file_attr]
        mock_is_modified_today.return_value = True

        # Mock ThreadPoolExecutor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance

        # Call the function
        download_today_files()

        # Ensure that files modified today are downloaded
        mock_executor_instance.submit.assert_called_once()

    @patch("download_files_from_sftp.create_sftp_connection")
    def test_no_sftp_connection(self, mock_create_sftp):
        mock_create_sftp.return_value = None
        download_today_files()
        mock_create_sftp.assert_called_once()


if __name__ == "__main__":
    unittest.main()
