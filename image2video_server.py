from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import subprocess
from typing import Optional
import tempfile
import logging

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temporary directory for storing files
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/image-video")
async def generate_video(
    image: UploadFile = File(...),
    duration: Optional[int] = 5,
    fps: Optional[int] = 30
):
    """
    Generate a video from an uploaded image.

    Parameters:
    - image: The input image file
    - duration: Duration of the output video in seconds (default: 5)
    - fps: Frames per second of the output video (default: 30)

    Returns:
    - The generated video file
    """
    # Generate unique filenames
    image_prefix = f"{uuid.uuid4()}_{image.filename}"
    input_image_path = os.path.join(TEMP_DIR, image_prefix)
    try:

        # output_video_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.mp4")
        logger.info(f"Received image: {image.filename}")
        logger.info(f"Saving uploaded image to: {input_image_path}")
        name_prefix = os.path.basename(image_prefix).split('.')[0]

        # Save uploaded image
        with open(input_image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        logger.info(f"Image saved successfully.")

        # Generate video using ffmpeg
        # This creates a video that shows the static image for the specified duration
        # Use LivePortrait's inference.py instead of ffmpeg
        driving_video_path = "assets/examples/driving/video.pkl"  # Fixed driving video path
        inference_cmd = f"python inference.py -s {input_image_path} -d {driving_video_path}"
        logger.info(f"Running LivePortrait inference command: {inference_cmd}")
        subprocess.run(inference_cmd, shell=True, check=True)
        # Extract the filename without extension from input_image_path
        output_video_path = f"animations/{name_prefix}--video.mp4"
        logger.info(f"Video generated at: {output_video_path}")

        # Return the video file
        return FileResponse(
            path=output_video_path,
            media_type="video/mp4",
            filename="generated_video.mp4"
        )

    except Exception as e:
        logger.error(f"Error during video generation: {e}")
        return {"error": str(e)}

    finally:
        # Clean up temporary files
        if os.path.exists(input_image_path):
            os.remove(input_image_path)
            logger.info(f"Deleted temporary image: {input_image_path}")
        # if os.path.exists(output_video_path):
        #     os.remove(output_video_path)
        #     logger.info(f"Deleted temporary video: {output_video_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# uvicorn image2video_server:app --host 0.0.0.0 --port 8888
