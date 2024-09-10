import sys
import os

# Add the `src` directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock
from src import download_files_from_sftp as dffs


class TestDownloadFilesFromSFTP(unittest.TestCase):

    @patch("download_files_from_sftp.paramiko.SFTPClient")
    @patch("download_files_from_sftp.paramiko.Transport")
    def test_create_sftp_connection_success(self, mock_transport, mock_sftp_client):
        # Mock successful SFTP connection
        mock_transport.return_value = MagicMock()
        mock_sftp_client.from_transport.return_value = MagicMock()

        # Test connection
        sftp = dffs.create_sftp_connection()
        self.assertIsNotNone(sftp)
        mock_transport.assert_called_once_with(("testFTP.dv.com", 22))
        mock_sftp_client.from_transport.assert_called_once()

    @patch("download_files_from_sftp.paramiko.SFTPClient")
    @patch("download_files_from_sftp.paramiko.Transport")
    def test_create_sftp_connection_failure(self, mock_transport, mock_sftp_client):
        # Mock connection failure
        mock_transport.side_effect = Exception("Failed to connect")

        # Test connection failure handling
        sftp = dffs.create_sftp_connection()
        self.assertIsNone(sftp)

    @patch("download_files_from_sftp.paramiko.SFTPClient")
    def test_get_files_from_sftp(self, mock_sftp_client):
        # Mock the file list with attributes
        mock_file_attr = MagicMock()
        mock_file_attr.st_mtime = 1609459200  # Simulate a file modified on 2021-01-01
        mock_file_attr.filename = "test_file.xml"
        mock_sftp_client.listdir_attr.return_value = [mock_file_attr]

        # Test file retrieval
        file_list = dffs.get_files_from_sftp(mock_sftp_client, "/data")
        self.assertEqual(len(file_list), 1)
        self.assertEqual(file_list[0].filename, "test_file.xml")


if __name__ == "__main__":
    unittest.main()
