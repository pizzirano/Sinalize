import os
import subprocess
from django.conf import settings

def convert_video_to_mp4(input_path: str) -> str | None:
    """Convert a MOV video file to MP4 using ffmpeg.

    Args:
        input_path: Absolute path to the source MOV file.
    Returns:
        The absolute path to the converted MP4 file, or None if conversion failed.
    """
    if not os.path.isfile(input_path):
        return None
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}.mp4"
    # Run ffmpeg; suppress output for brevity
    cmd = ["ffmpeg", "-i", input_path, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", output_path]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError:
        return None
