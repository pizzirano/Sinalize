import os
import subprocess


def convert_video_to_mp4(input_path):
    if not os.path.exists(input_path):
        return None, 'Arquivo inexistente'

    base, _ext = os.path.splitext(input_path)
    output_path = base + '.mp4'

    if input_path.lower().endswith('.mp4'):
        return input_path, ''

    try:
        subprocess.run(
            [
                'ffmpeg',
                '-y',
                '-i',
                input_path,
                '-vcodec',
                'libx264',
                '-acodec',
                'aac',
                output_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        return None, str(exc)
    except subprocess.CalledProcessError as exc:
        return None, (exc.stderr or exc.stdout or str(exc)).strip()

    if os.path.exists(output_path):
        os.remove(input_path)
        return output_path, ''

    return None, 'ffmpeg terminou sem gerar o arquivo MP4'
