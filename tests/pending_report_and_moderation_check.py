from django.test import Client
from django.contrib.auth.models import User
from catalog.models import Termo, Video, Profile

print('Termos PENDING:', Termo.objects.filter(status='PENDING').count())
print('Videos PENDING:', Video.objects.filter(status='PENDING').count())
for t in Termo.objects.filter(status='PENDING'):
    print(f'  Termo id={t.id_termo} | {t.nome_termo} | by={getattr(t.created_by, "username", None)}')
    for v in t.videos.filter(status='PENDING'):
        print(f'    Video id={v.id_video} | {v.titulo}')

# Ensure moderator user exists
mod_user, created = User.objects.get_or_create(username='mod_check_user')
if created:
    mod_user.set_password('modpass')
    mod_user.save()
# Ensure profile exists and role set
prof, _ = Profile.objects.get_or_create(user=mod_user)
prof.role = 'MODERATOR'
prof.save()

c = Client()
c.force_login(mod_user)
resp = c.get('/catalog/moderacao/')
content = resp.content.decode('utf-8')
found_all = True
for t in Termo.objects.filter(status='PENDING'):
    if t.nome_termo not in content:
        found_all = False
for v in Video.objects.filter(status='PENDING'):
    if v.titulo not in content:
        found_all = False
print('MODERATION_PAGE_SHOWS_PENDING:', found_all)
