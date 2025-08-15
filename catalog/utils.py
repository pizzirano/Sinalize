import os
import subprocess
from django.conf import settings

def convert_video_to_mp4(input_path):
    if not os.path.exists(input_path):
        print(f"Arquivo de entrada não encontrado: {input_path}")
        return None

    base, ext = os.path.splitext(input_path)
    output_path = base + '.mp4'

    # Se já for mp4, não faz nada
    if input_path.lower().endswith('.mp4'):
        return input_path

    try:
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-vcodec', 'libx264', '-acodec', 'aac',
            output_path
        ], check=True)

        # Remove o original, só mantém o .mp4
        if os.path.exists(output_path):
            os.remove(input_path)
            return output_path
    except Exception as e:
        print(f"Erro ao converter vídeo: {e}")

    return None