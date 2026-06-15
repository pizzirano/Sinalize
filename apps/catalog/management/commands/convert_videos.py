import os

from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.models import Video
from catalog.utils import convert_video_to_mp4


class Command(BaseCommand):
    help = 'Converte para MP4 todos os videos ainda nao convertidos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Lista os videos elegiveis sem executar a conversao.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        videos = Video.objects.filter(convertido=False).exclude(video='')
        self.stdout.write(f'{videos.count()} videos para converter')

        for video in videos:
            if not video.video:
                self.stdout.write(f'  X {video.titulo} (sem arquivo associado)')
                continue

            input_path = os.path.join(settings.MEDIA_ROOT, video.video.name)
            if not os.path.exists(input_path):
                self.stdout.write(
                    f'  X {video.titulo} (arquivo inexistente: {video.video.name})'
                )
                continue

            if dry_run:
                self.stdout.write(
                    f'  - {video.titulo} ({video.status}, {video.video.name})'
                )
                continue

            output_path, error = convert_video_to_mp4(input_path)
            if output_path:
                video.video.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
                video.convertido = True
                video.save(update_fields=['video', 'convertido'])
                self.stdout.write(f'  OK {video.titulo} -> {video.video.name}')
            else:
                self.stdout.write(f'  X {video.titulo} (erro na conversao)')
                if error:
                    self.stderr.write(error)
