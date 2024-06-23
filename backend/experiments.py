from dotenv import load_dotenv
import os
import asyncio

load_dotenv('../.env')

from scene_generator import SceneGenerator

bluetooth_explanation = [
    "The world is filled with an invisible ocean of electromagnetic waves, forming the foundation of all wireless communication.",

    "Bluetooth operates in a specific part of this ocean - the 2.4 GHz band, a public frequency range shared by many devices.",

    "To avoid interference, Bluetooth devices perform a 'frequency hopping dance', rapidly switching between 79 different frequencies up to 1600 times per second.",

    "Before communicating, Bluetooth devices perform a 'secret handshake' called pairing, exchanging unique codes to verify each other's identity.",

    "In a Bluetooth connection, one device acts as the 'master', coordinating up to seven 'slave' devices in a small network called a piconet, orchestrating their synchronized frequency hopping."
]

scene_transcriptions = [
    "That, in fact, is how Bluetooth works. It works by sending an array of signals over to a peer networking device. Once it receives the signal, the networking device sends some signals back to let the original device know that it receives something. "
]

async def main():
    sg = SceneGenerator(bluetooth_explanation)
    await sg.generate_all_scenes()
    # await sg.add_audio_to_scene("54af9765-1da3-42f3-9cb7-2d3a0f48ba25", scene_transcriptions[0], "681a4099-0e50-4539-9a1d-051ec44646b6")

if __name__ == "__main__":
    asyncio.run(main())