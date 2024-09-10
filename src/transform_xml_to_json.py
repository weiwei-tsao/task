"""
workflow - the key of step 2 is to read the content from xml files
- Use the xml.etree.ElementTree library to parse xml files:
- convert the event time to required date format and
- calculate user's age to determine is greater or less than the average value and
- write the user data into json file for future usage
"""

import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime
import logging

from utils import setup_logging

# Setup logging
setup_logging()


# Parse xml files
def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    users = []
    for user in root.findall("User"):
        user_data = {
            "UserID": get_field(user, "UserID", default="Unknown"),
            "UserName": get_field(user, "UserName", default="Unknown"),
            "UserAge": safe_int_conversion(get_field(user, "UserAge", default=None)),
            "EventTime": convert_to_iso8601(get_field(user, "EventTime", default=None)),
        }
        users.append(user_data)

    return users


# get fields safely by handling missing fields
def get_field(element, field_name, default=None):
    field = element.find(field_name)
    if field is not None and field.text:
        return field.text
    else:
        logging.warning(f"Missing or empty field: {field_name}")
        return default


# Convert EventTime to ISO 8601 format
def convert_to_iso8601(event_time):
    if event_time is None:
        return (
            "0000-00-00T00:00:00.000Z"  # Return a default date if EventTime is missing
        )
    try:
        event_time_obj = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S")
        return event_time_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    except ValueError:
        logging.error(f"Invalid EventTime format: {event_time}")
        return (
            "0000-00-00T00:00:00.000Z"  # Return default date in case of format errors
        )


#  Convert UserAge to an integer
def safe_int_conversion(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        logging.error(f"Invalid UserAge value: {value}")
        return None


# Calculate average UserAge, excluding None values
def calculate_average_age(users):
    valid_ages = [user["UserAge"] for user in users if user["UserAge"] is not None]

    if not valid_ages:  # Check if the list is empty
        logging.warning("No valid ages found for average calculation.")
        return None  # Return None or an appropriate fallback if there are no valid ages

    return sum(valid_ages) / len(valid_ages)


# Write users to JSON file inside a date folder
def write_to_json_file(file_name, users):

    # Define the directory structure: "json/today's_date/"
    today = datetime.now().strftime("%Y-%m-%d")
    directory = os.path.join("json", today)

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Full path for the JSON file
    full_file_path = os.path.join(directory, file_name)

    # Write the JSON data to the file
    with open(full_file_path, "w") as file:
        for user in users:
            json.dump(user, file)
            file.write("\n")

    logging.info(f"Saved {file_name} in {directory}")


# Main function to transform XML to JSON and categorize users
def transform_xml_to_json(file_path):
    print("Transformation gets started.")
    # parse xml files
    users = parse_xml_file(file_path)

    # calculate average age
    avg_age = calculate_average_age(users)  # Step 2: Calculate average age

    # Error handle
    if avg_age is None:
        logging.error(
            "Cannot calculate average age due to missing or invalid age data."
        )
        return

    # Compare user age with the average value and write to json files
    above_avg_users = [
        user
        for user in users
        if user["UserAge"] is not None and user["UserAge"] > avg_age
    ]
    below_avg_users = [
        user
        for user in users
        if user["UserAge"] is not None and user["UserAge"] <= avg_age
    ]

    write_to_json_file("above_average_output.json", above_avg_users)
    write_to_json_file("below_average_output.json", below_avg_users)

    print(f"Transformation complete. Average age: {avg_age:.2f}")


if __name__ == "__main__":
    transform_xml_to_json("data.xml")
