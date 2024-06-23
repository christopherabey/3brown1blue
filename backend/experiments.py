from dotenv import load_dotenv
import os

load_dotenv('../.env')

from scene_generator import SceneGenerator

test_transcriptions = [
    "The quick brown fox jumps over the lazy dog.",
    "That, in fact, is how Bluetooth works. It works by sending an array of signals over to a peer networking device. Once it receives the signal, the networking device sends some signals back to let the original device know that it receives something. "
]

sg = SceneGenerator(test_transcriptions)
# sg.video_id = "da398880-53e7-447a-b324-391436e871b9"
# sg.render_scene("93f5a28c-bc48-4b0c-9f61-4b979da8a060")

sg.generate_all_scenes()