import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from hume import HumeStreamClient
from hume.models.config import FaceConfig
import os 
from dotenv import load_dotenv
import tempfile
import time
import sys

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
        time.sleep(5) # wait for the socket to connect
        try:
            while True:
                data = await websocket.receive_text()
                if data.startswith('data:image/png;base64,'):
                    frame_data = base64.b64decode(data.split(",")[1])
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(frame_data)
                        tmp_file_path = tmp_file.name

                    try:
                        result = await socket.send_file(tmp_file_path)
                        await websocket.send_json(result)
                    finally:
                        os.remove(tmp_file_path)
                        time.sleep(2)
                else:
                    print("Received unexpected data format")

        except WebSocketDisconnect as e:
            print("WebSocket connection closed")
            print(f"Error: {e}", sys.exc_info())
        except Exception as e:
            print(f"Error: {e}", sys.exc_info())