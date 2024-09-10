import sys
import os

# Add the `src` directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
from transform_xml_to_json import (
    parse_xml_file,
    convert_to_iso8601,
    write_to_json_file,
    transform_xml_to_json,
)
from xml.etree.ElementTree import Element, SubElement, tostring


class TestTransformXmlToJsonWithSampleData(unittest.TestCase):

    def setUp(self):
        # Setup XML structure that matches the provided sample XML data
        self.root = Element("Users")

        # Sample users
        users = [
            {
                "UserID": "1",
                "UserName": "Alice",
                "UserAge": "30",
                "EventTime": "2024-07-30T10:00:00",
            },
            {
                "UserID": "2",
                "UserName": "Bob",
                "UserAge": "25",
                "EventTime": "2024-07-30T11:00:00",
            },
            {
                "UserID": "3",
                "UserName": "Charlie",
                "UserAge": "35",
                "EventTime": "2024-07-30T12:00:00",
            },
            {
                "UserID": "4",
                "UserName": "David",
                "UserAge": "28",
                "EventTime": "2024-07-30T13:00:00",
            },
            {
                "UserID": "5",
                "UserName": "Eve",
                "UserAge": "40",
                "EventTime": "2024-07-30T14:00:00",
            },
            {
                "UserID": "6",
                "UserName": "Frank",
                "UserAge": "22",
                "EventTime": "2024-07-30T15:00:00",
            },
            {
                "UserID": "7",
                "UserName": "Grace",
                "UserAge": "33",
                "EventTime": "2024-07-30T16:00:00",
            },
            {
                "UserID": "8",
                "UserName": "Heidi",
                "UserAge": "27",
                "EventTime": "2024-07-30T17:00:00",
            },
            {
                "UserID": "9",
                "UserName": "Ivy",
                "UserAge": "31",
                "EventTime": "2024-07-30T18:00:00",
            },
            {
                "UserID": "10",
                "UserName": "Judy",
                "UserAge": "29",
                "EventTime": "2024-07-30T19:00:00",
            },
        ]

        # Create the XML tree structure
        for user in users:
            user_element = SubElement(self.root, "User")
            for key, value in user.items():
                field = SubElement(user_element, key)
                field.text = value

        self.xml_data = tostring(self.root)

    @patch("xml.etree.ElementTree.parse")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_transform_xml_to_json(self, mock_makedirs, mock_open_file, mock_et_parse):
        # Mock the XML parsing
        mock_et_parse.return_value.getroot.return_value = self.root

        # Mock file writing
        mock_open = mock_open_file()

        # Call the function under test
        transform_xml_to_json("dummy_path")

        # Assert that the appropriate directories are created
        mock_makedirs.assert_called()

        # Verify the written content
        expected_above_avg_users = [
            {
                "UserID": "1",
                "UserName": "Alice",
                "UserAge": 30,
                "EventTime": "2024-07-30T10:00:00.000Z",
            },
            {
                "UserID": "3",
                "UserName": "Charlie",
                "UserAge": 35,
                "EventTime": "2024-07-30T12:00:00.000Z",
            },
            {
                "UserID": "5",
                "UserName": "Eve",
                "UserAge": 40,
                "EventTime": "2024-07-30T14:00:00.000Z",
            },
            {
                "UserID": "7",
                "UserName": "Grace",
                "UserAge": 33,
                "EventTime": "2024-07-30T16:00:00.000Z",
            },
            {
                "UserID": "9",
                "UserName": "Ivy",
                "UserAge": 31,
                "EventTime": "2024-07-30T18:00:00.000Z",
            },
        ]

        expected_below_avg_users = [
            {
                "UserID": "2",
                "UserName": "Bob",
                "UserAge": 25,
                "EventTime": "2024-07-30T11:00:00.000Z",
            },
            {
                "UserID": "4",
                "UserName": "David",
                "UserAge": 28,
                "EventTime": "2024-07-30T13:00:00.000Z",
            },
            {
                "UserID": "6",
                "UserName": "Frank",
                "UserAge": 22,
                "EventTime": "2024-07-30T15:00:00.000Z",
            },
            {
                "UserID": "8",
                "UserName": "Heidi",
                "UserAge": 27,
                "EventTime": "2024-07-30T17:00:00.000Z",
            },
            {
                "UserID": "10",
                "UserName": "Judy",
                "UserAge": 29,
                "EventTime": "2024-07-30T19:00:00.000Z",
            },
        ]

        # Capture written data
        calls = mock_open.write.call_args_list
        written_data = "".join([call[0][0] for call in calls])

        # Validate content for above and below average users
        for user in expected_above_avg_users:
            self.assertIn(json.dumps(user), written_data)

        for user in expected_below_avg_users:
            self.assertIn(json.dumps(user), written_data)


if __name__ == "__main__":
    unittest.main()
