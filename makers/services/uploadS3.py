import requests
import json
from django.conf import settings
from django.http import JsonResponse
import uuid

def upload_model_to_s3(model_file_url, filename, bucket_name):
    # Define the API Gateway URL and your API key
    api_url = f"https://jpxc4j2v57.execute-api.eu-north-1.amazonaws.com/uploadModel/{bucket_name}/{filename}"
    headers = {
        'x-api-key': settings.aws_lambda_s3_key  # Replace with your actual API key
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





def upload_image_to_s3(uploaded_file,filename, bucket_name):
    """
    Upload the image received in the request body to an S3 bucket via Lambda function.
    """

    if not uploaded_file:
        return JsonResponse({'error': 'No image file found in the request'}, status=400)


    # Prepare the API URL for the Lambda function
    api_url = f"https://12p50emige.execute-api.eu-north-1.amazonaws.com/imageTo3D/imageto3D/{bucket_name}/{filename}"
    headers = {
        'x-api-key': settings.aws_lambda_s3_key  # Replace with your actual API key
    }

    # Prepare the form data to send with the request
    files = {
        'file': (filename, uploaded_file, uploaded_file.content_type),
    }

    # You can include other fields in the payload if required
    payload = {
        'fieldname': 'image',  # Example: you could pass more data if necessary
    }

    try:
        # Send the request to the Lambda function via API Gateway
        response = requests.post(api_url, headers=headers, files=files)

        # Check if the Lambda function responded successfully
        if response.status_code == 200:
            response_data = response.json()
            s3_path = {response_data['s3_url']}
            return JsonResponse({
                'message': 'Image uploaded successfully!',
                's3_url': f"https://makergrid-media.s3.eu-north-1.amazonaws.com/{s3_path}",
            }, status=200)
        else:
            # If something went wrong, print the error response and return it
            return JsonResponse({
                'error': f"Failed to upload the image. Status code: {response.status_code}",
                'details': response.json(),
            }, status=response.status_code)

    except requests.exceptions.RequestException as e:
        # Handle network or other errors during the request
        return JsonResponse({'error': f"Failed to upload image: {str(e)}"}, status=500)
