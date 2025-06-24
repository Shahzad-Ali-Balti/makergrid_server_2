# makers/tasks.py
from celery import shared_task
from makers.services.uploadS3 import upload_model_to_s3
from makers.models import Asset
import replicate
from openai import OpenAI
import os
import uuid
import httpx
import django
from django.contrib.auth import get_user_model

django.setup()
User = get_user_model()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
TRELLIS_KEY = os.getenv("TRELLIS_KEY")

@shared_task(bind=True)
def generate_model_task(self, image_url, user_id):
    try:
        print(f"model genaration task is appointed")
        replicate_input = {
            "images": [image_url],
            "texture_size": 2048,
            "mesh_simplify": 0.9,
            "generate_model": True,
            "save_gaussian_ply": True,
            "ss_sampling_steps": 38,
        }

        timeout = httpx.Timeout(300)
        output = replicate.run(TRELLIS_KEY, input=replicate_input, timeout=timeout)

        model_file = output.get("model_file") and output["model_file"].url
        color_video = output.get("color_video") and output["color_video"].url
        gaussian_ply = output.get("gaussian_ply") and output["gaussian_ply"].url

        if not model_file:
            raise ValueError("model_file not found in output")

        # Upload model to S3
        glb_filename = f"{uuid.uuid4()}.glb"
        bucket_name = "makergrid-media"
        s3_url = upload_model_to_s3(model_file, glb_filename, bucket_name)

        # Create Asset
        user = User.objects.get(id=user_id)
        asset = Asset.objects.create(
            user=user,
            model_file=s3_url,
            preview_image_url=image_url,
        )
        print(f'model is generated and stored : {s3_url}')
        return {
            "status": "completed",
            "asset_id": asset.id,
            "stored_path": s3_url,
            "model_file": model_file,
            "color_video": color_video,
            "gaussian_ply": gaussian_ply,
            "preview_image_url": image_url,
            "created_at": str(asset.created_at),
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}

