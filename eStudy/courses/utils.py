import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv

load_dotenv()
def generate_presigned_url(bucket_name, file_key, expiration=3600):



    CUSTOM_ENDPOINT_URL = os.getenv('CUSTOM_ENDPOINT_URL')
    AWS_ACCESS_KEY_ID =os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('BUCKET_NAME')  
    """
    Generates a pre-signed URL for an S3 object.
    :param bucket_name: The name of the S3 bucket.
    :param file_key: The key (path) of the file in the S3 bucket.
    :param expiration: The expiration time for the URL in seconds (default: 1 hour).
    :return: The pre-signed URL or None if an error occurs.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id= AWS_ACCESS_KEY_ID,
        aws_secret_access_key=  AWS_SECRET_ACCESS_KEY,
        endpoint_url= CUSTOM_ENDPOINT_URL  # Custom endpoint
    )

    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=expiration
        )
        return url
    except NoCredentialsError:
        print("Error: No AWS credentials found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None