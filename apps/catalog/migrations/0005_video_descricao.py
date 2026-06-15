from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_video_tipo_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='descricao',
            field=models.TextField(blank=True, verbose_name='Descrição do Vídeo'),
        ),
    ]
