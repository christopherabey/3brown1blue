import base64
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from hume import HumeStreamClient
from hume.models.config import FaceConfig
import os 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello world"}

@app.get("/generate")
async def generate():
    """
    Takes in a topic and returns a video id for the generated video
    """
    return {"message": "Generating scenes"}

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
    
    async with client.connect([config]) as socket:
        while True:
            data = await websocket.receive_text()
            frame_data = base64.b64decode(data.split(",")[1])
            
            result = await socket.send_file(frame_data)
            await websocket.send_json(result)



