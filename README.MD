# Project Overview

This project automates the process of detecting daily xml files on SFTP server, transforming to specific json files, uploading to AWS S3.

## Requirements

It asks to implement the following three steps:

- Step 1: Download xml files from SFTP server
- Step 2: Transform xml files to specific json file
- Step 3: Update the json file to S3

## Solution

### Step 1

The workflow of step 1 can be breakdown as following parts:

- Connect to the SFTP server with secured credentials which configured in environment file.
- List all the files on the server and
- Identify files modified in today and
- Copy them to local folder and delete them in the server.

There are couple things which need to be handle carefully. One of the potential is if there are lots of current day files, how to improve the copy action efficiency. The thread pool is applied to help us achieve it.

### Step 2

At this part, the workflow is straightforward:

- parse xml file from the download folder
- do calculation based on user age which gets from each xml file and
- according to the age to group users and
- put each user as one-line json object to a specific json file

In this step, here are couple points need more attention. The first thing is if some fields in the xml file are missing, there should be a default value to handle it. The second thing is that as we need to do age calculation, each user's age must be a valid number to do calculation. Lastly, for future convenience, the generated json files are grouped by the date.

### Step 3

Last part is to upload json files to AWS S3. AWS credentials and S3 configuration are put into the environment file as discussed before.

## Assumptions

SFTP Server: The server is accessible and the structure is consistent, which means files are organized in a way that allows filtering and further action.

Log: Logs are maintained for debugging and auditing,

## Libraries

- `Paramiko`: A Python library to handle the SFTP operations.
- `dotenv`: Used to manage environment variables for secure storage of sensitive information like credentials.
- `Logging`: Standard Python logging is implemented to track the progress of file transfers and any errors encountered.
- `Virtual Environment`: The project is encapsulated in a virtual environment (venv) to isolate dependencies and ensure reproducibility.
- `concurrent.futures`: The module of concurrent.futures is used for asynchronous action, such as download files.
- `xml.etree.ElementTree`: A Python API for parsing and creating XML data.
- `boto3`: AWS SDK for Python to create, and manage AWS services, such as S3.

## Additional

Unit test files are located in the `test` folder, covering majority of each module.
