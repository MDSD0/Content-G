from typing import Optional
import tempfile
import os
import re
import subprocess
from moviepy import concatenate_videoclips, VideoFileClip

def run_manim_code_combined(code: str, output_file: Optional[str] = "output.mp4") -> str:
    """
    Runs the specified Manim code, generates animations for all Scene classes,
    combines them into one video, and saves the final output in the current directory.
    """


    print("Received Manim Code:")
    print(code)

    # Extract all Scene classes
    scene_classes = re.findall(r"class\s+(\w+)\(Scene\):", code)
    if not scene_classes:
        return "Error: Manim code must contain at least one class inheriting from Scene."
    print("Detected Scene Classes:", scene_classes)

    # Use a temporary directory for execution
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "temp_manim_script.py")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Save the Manim code to a temporary file
            with open(temp_file_path, "w") as file:
                file.write(code)

            # Check if Manim is installed and accessible
            manim_check = subprocess.run(
                ["manim", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if manim_check.returncode != 0:
                return f"Error: Manim is not installed or not accessible.\n{manim_check.stderr}"

            # Render each Scene class separately
            video_clips = []
            for scene_class in scene_classes:
                result = subprocess.run(
                    ["manim", temp_file_path, scene_class, "-ql", "--media_dir", output_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if result.returncode != 0:
                    return f"Error while generating animation for {scene_class}:\n{result.stderr}"

                # Locate the generated video file
                generated_video_path = None
                for root, _, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith(".mp4") and scene_class in file:
                            generated_video_path = os.path.join(root, file)
                            break
                    if generated_video_path:
                        break

                if not generated_video_path:
                    return f"Error: Animation for {scene_class} generated but output file not found."

                # Load the video into MoviePy for combining
                video_clips.append(VideoFileClip(generated_video_path))

            # Combine all video clips into one
            final_video = concatenate_videoclips(video_clips)
            final_video_path = os.path.join(os.getcwd(), output_file)
            final_video.write_videofile(final_video_path, codec="libx264")

            return f"Combined animation generated and saved as '{output_file}'."

        except Exception as e:
            return f"Error: {str(e)}"

def test_run_manim_code_combined():
    # Sample Manim code with multiple Scene classes
    sample_manim_code = """
from manim import *

class SceneOne(Scene):
    def construct(self):
        text = Text("Scene One")
        self.play(Write(text))
        self.wait(1)

class SceneTwo(Scene):
    def construct(self):
        text = Text("Scene Two", color=BLUE)
        self.play(Write(text))
        self.wait(1)

class SceneThree(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait(1)
    """

    # Output file name
    output_file = "test_combined_animation.mp4"

    # Call the function and capture the result
    result = run_manim_code_combined(sample_manim_code, output_file)

    # Print the result
    print(result)

    # Verify the output
    if "Combined animation generated" in result:
        print(f"Test passed: {output_file} successfully created.")
    else:
        print("Test failed.")

# Run the test
if __name__ == "__main__":
    test_run_manim_code_combined()

