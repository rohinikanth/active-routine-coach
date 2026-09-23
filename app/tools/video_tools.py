"""Video generation and Cloud Storage upload tools for ActiveRoutine Coach."""

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


def generate_routine_video(
    prompt_description: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates a short exercise or workout routine video clip for ActiveRoutine Coach using Google's Omni model (gemini-omni-flash-preview) in the global region, saves it as an ADK artifact, and uploads it to public Cloud Storage.

    Args:
        prompt_description: Description of the workout exercise or stretch routine item to visualize (e.g. '5-second desk stretch demonstration').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        Dict containing the public Cloud Storage HTTPS URL of the video and filename.
    """
    client = get_genai_client()
    full_prompt = (
        f"Generate a short 5-second video clip demonstration for active routine exercise: {prompt_description}"
    )

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=full_prompt,
    )

    video_bytes = None
    mime_type = "video/mp4"

    # Extract video bytes from interaction output_video
    if hasattr(interaction, "output_video") and interaction.output_video:
        for vid in interaction.output_video:
            if getattr(vid, "data", None):
                video_bytes = vid.data
                mime_type = getattr(vid, "mime_type", "video/mp4") or "video/mp4"
                break

    # Fallback to steps if output_video is not populated directly
    if not video_bytes and hasattr(interaction, "steps") and interaction.steps:
        for step in interaction.steps:
            contents = getattr(step, "content", []) or []
            if isinstance(contents, list):
                for part in contents:
                    if getattr(part, "type", None) == "video" and getattr(part, "data", None):
                        video_bytes = part.data
                        mime_type = getattr(part, "mime_type", "video/mp4") or "video/mp4"
                        break

    if not video_bytes:
        raise RuntimeError("Failed to extract video bytes from gemini-omni-flash-preview interaction.")

    ext = "mp4"
    filename = f"routine_video_{uuid.uuid4().hex[:8]}.{ext}"

    # 1. Save artifact to Playground via tool_context
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload video bytes directly to public GCS bucket
    storage_client = get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "public_url": public_url,
        "filename": filename,
        "message": f"Generated video and uploaded to {public_url}",
    }
