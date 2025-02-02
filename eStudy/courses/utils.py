import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_presigned_url(bucket_name, file_key, expiration=10, range_start=None, range_end=None):
    """
    Generate a pre-signed URL for accessing an S3 object, adjusting expiration 
    based on video size (not the actual video length).
    """
    try:
        # Fetch AWS credentials from environment variables
        AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        CUSTOM_ENDPOINT_URL = os.getenv('CUSTOM_ENDPOINT_URL')
        
        # Create an S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=CUSTOM_ENDPOINT_URL
        )
        
        # Get video metadata (for size) to estimate streaming time or expiration time
        head_object = s3_client.head_object(Bucket=bucket_name, Key=file_key)
        video_size = head_object['ContentLength']  # Get the file size (in bytes)
        
        # Estimate expiration time based on video size (this is an approximation)
        # Assuming average bitrate for video content and that larger files should have a longer expiration time
        estimated_duration = video_size / (1024 * 1024 * 5)  # For example, ~5MB per second of video (approx)
        adjusted_expiration = max(expiration, int(estimated_duration * 1.5))  # 1.5x for safety

        # Generate the presigned URL with adjusted expiration
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=adjusted_expiration
        )
        return presigned_url

    except Exception as e:
        return None
