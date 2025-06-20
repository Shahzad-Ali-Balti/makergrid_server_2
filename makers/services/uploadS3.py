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
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
logger = logging.getLogger(__name__)

def upload_model_to_s3_1(model_file_url, filename, bucket_name):
    """
    Upload a model file URL to S3 via Lambda function.
    :param model_url: The URL of the model file to upload.
    :param filename: The desired filename in the S3 bucket.
    :param bucket_name: The name of the target S3 bucket.
    :return: The S3 URL if upload is successful, else None.
    """
    
    # Define the API Gateway URL and your API key
    api_url = f"https://jpxc4j2v57.execute-api.eu-north-1.amazonaws.com/uploadModel/{bucket_name}/{filename}"
    headers = {
        'x-api-key': settings.AWS_LAMBDA_S3_KEY  # Replace with your actual API key from settings
    }

    # Define the payload (body) of the request
    payload = {
        "model_file_url": model_file_url
    }

    try:
        # Make a POST request to the API Gateway
        response = requests.post(api_url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            logger.info("File uploaded to S3 successfully!")
            response_data = response.json()  # Get the JSON response from the API

            # Extract the s3_path from the response body
            s3_path = response_data.get('body', {}).get('s3_path', '')

            # Construct the complete URL for the uploaded model
            if s3_path:
                complete_url = f"https://makergrid-media.s3.eu-north-1.amazonaws.com/{s3_path}"
                logger.info("Complete URL of object: %s", complete_url)
                return complete_url
            else:
                logger.error("Error: No 's3_path' found in the response.")
                return None
        else:
            # Log the failed response
            logger.error(f"Failed to upload the file. Status code: {response.status_code}")
            logger.error("Error response: %s", response.json())
            return None

    except requests.exceptions.RequestException as e:
        # Handle network or request errors
        logger.error(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        # General exception handling
        logger.error(f"An error occurred: {str(e)}")
        return None

def upload_model_to_s3(model_file_url, filename, bucket_name):
    # Define the API Gateway URL and your API key
    api_url = f"https://jpxc4j2v57.execute-api.eu-north-1.amazonaws.com/uploadModel/{bucket_name}/{filename}"
    headers = {
        'x-api-key': settings.AWS_LAMBDA_S3_KEY  # Replace with your actual API key
    }

    # Define the payload (body) of the request
    payload = {
        "model_file_url": model_file_url
    }

    try:
        # Make a POST request to the API Gateway
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        # Check if the request was successful
        if response.status_code == 200:
            print("File uploaded to S3 successfully!")
            response_data = response.json()  # Get the JSON response from the API

            # Extract the s3_path from the response body
            s3_path = response_data.get('body', '').get('s3_path', '')

            # Construct the complete URL for the uploaded model
            if s3_path:
                complete_url = f"https://makergrid-media.s3.eu-north-1.amazonaws.com/{s3_path}"
                print("Complete URL of object:", complete_url)
                return complete_url
            else:
                print("Error: No s3_path found in the response.")
                return None
        else:
            print(f"Failed to upload the file. Status code: {response.status_code}")
            print("Error response:", response.json())
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None





def upload_image_to_s3__1(uploaded_file, filename, bucket_name,aws_access_key_id,aws_secret_access_key,region_name):
    # print(f"aws_access_key_id : {aws_access_key_id}")
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    # s3_client = boto3.client('s3', aws_access_key_id="AKIATSVFBQXL6UJNGZN3",
    #                          aws_secret_access_key="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", region_name="eu-north-1")
    try:
        # Upload the file directly to S3
        s3_client.upload_fileobj(uploaded_file, bucket_name, filename)

        # Construct the URL for the uploaded file
        # s3_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
        s3_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{filename}"

        print(f"File uploaded to S3. URL: {s3_url}")
        return s3_url
    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return None


def upload_image_to_s3(uploaded_file, filename, bucket_name, aws_access_key_id, aws_secret_access_key, region_name):
    """
    Upload the image to an S3 bucket using boto3.

    :param uploaded_file: The file object to upload (typically obtained via Django's request.FILES)
    :param filename: The name to save the file as in the S3 bucket
    :param bucket_name: The name of the S3 bucket
    :param aws_access_key_id: AWS access key ID
    :param aws_secret_access_key: AWS secret access key
    :param region_name: AWS region (e.g., 'us-west-1', 'eu-north-1', etc.)
    :return: S3 URL of the uploaded file or None in case of error
    """

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
