from catalog.models import Termo, Video

print('=== Consistencia termo/video ===')
issues = []
for t in Termo.objects.filter(status='APPROVED'):
    pending_videos = t.videos.filter(status='PENDING').count()
    if pending_videos:
        issues.append(f'PROBLEMA: Termo {t.id_termo} APPROVED mas tem {pending_videos} video(s) PENDING')

if issues:
    for issue in issues:
        print(issue)
else:
    print('Nenhum problema encontrado.')

print('Verificacao concluida.')
