import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from hume import HumeStreamClient
from hume.models.config import FaceConfig
import os 
from dotenv import load_dotenv
import tempfile
import time
import sys
from pydantic import BaseModel
from transcript_generator import TranscriptGenerator
from scene_generator import SceneGenerator
from logger import logger
import asyncio

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    text: str
    emotions: str # comma separated list of emotions (max 3)

@app.get("/")
def read_root():
    return {"message": "Hello world"}

@app.post("/generate/")
async def generate(request: VideoRequest):
    """
    Takes in a topic and returns a video id for the generated video
    """
    text = request.text
    transcript_generator = TranscriptGenerator()
    transcriptions = await transcript_generator.generate_transcript(text, emotions=request.emotions)
    scene_generator = SceneGenerator(transcriptions)
    video_id = await scene_generator.generate_all_scenes()

    return {"video_id": video_id, "text": "\n".join(transcriptions)}

@app.post("/generate_stub")
async def generate_stub(request: VideoRequest):
    """
    Takes in a topic and returns a video id for the generated video
    """
    return {"video_id": "0dc1c87d-f027-43be-b443-2d573b03ab7a", "text": "This is a stub"}

@app.get("/videos/{video_id}")
async def get_video(video_id: str):
    """
    Returns the video with the given video_id
    """
    video_path = f"generated/{video_id}/final_video.mp4"
    def iterfile():
        with open(video_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/mp4")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client = HumeStreamClient(api_key=os.getenv("HUME_API_KEY"))
    config = FaceConfig(identify_faces=True)
    
    try:
        async with client.connect([config]) as socket:
            logger.info("Connected to Hume API")
            await asyncio.sleep(3)  # wait for the socket to connect
            
            while True:
                try:
                    data = await websocket.receive_text()
                    if data.startswith('data:image/png;base64,'):
                        frame_data = base64.b64decode(data.split(",")[1])
                        
                        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                            tmp_file.write(frame_data)
                            tmp_file_path = tmp_file.name

                        logger.debug(f"Temporary file saved at: {tmp_file_path}")

                        try:
                            if os.path.exists(tmp_file_path) and os.path.getsize(tmp_file_path) > 0:
                                logger.debug(f"File size: {os.path.getsize(tmp_file_path)} bytes")
                                result = await socket.send_file(tmp_file_path)
                                await websocket.send_json(result)
                            else:
                                logger.error("Temporary file is empty or does not exist")
                        except Exception as e:
                            logger.exception(f"Error processing file: {e}")
                        finally:
                            os.unlink(tmp_file_path)  # Delete the temporary file
                    else:
                        logger.warning(f"Received unexpected data format: {data[:50]}...")
                except WebSocketDisconnect:
                    logger.info("WebSocket connection closed by client")
                    break
                except Exception as e:
                    logger.exception(f"Unexpected error in WebSocket loop: {e}")
                    await websocket.close(code=1011)  # Internal error
                    break
    except Exception as e:
        logger.exception(f"Error setting up Hume client: {e}")
        await websocket.close(code=1011)  # Internal error
