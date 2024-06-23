# from manim import *
import dotenv
dotenv.load_dotenv()

import uuid
from client import client
from logger import logger
import os
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips
import json


"""
Takes in generated scene transcriptions, then generates manim animation and according text-to-speech for each scene, then stitches it together to create a full video.

To generate manim animation, it uses LLMs to generate manim code from the scene descriptions. When generating a scene, it generates the code, then tries to run it. If it fails, it feeds the generated code + error message to the LLM to regenerate the code. This process is repeated until the code runs successfully with a max of 5 tries.

Saves videos in generated_videos folder, and returns the id of the video.
"""

GENERATIONS_PATH = "generated"

MAX_ITERATIONS = 5

SYSTEM_SCENE_PROMPT = """
You are an expert teacher of simple and complex topics, similar to 3 Blue 1 Brown. Given a transcription for a video scene, you are to generate Manim code that will create an animation for the scene. The code should be able to run without errors.

Try to be creative in your visualization of the topic. The scene should be engaging and informative. ONLY generate and return the manim code. Nothing else. Not even markdown or the programming language name

The classname of the root animation should always be VideoScene.
"""

SYSTEM_TRANSCRIPTION_PROMPT = """
You are an expert teacher of topics, similar to 3 Blue 1 Brown. Given a user's question about a topic, you are to generate a transcript for a video that will explain the topic.

If needed, you should chunk it up into multiple scenes, in a logical order to best explain the topic. The transcript should be engaging and informative, and you should not have more than 5 scenes.

ONLY Generate an array of strings, where each string is a scene transcription. START and END the array with square brackets. Each element in the array should be a string surrounded by double quotes. Do not include the programming language name or any markdown.

Format example:

[
    "This is the first scene",
    "This is the second scene",
    ...
]

"""

# 480p15 is the resolution and frame rate of the video, change if we want to change the resolution
VIDEO_INTERNAL_PATH = "videos/video/480p15/video.mp4"

class TranscriptGenerator:
    """
    Initializes the TranscriptGenerator with the given user topic
    :param user_topic: User topic (string)
    """
    def __init__(self):
        self.scene_transcriptions = []
    
    def populate_transcriptions_array(self, transcriptions):
        """
        Populates the scene_transcriptions array
        """
        transcriptions_split_left = '[' + '['.join(transcriptions.split('[')[1:])
        transcriptions_split_right = ']'.join(transcriptions_split_left.split(']')[:-1]) + ']'
        self.scene_transcriptions = list(json.loads(transcriptions_split_right))
        return



    def generate_transcript(self, user_topic):
        """
        Generates the transcript for the user topic
        :return: List of scene transcriptions (strings)
        """
        iteration = 0
        messages = [{
            "role": "system", "content": SYSTEM_TRANSCRIPTION_PROMPT
        }, {
            "role": "user", "content": user_topic
        }]

        while iteration < MAX_ITERATIONS:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=round(iteration/MAX_ITERATIONS, 1) # temperature increase heuristic
            )            
            output = response.choices[0].message.content.strip("```")

            logger.info(f"Generated transcript: {output}")

            messages.append({"role": "assistant", "content": output})
            try:
                self.scene_transcriptions = list(json.loads(output))
                return
            except Exception as e:
                try:
                    self.populate_transcriptions_array(output)
                    return 
                except Exception as e:
                    messages.append({"role": "user", "content": f"Error: Did not follow correct format. Please create an array of strings for scenes."})
            iteration += 1


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
        command = f"manim render -ql {GENERATIONS_PATH}/{self.video_id}/{scene_id}/video.py -o video --media_dir {GENERATIONS_PATH}/{self.video_id}/{scene_id}"
        
        print(f"Running command: {command}")

        try:
            # Use subprocess.run instead of os.system
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info(f"Command output: {result.stdout}")
            return True, ""
        except subprocess.CalledProcessError as e:
            # Capture the error output
            error_message = e.stderr.strip()
            return False, f"Command failed with exit code {e.returncode}. Error: {error_message}"
        except Exception as e:
            # Catch any other exceptions
            return False, str(e)
        

    def add_audio_to_scene(self, scene_id):
        """
        Adds audio to the scene with the given scene id
        :param scene_id: Scene id (string)
        """

        # Step 1: Create audio with tts api

        # Step 2: Add audio to scene

        # Step 3: Profit
        

    def generate_scene(self, scene_transcription):
        """
        Generates manim code from the scene description
        :param scene_description: Scene description (string)
        :return: scene_id (string)
        """
        iteration = 0
        messages = [{
            "role": "system", "content": SYSTEM_SCENE_PROMPT
        }, {
            "role": "user", "content": scene_transcription
        }]

        # create scene id
        scene_id = str(uuid.uuid4())

        while iteration < MAX_ITERATIONS:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            logger.info(f"Generated response: {response}")
            
            # get output from last message
            output = response.choices[0].message.content

            # strip code block markdown
            output = output.strip("```")

            logger.info(f"Generated code: {output}")

            # append output to messages
            messages.append({"role": "assistant", "content": output})

            # put code in a file
            try:
                if not os.path.exists(f"{GENERATIONS_PATH}/{self.video_id}/{scene_id}"):
                    os.makedirs(f"{GENERATIONS_PATH}/{self.video_id}/{scene_id}")
                with open(f"{GENERATIONS_PATH}/{self.video_id}/{scene_id}/video.py", "w") as f:
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

        for scene_transcription in self.scene_transcriptions:
            scene_id = self.generate_scene(scene_transcription)
            if scene_id is None:
                logger.error(f"Scene could not be generated for: {scene_transcription}")
                continue

            scene_path = f"{GENERATIONS_PATH}/{self.video_id}/{scene_id}/{VIDEO_INTERNAL_PATH}"
            if os.path.exists(scene_path):
                video_clips.append(VideoFileClip(scene_path))
                scene_ids.append(scene_id)
            else:
                logger.error(f"Video file does not exist at path: {scene_path}")

        if not video_clips:
            logger.error("No scenes were successfully generated.")
            return None

        final_video = concatenate_videoclips(video_clips)
        final_video_path = f"{GENERATIONS_PATH}/{self.video_id}/final_video.mp4"
        final_video.write_videofile(final_video_path, codec="libx264")

        logger.info(f"Final video path: {final_video_path}")
        return final_video_path
        

        
if __name__ == "__main__":
    # example usage for transcript generation
    user_topic = input("Enter user topic: ")
    transcript_generator = TranscriptGenerator()
    transcript_generator.generate_transcript(user_topic)
    logger.info(transcript_generator.scene_transcriptions)
