import sys
import os

# Add the `src` directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
from transform_xml_to_json import (
    calculate_average_age,
    get_field,
    parse_xml_file,
    convert_to_iso8601,
    safe_int_conversion,
    write_to_json_file,
    transform_xml_to_json,
)
from xml.etree.ElementTree import Element, SubElement, tostring


class TestTransformXmlToJson(unittest.TestCase):

    @patch("xml.etree.ElementTree.parse")
    def test_parse_xml_file(self, mock_et_parse):
        # Mock the XML structure
        mock_tree = MagicMock()
        mock_et_parse.return_value = mock_tree
        mock_root = MagicMock()
        mock_tree.getroot.return_value = mock_root

        # Mock user element and fields
        mock_user = MagicMock()
        mock_root.findall.return_value = [mock_user]
        mock_user.find.side_effect = lambda x: MagicMock(text=x)

        result = parse_xml_file("./downloads/file1.xml")
        self.assertEqual(result[0]["UserID"], "UserID")
        self.assertEqual(result[0]["UserName"], "UserName")
        self.assertEqual(result[0]["UserAge"], None)  # Testing default None case

    def test_get_field(self):
        mock_element = MagicMock()
        mock_field = MagicMock(text="SampleText")
        mock_element.find.return_value = mock_field

        result = get_field(mock_element, "FieldName", default="Default")
        self.assertEqual(result, "SampleText")

        # Missing field case
        mock_element.find.return_value = None
        result = get_field(mock_element, "MissingField", default="Default")
        self.assertEqual(result, "Default")

    def test_convert_to_iso8601(self):
        valid_event_time = "2024-09-01T12:34:56"
        result = convert_to_iso8601(valid_event_time)
        self.assertEqual(result, "2024-09-01T12:34:56.000Z")

        # Invalid event time
        invalid_event_time = "invalid_time"
        result = convert_to_iso8601(invalid_event_time)
        self.assertEqual(result, "0000-00-00T00:00:00.000Z")

    def test_safe_int_conversion(self):
        result = safe_int_conversion("30")
        self.assertEqual(result, 30)

        # Invalid integer conversion
        result = safe_int_conversion("invalid")
        self.assertIsNone(result)

    def test_calculate_average_age(self):
        users = [{"UserAge": 30}, {"UserAge": 40}, {"UserAge": None}]
        result = calculate_average_age(users)
        self.assertEqual(result, 35)

        # No valid ages case
        users = [{"UserAge": None}]
        result = calculate_average_age(users)
        self.assertIsNone(result)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_write_to_json_file(self, mock_makedirs, mock_open_file):
        users = [{"UserID": "1", "UserName": "Test"}]
        write_to_json_file("test.json", users)

        # Check if directory was created
        mock_makedirs.assert_called_once()

        # Check if file was opened and written to
        mock_open_file.assert_called_once_with(
            os.path.join("json", "2024-09-10", "test.json"), "w"
        )
        mock_open_file().write.assert_called()

    @patch("transform_xml_to_json.parse_xml_file")
    @patch("transform_xml_to_json.calculate_average_age")
    @patch("transform_xml_to_json.write_to_json_file")
    def test_transform_xml_to_json(
        self, mock_write_to_json, mock_calculate_average, mock_parse_xml
    ):
        # Mock users and average age calculation
        mock_parse_xml.return_value = [{"UserAge": 30}, {"UserAge": 25}]
        mock_calculate_average.return_value = 27

        transform_xml_to_json("./downloads/file1.xml")

        # Ensure users were written to the correct files
        mock_write_to_json.assert_any_call(
            "above_average_output.json", [{"UserAge": 30}]
        )
        mock_write_to_json.assert_any_call(
            "below_average_output.json", [{"UserAge": 25}]
        )


if __name__ == "__main__":
    unittest.main()
