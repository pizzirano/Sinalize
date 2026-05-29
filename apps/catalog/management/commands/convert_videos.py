from django.core.management.base import BaseCommand
from catalog.models import Video
from catalog.utils import convert_video_to_mp4
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Converte vídeos pendentes para mp4'

    def handle(self, *args, **options):
        pendentes = Video.objects.filter(
            convertido=False,
            status='PENDING'
        )
        self.stdout.write(f'{pendentes.count()} vídeos para converter')

        for video in pendentes:
            if not video.video:
                self.stdout.write(f'  ✗ {video.titulo} (sem arquivo associado)')
                continue

            input_path = os.path.join(settings.MEDIA_ROOT, video.video.name)
            output_path = convert_video_to_mp4(input_path)
            if output_path:
                video.video.name = os.path.relpath(
                    output_path, settings.MEDIA_ROOT
                )
                video.convertido = True
                video.save(update_fields=['video', 'convertido'])
                self.stdout.write(f'  ✓ {video.titulo}')
            else:
                self.stdout.write(f'  ✗ {video.titulo} (erro na conversão)')
