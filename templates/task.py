# tasks.py
import os
from celery import Celery
import google.generativeai as genai # Used for API interaction
import time
import base66 # For encoding/decoding image data if necessary (not directly used for API payload)
import requests # For API calls

# Configure Celery (using Redis as broker and backend)
# These URLs should match the ones in your app.py
celery_app = Celery(
    'tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Optional: Set a serializer for results if you pass complex objects
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True # Important for production readiness
)

# Configure the Google Gemini API key
# The API key is usually set as an environment variable for security
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@celery_app.task(bind=True)
def generate_veo_video_task(self, prompt: str):
    """
    Celery task to generate a video using an LLM.
    Currently, this simulates video generation by calling an image generation model (Imagen-3.0).
    Real Veo 3 video generation API would be integrated here if directly available.

    Args:
        self: The task instance itself, used for updating status.
        prompt (str): The text prompt for video generation.

    Returns:
        dict: A dictionary containing the video_url if successful, or an error message.
    """
    self.update_state(state='PROGRESS', meta={'status': 'Generating video ideas...'})
    print(f"Task {self.request.id}: Received prompt: {prompt}")

    # Simulate generation time and updates
    time.sleep(2) # Simulate initial processing

    try:
        # --- Simulating Veo 3 Video Generation with Imagen-3.0 for demonstration ---
        # This part would ideally call a dedicated video generation API (e.g., Veo 3)
        # For now, we're using Imagen-3.0 to generate an image as a placeholder for the "video"
        # and returning a URL to that image.

        self.update_state(state='PROGRESS', meta={'status': 'Rendering frames...'})
        print(f"Task {self.request.id}: Calling Imagen-3.0 with prompt: {prompt}")

        # The API key is automatically handled by the Canvas environment when left as an empty string
        # for `imagen-3.0-generate-002` when making the fetch call.
        api_key = ""
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"

        # Payload for structured image generation
        payload = {
            "instances": {
                "prompt": prompt
            },
            "parameters": {
                "sampleCount": 1
            }
        }

        # Exponential backoff for API calls
        retries = 3
        delay = 1
        for i in range(retries):
            try:
                response = requests.post(
                    api_url,
                    headers={'Content-Type': 'application/json'},
                    json=payload
                )
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                result = response.json()

                if result.get('predictions') and len(result['predictions']) > 0 and result['predictions'][0].get('bytesBase64Encoded'):
                    base64_data = result['predictions'][0]['bytesBase64Encoded']
                    image_url = f"data:image/png;base64,{base64_data}"
                    print(f"Task {self.request.id}: Image generated successfully.")
                    return {'video_url': image_url}
                else:
                    raise ValueError("Unexpected API response structure or missing image data.")
            except requests.exceptions.RequestException as e:
                print(f"API call attempt {i+1} failed: {e}")
                if i < retries - 1:
                    time.sleep(delay)
                    delay *= 2 # Exponential backoff
                else:
                    raise # Re-raise after last retry
            except ValueError as e:
                print(f"API call attempt {i+1} failed due to data structure: {e}")
                raise # Re-raise if data structure is unexpected

    except Exception as e:
        # Update state to FAILURE if any error occurs during generation
        print(f"Task {self.request.id}: Video generation failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        return {'error': str(e)}

