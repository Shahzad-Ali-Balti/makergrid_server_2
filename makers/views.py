import os
import uuid
import requests
import time
from dotenv import load_dotenv
from django.conf import settings
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Asset
from .serializers import AssetSerializer
from core.authentication.authentication import JWTAuthentication
from .pagination import CustomPageNumberPagination

from makers.services.uploadS3 import upload_model_to_s3,upload_image_to_s3
import replicate
from openai import OpenAI
import traceback
import httpx
load_dotenv(override=True)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRELLIS_KEY = os.getenv("TRELLIS_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def normalize_text(text):
    return text.lower().replace("-", " ").replace("_", " ").strip()


class TextTo3DModelView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        user_prompt = request.data.get("prompt")
        style = request.data.get("style")
        complexity = request.data.get("complexity")
        optimize_printing = request.data.get("optimize_printing")

        if not user_prompt or not style or not complexity:
            return Response({"error": "Prompt, style, and complexity are required."}, status=400)

        complexity_map = {
            "simple": "dall-e-2",
            "medium": "dall-e-2",
            "complex": "dall-e-3",
            "very complex": "dall-e-3",
        }

        style_descriptions = {
            "realistic": "photorealistic precision with accurate textures and lighting",
            "stylized": "heavily stylized with exaggerated forms and bold colors",
            "low-poly": "minimalist low-poly style for games",
            "sci-fi": "futuristic, metallic, neon-lit design",
            "fantasy": "mythical elements and magical scenery",
            "miniature": "detailed miniatures for tabletop gaming",
            "cartoon": "cartoonish, bold outlines, expressive features"
        }

        model_type = complexity_map.get(normalize_text(complexity), "dall-e-2")
        style_instruction = style_descriptions.get(normalize_text(style), style_descriptions["realistic"])

        final_prompt = (
            f"Generate an image from: {user_prompt}. Style should be {style_instruction}. "
            "Use a pure black background with the subject centered."
        )

        if optimize_printing:
            final_prompt += " Ensure 3D printability with correct thickness and no fragile parts."

        image_size = "1792x1024" if normalize_text(complexity) == "very complex" else "1024x1024"

        try:
            image_response = client.images.generate(
                model=model_type,
                prompt=final_prompt,
                size=image_size,
                n=1,
            )
            image_url = image_response.data[0].url

            replicate_input = {
                "images": [image_url],
                "texture_size": 2048,
                "mesh_simplify": 0.9,
                "generate_model": True,
                "save_gaussian_ply": True,
                "ss_sampling_steps": 38,
            }
            timeout=httpx.Timeout(300)
            output = replicate.run(TRELLIS_KEY, input=replicate_input,timeout=timeout)
            model_file = output.get("model_file") and output["model_file"].url
            color_video = output.get("color_video") and output["color_video"].url
            gaussian_ply = output.get("gaussian_ply") and output["gaussian_ply"].url

            if not model_file:
                return Response({"error": "model_file not found in output"}, status=500)

            glb_filename = f"{uuid.uuid4()}.glb"
            bucket_name = "makergrid-media"

            s3_url = upload_model_to_s3(model_file,glb_filename,bucket_name)

            asset = Asset.objects.create(
                user=request.user,
                prompt=user_prompt,
                model_file=s3_url,
                preview_image_url=image_url,
                style=style,
                complexity=complexity,
                optimize_printing=optimize_printing
            )

            response = Response({
                "message": "✅ 3D model created.",
                "asset_id": asset.id,
                "model_file": model_file,
                "gaussian_ply": gaussian_ply,
                "color_video": color_video,
                "stored_path": s3_url,
                "preview_image_url": image_url,
                "created_at": asset.created_at,
            })

            if (new_token := request.META.get('HTTP_NEW_ACCESS')):
                response['New-Access-Token'] = new_token

            return response

        except Exception as e:
            print("🔥 Exception in TextTo3DModelView:")
            print(traceback.format_exc()) 
            return Response({"error": str(e)}, status=500)


class ImageTo3DModelView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    print("Image to Model Requested")

    def post(self, request):
        try:
            uploaded_file = request.FILES.get("image")
            if not uploaded_file:
                return Response({"error": "No image uploaded"}, status=400)
            
            filename = f"temp_{uuid.uuid4()}.png"
            bucket_name = "makergrid-media"
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            region_name=settings.AWS_S3_REGION_NAME
            image_url = upload_image_to_s3(uploaded_file,filename,bucket_name,aws_access_key_id,aws_secret_access_key,region_name)
            print(f"image_url for public :{image_url}")

            replicate_input = {
                "images": [image_url],
                "texture_size": 2048,
                "mesh_simplify": 0.9,
                "generate_model": True,
                "save_gaussian_ply": True,
                "ss_sampling_steps": 38,
            }
            timeout = httpx.Timeout(300)
            output = replicate.run(TRELLIS_KEY, input=replicate_input,timeout=timeout)
            if not output:
                return Response({"error": "Replicate output was None. Check API key, image URL, or payload format."}, status=500)
            model_file = output.get("model_file") and output["model_file"].url
            color_video = output.get("color_video") and output["color_video"].url
            gaussian_ply = output.get("gaussian_ply") and output["gaussian_ply"].url

            if not model_file:
                return Response({"error": "model_file not found in output"}, status=500)

            glb_filename = f"{uuid.uuid4()}.glb"
            bucket_name = "makergrid-media"

            s3_url = upload_model_to_s3(model_file,glb_filename,bucket_name)
            asset = Asset.objects.create(
                user=request.user,
                model_file=s3_url,
                preview_image_url=image_url,
            )

            response = Response({
                "message": "✅ 3D model created.",
                "asset_id": asset.id,
                "model_file": model_file,
                "gaussian_ply": gaussian_ply,
                "color_video": color_video,
                "stored_path": s3_url,
                "preview_image_url": image_url,
                "created_at": asset.created_at,
            })

            if (new_token := request.META.get('HTTP_NEW_ACCESS')):
                response['New-Access-Token'] = new_token

            return response


        except Exception as e:
            print("🔥 Exception in TextTo3DModelView:")
            print(traceback.format_exc()) 
            return Response({"error": str(e)}, status=500)

class AssetListCreateView(generics.ListCreateAPIView):
    serializer_class = AssetSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Asset.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AssetRetrieveView(generics.RetrieveAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class UserAssetsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        assets = Asset.objects.filter(user=user).order_by('-created_at')

        paginator = CustomPageNumberPagination()
        paginated = paginator.paginate_queryset(assets, request)
        serializer = AssetSerializer(paginated, many=True)

        has_next_page = paginator.page.has_next() if paginator.page else False

        return Response({
            "items": serializer.data,
            "hasNextPage": has_next_page
        })
