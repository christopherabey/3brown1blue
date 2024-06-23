import dotenv
dotenv.load_dotenv()

import uuid
from client import client
from logger import logger
import os
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip, ImageClip, CompositeVideoClip
from moviepy.audio.AudioClip import AudioClip
from speech import speech_client
import json
import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor


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

Two elements should not be in the same location at the same time. Ensure that every asset you use is defined in the file, and that the file can be run without errors.

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
            output = response.choices[0].message.content.strip().strip('python').strip("```")

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
        self.scene_transcriptions = {uuid.uuid4(): scene_transcription for scene_transcription in scene_transcriptions}
        self.video_id = str(uuid.uuid4())

    def get_scene_path(self, scene_id, video_id):
        return f"{GENERATIONS_PATH}/{video_id}/{scene_id}/{VIDEO_INTERNAL_PATH}"
    
    def get_audio_path(self, scene_id, video_id):
        return f"{GENERATIONS_PATH}/{video_id}/{scene_id}/audio.wav"
        
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
        

    async def generate_speech(self, scene_id, video_id):
        """
        Generates speech for the scene with the given scene id
        :param scene_id: Scene id (string)
        :param video_id: Video id (string)
        """
        scene_transcription = self.scene_transcriptions[scene_id]
        synthesis = await speech_client.synthesize(scene_transcription, voice='lily', format='wav')
        audio_path = f"{GENERATIONS_PATH}/{video_id}/{scene_id}/audio.wav"
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(synthesis['audio'])
        
        logger.info(f"Successfully generated speech for scene {scene_id}")
        return scene_id
        
            

    def generate_manim(self, scene_id):
        """
        Generates manim code from the scene description
        :param scene_description: Scene description (string)
        :return: scene_id (string)
        """
        iteration = 0
        scene_transcription = self.scene_transcriptions[scene_id]
        messages = [{
            "role": "system", "content": SYSTEM_SCENE_PROMPT
        }, {
            "role": "user", "content": scene_transcription
        }]

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
                return scene_id
            
            # scene was not rendered successfully
            # add error message to messages
            messages.append({"role": "user", "content": f"Error: {render_output[1]}"})
            iteration += 1
            
        # scene was not rendered successfully after MAX_ITERATIONS
        return None
    
    def combine_manim_and_speech(self, scene_id, video_id):
        """
        Combines the manim code and speech synthesis for the scene with the given scene id
        :param scene_id: Scene id (string)
        :param manim_result: Manim code (string)
        :param speech_result: Speech synthesis (string)
        """
        scene_path = self.get_scene_path(scene_id, video_id)
        audio_path = self.get_audio_path(scene_id, video_id)

        video = VideoFileClip(scene_path)
        audio = AudioFileClip(audio_path)

        # Get durations
        video_duration = video.duration
        audio_duration = audio.duration

        logger.info(f"Video duration: {video_duration}, Audio duration: {audio_duration}")

        # If audio is shorter than video, append silence
        if audio_duration < video_duration:
            silence_duration = video_duration - audio_duration
            silence = AudioClip(lambda t: 0, duration=silence_duration)
            audio = CompositeAudioClip([audio, silence.set_start(audio_duration)])
        
        # If audio is longer than video, extend the video by holding the last frame
        elif audio_duration > video_duration:
            logger.warning("Audio is longer than video, extending video by holding the last frame")
            last_frame = video.get_frame(video_duration - 0.1)
            frozen_clip = ImageClip(last_frame).set_duration(audio_duration - video_duration)
            video = CompositeVideoClip([video, frozen_clip.set_start(video_duration)])
            video = video.set_duration(audio_duration)

        # Ensure both clips have the same duration
        final_duration = min(video.duration, audio.duration)
        video = video.subclip(0, final_duration)
        audio = audio.subclip(0, final_duration)

        # Composite the video with the audio
        final_clip = video.set_audio(audio)

        # Write the final video with audio
        # wipe scene file
        os.remove(scene_path)

        final_clip.write_videofile(scene_path, codec="libx264")

        # Step 3: Profit
        # Close the clips to free up system resources
        video.close()
        audio.close()
        final_clip.close()

        logger.info(f"Successfully added audio to scene {scene_id}")

    def combine_video_scenes(self):
        """
        Combines all the video scenes into a single video
        """
        scene_ids = []
        video_clips = []

        for scene_id in self.scene_transcriptions.keys():
            scene_path = self.get_scene_path(scene_id, self.video_id)
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

    async def generate_all_scenes(self):
        """
        Generates manim code for all scenes and stitches them together into a single video.
        :return: Path to the final stitched video.
        """
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            loop = asyncio.get_running_loop()
            tasks = []
            for scene_id in self.scene_transcriptions.keys():
                # Use run_in_executor for potentially CPU-bound tasks
                manim_task = loop.run_in_executor(executor, self.generate_manim, scene_id)
                speech_task = loop.run_in_executor(executor, self.generate_speech, scene_id, self.video_id)
                tasks.append((manim_task, speech_task, scene_id))

                # Wait for all tasks to complete
            results = await asyncio.gather(*(asyncio.gather(*task_pair[:2]) for task_pair in tasks))
        
            logger.info(f"Results: {results}")

            for (manim_result, speech_result), scene_id in zip(results, self.scene_transcriptions.keys()):
                if manim_result is None or speech_result is None:
                    logger.error(f"Scene {scene_id} was not generated successfully")
                    continue
                self.combine_manim_and_speech(scene_id, self.video_id)

            self.combine_video_scenes()
        

        
if __name__ == "__main__":
    # example usage for transcript generation
    user_topic = input("Enter user topic: ")
    transcript_generator = TranscriptGenerator()
    transcript_generator.generate_transcript(user_topic)
    logger.info(transcript_generator.scene_transcriptions)
