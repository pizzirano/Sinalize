from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from catalog.models import Termo, Video, Dominio

user, created = User.objects.get_or_create(username='orquestrador_test')
if created:
    user.set_password('pass')
    user.save()

if not Dominio.objects.filter(pk=1).exists():
    Dominio.objects.create(pk=1, nome_dominio='Turismo')

termo = Termo.objects.create(nome_termo='Criado via ORM', descricao='desc', status='PENDING', created_by=user)

v1 = Video.objects.create(
    titulo='ORM1',
    tipo_video='Sinal',
    termo=termo,
    video=SimpleUploadedFile('orm1.mp4', b'0'*10, content_type='video/mp4'),
    status='PENDING',
    uploaded_by=user,
    convertido=False
)

v2 = Video.objects.create(
    titulo='ORM2',
    tipo_video='Sinal',
    termo=termo,
    video=SimpleUploadedFile('orm2.mp4', b'1'*10, content_type='video/mp4'),
    status='PENDING',
    uploaded_by=user,
    convertido=False
)

print('Created termo', termo.id_termo)
print('Termos PENDING:', Termo.objects.filter(status='PENDING').count())
print('Videos PENDING:', Video.objects.filter(status='PENDING').count())
v = Video.objects.order_by('-id_video').first()
print('Last video:', {'id': v.id_video, 'status': v.status, 'uploaded_by': getattr(v.uploaded_by, 'username', None)})
