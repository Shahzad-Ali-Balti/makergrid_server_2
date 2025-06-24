import requests
import json
from django.conf import settings
from django.http import JsonResponse
import uuid
import logging
import requests
import json
from django.conf import settings
import boto3
import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError,BotoCoreError, ClientError

logger = logging.getLogger(__name__)


def upload_model_to_s3(model_file_url, filename, bucket_name):
    """
    Downloads a file from a URL and uploads it to S3 using boto3.
    :param model_file_url: URL of the remote model file.
    :param filename: Desired key (filename) in S3.
    :param bucket_name: Name of the target S3 bucket.
    :return: Public S3 URL if successful, else None.
    """
    try:
        # Step 1: Download the file content from URL
        response = requests.get(model_file_url, stream=True)
        response.raise_for_status()

        # Step 2: Upload the content to S3
        s3_client = boto3.client('s3')
        s3_client.upload_fileobj(response.raw, bucket_name, filename)

        # Step 3: Return the public URL
        public_url = f"https://{bucket_name}.s3.eu-north-1.amazonaws.com/{filename}"
        print(f"S3 Model Uploaded: {public_url}")
        return public_url

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download file: {e}")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to upload to S3: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None


def upload_image_to_s3(uploaded_file, filename, bucket_name, aws_access_key_id, aws_secret_access_key, region_name):

    # Initialize the S3 client with provided AWS credentials
    try:
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=region_name)

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error with AWS credentials: {str(e)}")
        return None

    try:
        # Upload the file directly to S3
        s3_client.upload_fileobj(uploaded_file, bucket_name, filename)

        # Construct the URL for the uploaded file
        s3_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{filename}"
        print(f"File uploaded to S3 successfully! URL: {s3_url}")
        return s3_url

    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return None
