from manim import *
import uuid
from client import client
from backend.logger import logger
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips


"""
Takes in generated scene transcriptions, then generates manim animation and according text-to-speech for each scene, then stitches it together to create a full video.

To generate manim animation, it uses LLMs to generate manim code from the scene descriptions. When generating a scene, it generates the code, then tries to run it. If it fails, it feeds the generated code + error message to the LLM to regenerate the code. This process is repeated until the code runs successfully with a max of 5 tries.

Saves videos in generated_videos folder, and returns the id of the video.
"""

GENERATIONS_PATH = "generated"

MAX_ITERATIONS = 5

SYSTEM_SCENE_PROMPT = """
You are an expert teacher of simple and complex topics, similar to 3 Blue 1 Brown. Given a transcription for a video scene, you are to generate Manim code that will create an animation for the scene. The code should be able to run without errors.

Try to be creative in your visualization of the topic. The scene should be engaging and informative. ONLY generate and return the manim code. Nothing else.

The classname of the root animation should always be VideoScene.
"""

# 480p15 is the resolution and frame rate of the video, change if we want to change the resolution
VIDEO_INTERNAL_PATH = "media/videos/video/480p15/VideoScene.mp4"


class SceneGenerator:
    """
    Initializes the SceneGenerator with the given scene descriptions
    :param scene_transcriptions: List of scene transcriptions (strings)
    """
    def __init__(self, scene_transcriptions):
        self.scene_transcriptions = scene_transcriptions
        self.video_id = str(uuid.uuid4())

    def render_scene(self, scene_id):
        """
        Renders the scene with the given scene id
        :param scene_id: Scene id (string)
        :return: true if the scene was rendered successfully, false otherwise, including the error message (bool, string)
        """
        try:
            # render scene
            # -ql flag is used to render the scene in low quality
            # can add -p to open the scene in preview window
            os.system(f"manim -ql {GENERATIONS_PATH}/{self.video_id}/{scene_id}/video.py VideoScene")
            return True, ""
        except Exception as e:
            return False, str(e)
        

    def add_audio_to_scene(self, scene_id):
        """
        Adds audio to the scene with the given scene id
        :param scene_id: Scene id (string)
        """

        # Step 1: Create audio with tts api

        # Step 2: Add audio to scene

        # Step 3: Profit
        

    def generate_scene(self, scene_description):
        """
        Generates manim code from the scene description
        :param scene_description: Scene description (string)
        :return: scene_id (string)
        """
        iteration = 0
        messages = [{
            "role": "system", "content": SYSTEM_SCENE_PROMPT
        }, {
            "role": "user", "content": scene_description
        }]

        # create scene id
        scene_id = str(uuid.uuid4())

        while iteration < MAX_ITERATIONS:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages
            )
            logger.info(f"Generated response: {response}")
            
            # get output from last message
            output = response.choices[0].message.content

            # strip code block markdown
            output = output.strip("```")

            # append output to messages
            messages.append({"role": "assistant", "content": output})

            # put code in a file
            try:
                with open(f"{GENERATIONS_PATH}/{scene_id}/video.py", "w") as f:
                    f.write(output)
            except Exception as e:
                logger.error(f"Error writing to file: {e}")
                return None

            render_output = self.render_scene(scene_id)

            logger.info(f"Status for scene {scene_id}: {render_output}")

            # note render_output is either True or (False, string)
            if render_output[0]:
                logger.info(f"Scene {scene_id} was rendered successfully")

                # add audio to scene
                return scene_id
            
            # scene was not rendered successfully
            # add error message to messages
            messages.append({"role": "user", "content": f"Error: {render_output[1]}"})
            iteration += 1
            
        # scene was not rendered successfully after MAX_ITERATIONS
        return None
    

    def generate_all_scenes(self):
        """
        Generates manim code for all scenes and stitches them together into a single video.
        :return: Path to the final stitched video.
        """
        scene_ids = []
        video_clips = []

        for scene_description in self.scene_transcriptions:
            scene_id = self.generate_scene(scene_description)
            if scene_id is None:
                logger.error(f"Scene could not be generated for: {scene_description}")
                continue

            scene_path = f"{GENERATIONS_PATH}/{scene_id}/{VIDEO_INTERNAL_PATH}.mp4"
            if os.path.exists(scene_path):
                video_clips.append(VideoFileClip(scene_path))
                scene_ids.append(scene_id)
            else:
                logger.error(f"Video file does not exist for scene ID: {scene_id}")

        if not video_clips:
            logger.error("No scenes were successfully generated.")
            return None

        final_video = concatenate_videoclips(video_clips)
        final_video_path = f"{GENERATIONS_PATH}/{self.video_id}/final_video.mp4"
        final_video.write_videofile(final_video_path, codec="libx264")

        return final_video_path
        

        