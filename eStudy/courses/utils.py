import boto3
import os
from dotenv import load_dotenv
from courses.models import Video  


load_dotenv()

def generate_presigned_url(bucket_name, file_key):
    try:

        AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        CUSTOM_ENDPOINT_URL = os.getenv('CUSTOM_ENDPOINT_URL')

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=CUSTOM_ENDPOINT_URL
        )
        try:
            video = Video.objects.get(s3_file_key=file_key)
            playtime_minutes = video.playtime
        except Video.DoesNotExist:
            return None
        print(f'playtime :{playtime_minutes}')

        adjusted_expiration = int(playtime_minutes * 60 * 1.5)
        print(adjusted_expiration)

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=adjusted_expiration
        )

        return presigned_url

    except Exception as e:
        print(f"Error: {e}")
        return None
