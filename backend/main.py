import base64
from fastapi import FastAPI, WebSocket
from hume import HumeStreamClient
from hume.models.config import FaceConfig
import os 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello world"}

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



