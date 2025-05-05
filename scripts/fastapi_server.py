from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import subprocess
from typing import Optional
import tempfile

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

@app.post("/generate-video")
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
    try:
        # Generate unique filenames
        input_image_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_{image.filename}")
        output_video_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.mp4")
        
        # Save uploaded image
        with open(input_image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Generate video using ffmpeg
        # This creates a video that shows the static image for the specified duration
        ffmpeg_cmd = f"ffmpeg -loop 1 -i {input_image_path} -c:v libx264 -t {duration} -pix_fmt yuv420p -vf fps={fps} {output_video_path}"
        subprocess.run(ffmpeg_cmd, shell=True, check=True)
        
        # Return the video file
        return FileResponse(
            path=output_video_path,
            media_type="video/mp4",
            filename="generated_video.mp4"
        )
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        # Clean up temporary files
        if os.path.exists(input_image_path):
            os.remove(input_image_path)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 