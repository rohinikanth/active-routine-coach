"""Image generation and Cloud Storage upload tools for ActiveRoutine Coach."""

from typing import Any, Dict
import uuid

from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# Hardcoded project ID and public Cloud Storage bucket name
PROJECT_ID = "qwiklabs-gcp-03-9a71b17e4d3a"
BUCKET_NAME = "active-routine-coach-media-qwiklabs-gcp-03-9a71b17e4d3a"

# Lazy client initializers
_genai_client: genai.Client = None
_storage_client: storage.Client = None


def get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )
    return _genai_client


def get_storage_client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


def generate_routine_image(
    prompt_description: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates a visual badge or exercise illustration for ActiveRoutine Coach, saves it as an ADK artifact, and uploads it to public GCS.

    Args:
        prompt_description: Description of the routine visual card or badge (e.g. '10-Min Desk Stretch Workout Badge').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        Dict containing the public Cloud Storage HTTPS URL of the image and filename.
    """
    client = get_genai_client()
    full_prompt = (
        f"A vibrant, professional motivational badge illustration for an active productivity routine: {prompt_description}"
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=full_prompt,
    )

    part = response.candidates[0].content.parts[0]
    image_bytes = part.inline_data.data
    mime_type = part.inline_data.mime_type or "image/png"

    ext = "jpg" if "jpeg" in mime_type.lower() else "png"
    filename = f"routine_badge_{uuid.uuid4().hex[:8]}.{ext}"

    # 1. Save artifact to Playground via tool_context
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes directly to public GCS bucket
    storage_client = get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "public_url": public_url,
        "filename": filename,
        "message": f"Generated image and uploaded to {public_url}",
    }
