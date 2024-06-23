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
import asyncio


"""
Takes in generated scene transcriptions, then generates manim animation and according text-to-speech for each scene, then stitches it together to create a full video.

To generate manim animation, it uses LLMs to generate manim code from the scene descriptions. When generating a scene, it generates the code, then tries to run it. If it fails, it feeds the generated code + error message to the LLM to regenerate the code. This process is repeated until the code runs successfully with a max of 5 tries.

Saves videos in generated_videos folder, and returns the id of the video.
"""

GENERATIONS_PATH = "generated"

MAX_ITERATIONS = 5

SYSTEM_SCENE_PROMPT = """
You are an expert teacher of simple and complex topics, similar to 3 Blue 1 Brown. Given a transcription for a video scene, you are to generate Manim code that will create an animation for the scene. The code should be able to run without errors. The file will be run with the manim cli tool.

- Be creative in your visualization of the topic. 
- The scene should be engaging and informative. ONLY generate and return the manim code. Nothing else. Not even markdown or the programming language name
- DO NOT FADE OUT AT THE END
- Do not overlay multiple objects at the same approximate position at the same time. Everything should be clearly visible.
- Remember that the color BROWN is not defined
- All elements should be inside the bounds of the video
- Make sure that all the functions you use exist and are imported
- Match the length of the animation to the length of the transcription. If it is a long transcription, it should be a long animation
- PAY SPECIAL ATTENTION TO THE POSITION AND SIZE OF THE ELEMENTS. Make use of Manim's positioning and alignment features so that elements are properly contained within or relative to each other.
- If you are using ANY assets, such as SVGs, you need to create it yourself from scratch from the python code you generate, as that is all that will be run.
- The classname of the root animation should always be VideoScene.

EXAMPLES:
"Bananas are an odd fruit. They are berries, but strawberries are not. They are also a herb, not a fruit. Bananas are a great source of potassium."
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Title
        title = Text("Bananas: An Odd Fruit", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Bananas are berries
        berry_text = Text("Bananas are berries,", font_size=36).shift(UP*2)
        strawberry_text = Text("but strawberries are not.", font_size=36).next_to(berry_text, DOWN)
        self.play(Write(berry_text))
        self.play(Write(strawberry_text))
        self.wait(2)

        # Bananas are herbs
        herb_text = Text("They are also a herb,", font_size=36).shift(DOWN*0.5)
        not_fruit_text = Text("not a fruit.", font_size=36).next_to(herb_text, DOWN)
        self.play(Write(herb_text))
        self.play(Write(not_fruit_text))
        self.wait(2)

        # Bananas are a great source of potassium
        potassium_text = Text("Bananas are a great source of potassium.", font_size=36).shift(DOWN*2.5)
        self.play(Write(potassium_text))
        self.wait(2)

        # Adding images for better visualization
        banana_image = self.create_banana().scale(0.5).to_edge(LEFT)
        strawberry_image = self.create_strawberry().scale(0.5).to_edge(RIGHT)
        self.play(FadeIn(banana_image), FadeIn(strawberry_image))
        self.wait(2)

        # Highlighting potassium
        potassium_chemical = Text("K", font_size=48, color=YELLOW).next_to(potassium_text, RIGHT)
        self.play(Indicate(potassium_text), FadeIn(potassium_chemical))
        self.wait(2)

        # End scene
        self.play(FadeOut(title), FadeOut(berry_text), FadeOut(strawberry_text), FadeOut(herb_text), 
                  FadeOut(not_fruit_text), FadeOut(potassium_text), FadeOut(banana_image), FadeOut(strawberry_image), 
                  FadeOut(potassium_chemical))
        self.wait(1)

    def create_banana(self):
        banana = VGroup()
        banana.add(
            Polygon(
                [0, 0, 0], [2, 1, 0], [1, 3, 0], [-1, 3, 0], [-2, 1, 0],
                color=YELLOW, fill_opacity=1, stroke_color=BLACK
            )
        )
        return banana

    def create_strawberry(self):
        strawberry = VGroup()
        strawberry.add(
            Polygon(
                [0, 0, 0], [1, 2, 0], [0.5, 3, 0], [-0.5, 3, 0], [-1, 2, 0],
                color=RED, fill_opacity=1, stroke_color=BLACK
            )
        )
        strawberry.add(
            Polygon(
                [0, 3, 0], [0.5, 3.5, 0], [1, 3, 0],
                color=GREEN, fill_opacity=1, stroke_color=BLACK
            )
        )
        return strawberry


"Sine is an unintuitive math thing that people take as fact, but we can see it is a fundamental property of a circle."

from manim import *

class SineCurveUnitCircle(Scene):
    # contributed by heejin_park, https://infograph.tistory.com/230
    def construct(self):
        self.show_axis()
        self.show_circle()
        self.move_dot_and_draw_curve()
        self.wait()

    def show_axis(self):
        x_start = np.array([-6,0,0])
        x_end = np.array([6,0,0])

        y_start = np.array([-4,-2,0])
        y_end = np.array([-4,2,0])

        x_axis = Line(x_start, x_end)
        y_axis = Line(y_start, y_end)

        self.add(x_axis, y_axis)
        self.add_x_labels()

        self.origin_point = np.array([-4,0,0])
        self.curve_start = np.array([-3,0,0])

    def add_x_labels(self):
        x_labels = [
            MathTex("\pi"), MathTex("2 \pi"),
            MathTex("3 \pi"), MathTex("4 \pi"),
        ]

        for i in range(len(x_labels)):
            x_labels[i].next_to(np.array([-1 + 2*i, 0, 0]), DOWN)
            self.add(x_labels[i])

    def show_circle(self):
        circle = Circle(radius=1)
        circle.move_to(self.origin_point)
        self.add(circle)
        self.circle = circle

    def move_dot_and_draw_curve(self):
        orbit = self.circle
        origin_point = self.origin_point

        dot = Dot(radius=0.08, color=YELLOW)
        dot.move_to(orbit.point_from_proportion(0))
        self.t_offset = 0
        rate = 0.25

        def go_around_circle(mob, dt):
            self.t_offset += (dt * rate)
            # print(self.t_offset)
            mob.move_to(orbit.point_from_proportion(self.t_offset % 1))

        def get_line_to_circle():
            return Line(origin_point, dot.get_center(), color=BLUE)

        def get_line_to_curve():
            x = self.curve_start[0] + self.t_offset * 4
            y = dot.get_center()[1]
            return Line(dot.get_center(), np.array([x,y,0]), color=YELLOW_A, stroke_width=2 )


        self.curve = VGroup()
        self.curve.add(Line(self.curve_start,self.curve_start))
        def get_curve():
            last_line = self.curve[-1]
            x = self.curve_start[0] + self.t_offset * 4
            y = dot.get_center()[1]
            new_line = Line(last_line.get_end(),np.array([x,y,0]), color=YELLOW_D)
            self.curve.add(new_line)

            return self.curve

        dot.add_updater(go_around_circle)

        origin_to_circle_line = always_redraw(get_line_to_circle)
        dot_to_curve_line = always_redraw(get_line_to_curve)
        sine_curve_line = always_redraw(get_curve)

        self.add(dot)
        self.add(orbit, origin_to_circle_line, dot_to_curve_line, sine_curve_line)
        self.wait(8.5)

        dot.remove_updater(go_around_circle)

"Finally, let's wrap up with some practical tips. One common approach to troubleshoot CORS issues is to use debugging tools in your browser that show you what headers are being sent and received. Additionally, for development and testing purposes, there are browser extensions that disable CORS, but remember, these should not be used in production environments. On the screen, we show an example of inspecting network requests in a browser's developer tools, highlighting the 'Origin' and 'Access-Control-Allow-Origin' headers. By understanding CORS and setting the correct headers on your server, you'll save yourself a lot of headaches and keep your web applications running smoothly. Thanks for joining me today, and happy coding!"

from manim import *

class VideoScene(Scene):
    def construct(self):
        # Title
        title = Text("Practical Tips for Troubleshooting CORS Issues", font_size=40).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Debugging tools
        debugging_tools_text = Text("Use Browser Debugging Tools", font_size=32).next_to(title, DOWN, buff=0.5)
        self.play(Write(debugging_tools_text))
        self.wait(1)

        # Showing Headers
        headers_text = Text("Inspect Network Requests", font_size=32).next_to(debugging_tools_text, DOWN, buff=0.5)
        self.play(Write(headers_text))
        self.wait(1)

        browser_image = self.create_browser().next_to(headers_text, DOWN, buff=0.5)
        self.play(FadeIn(browser_image))
        self.wait(1)

        origin_header = Text("Origin", font_size=20, color=YELLOW).next_to(browser_image, LEFT, buff=0.5)
        allow_origin_header = Text("Access-Control-Allow-Origin", font_size=20, color=GREEN).next_to(browser_image, RIGHT, buff=0.5)
        self.play(Write(origin_header), Write(allow_origin_header))
        self.wait(2)

        # Debugging disclaimer
        disclaimer = Text("Use CORS Disable Extensions Only for Development and Testing", font_size=28).next_to(browser_image, DOWN, buff=1)
        self.play(Write(disclaimer))
        self.wait(2)

        # End Scene
        thanks_text = Text("Thanks for joining me today,\nand happy coding!", font_size=36).next_to(disclaimer, DOWN, buff=1)
        self.play(Write(thanks_text))
        self.wait(3)

    def create_browser(self):
        browser = VGroup()
        
        # Browser window outline
        outline = Rectangle(width=10, height=6, color=WHITE)
        address_bar = Rectangle(width=9.5, height=0.5, color=BLUE).shift(UP*2.3)
        
        # Address bar elements
        address_text = Text("http://localhost", font_size=20, color=WHITE).move_to(address_bar.get_center())
        
        # Network panel
        network_panel = Rectangle(width=9.5, height=4.5, color=GRAY).shift(DOWN*0.75)
        
        # Header examples
        origin_header_example = Text("Origin: http://example.com", font_size=18, color=YELLOW).move_to(network_panel.get_center()).shift(UP*1.5)
        allow_origin_header_example = Text("Access-Control-Allow-Origin: *", font_size=18, color=GREEN).move_to(network_panel.get_center())
        
        browser.add(outline, address_bar, address_text, network_panel, origin_header_example, allow_origin_header_example)
        return browser
"""

