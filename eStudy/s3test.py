import boto3

import os
from dotenv import load_dotenv

load_dotenv()

from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Custom S3 endpoint and credentials
CUSTOM_ENDPOINT_URL = os.getenv('CUSTOM_ENDPOINT_URL')
AWS_ACCESS_KEY_ID =os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')  
FILE_KEY = os.getenv('FILE_KEY')  

# Initialize the S3 client with the custom endpoint
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=CUSTOM_ENDPOINT_URL  # Specify the custom endpoint
)

def read_file_from_s3(bucket_name, file_key):
    try:
        # Fetch the file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read() 
        return file_content
    except NoCredentialsError:
        print("Error: No AWS credentials found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Test the function
if __name__ == "__main__":
    content = read_file_from_s3(BUCKET_NAME, FILE_KEY)
    if content:
        print("File content fetched successfully!")
        # Save the file locally (optional)
        with open(FILE_KEY, 'wb') as file:
            file.write(content)
        print(f"File saved as {FILE_KEY}")