VOICE_ID = "7d21119e-bb5d-4416-8164-9170ec4952c2"
# VOICE_ID = "caleb"

# 480p15 is the resolution and frame rate of the video, change if we want to change the resolution
VIDEO_INTERNAL_PATH = "videos/video/480p15/video.mp4"

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
        synthesis = await speech_client.synthesize(scene_transcription, voice=VOICE_ID, format='wav', temperature=0.3)
        audio_path = f"{GENERATIONS_PATH}/{video_id}/{scene_id}/audio.wav"
        # if audio path does not exist, create it
        if not os.path.exists(f"{GENERATIONS_PATH}/{video_id}/{scene_id}"):
            os.makedirs(f"{GENERATIONS_PATH}/{video_id}/{scene_id}")
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(synthesis['audio'])
        
        logger.info(f"Successfully generated speech for scene {scene_id}")
        return scene_id
        
            

    async def generate_manim(self, scene_id):
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
            response = await client.chat.completions.create(
                model=os.getenv("LLM_MODEL"),
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
        tasks = []
        for scene_id, transcription in self.scene_transcriptions.items():
            manim_task = asyncio.create_task(self.generate_manim(scene_id))
            speech_task = asyncio.create_task(self.generate_speech(scene_id, self.video_id))
            tasks.append((manim_task, speech_task))

        # Wait for all tasks to complete
        results = await asyncio.gather(*(asyncio.gather(*task_pair[:2]) for task_pair in tasks))

        logger.info(f"Results: {results}")

        for (manim_result, speech_result), scene_id in zip(results, self.scene_transcriptions.keys()):
            if manim_result is None or speech_result is None:
                logger.error(f"Scene {scene_id} was not generated successfully")
                continue
            self.combine_manim_and_speech(scene_id, self.video_id)

        self.combine_video_scenes()
        return self.video_id
        


async def main():
    examples = [
    "Welcome everyone! Today we're diving into a topic that can often be a source of confusion and frustration for web developers: CORS, which stands for Cross-Origin Resource Sharing. Have you ever tried to make a request to another website from your web application and hit a roadblock? That's probably CORS at work. Let's break it down to understand what it is, why it exists, and how to overcome common issues. Before we start, imagine the screen displaying a simple web browser requesting data from a different server, and suddenly a big 'Access Denied' sign appears. That's the essence of why we need to talk about CORS.",
    
    "First, let's discuss the concept of 'origin'. In the context of web browsing, an origin is defined by the scheme (like http or https), the hostname, and the port of a URL. So, http://example.com:80 and https://example.com:443 are considered different origins. Now, CORS is a security feature implemented in browsers to prevent malicious websites from making unauthorized requests to your server. Imagine the screen showing two websites—one labeled 'Your Site' and the other 'Malicious Site'—with arrows indicating various kinds of requests they could make. CORS blocks some of these requests to protect your data and your users.",
    
    "So, how does CORS actually work? When you make an HTTP request to a different origin, the browser sends an additional HTTP header called 'Origin' with the request. The server can then decide whether to allow this request based on that header. If the server allows it, it sends back a response with headers like 'Access-Control-Allow-Origin'. Let's visualize this with a sequence: first, the browser sends a request with an 'Origin' header, and then the server responds with either 'Access Allowed' or 'Access Denied'. This back-and-forth ensures that both sides agree on the rules for data sharing.",
    
    "Now, let's get to the heart of why CORS can be such a headache. Many times, the issue stems from the server not including the proper headers in its response. For example, if your server doesn't include 'Access-Control-Allow-Origin', the browser will block the request, even if the server has the data available. On the screen, we see a frustrated developer looking at an error message in the browser console that says, 'No Access-Control-Allow-Origin header is present'. To fix this, the server needs to add the correct headers. Sometimes it can be as simple as configuring your server to include 'Access-Control-Allow-Origin: *', which allows any origin to access the resource. But be careful, this can open your server to potential risks. For more security, you might specify particular origins that are allowed.",
    
    "Finally, let's wrap up with some practical tips. One common approach to troubleshoot CORS issues is to use debugging tools in your browser that show you what headers are being sent and received. Additionally, for development and testing purposes, there are browser extensions that disable CORS, but remember, these should not be used in production environments. On the screen, we show an example of inspecting network requests in a browser's developer tools, highlighting the 'Origin' and 'Access-Control-Allow-Origin' headers. By understanding CORS and setting the correct headers on your server, you'll save yourself a lot of headaches and keep your web applications running smoothly. Thanks for joining me today, and happy coding!"
]
    sg = SceneGenerator(examples)
    await sg.generate_all_scenes()

if __name__ == "__main__":
    asyncio.run(main())