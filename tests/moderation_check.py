from django.test import Client
from django.contrib.auth.models import User
from catalog.models import Termo, Video

mod, created = User.objects.get_or_create(username='mod_test')
if created:
    mod.set_password('modpass')
    mod.save()

# ensure profile exists
from catalog.models import Profile
Profile.objects.get_or_create(user=mod)
mod.profile.role = 'MODERATOR'
mod.profile.save()

c = Client()
# force login as moderator
c.force_login(mod)
resp = c.get('/catalog/moderacao/')
print('status', resp.status_code)
content = resp.content.decode('utf-8')
print('contains termo:', 'Criado via ORM' in content)
print('contains ORM1:', 'ORM1' in content)
print('contains ORM2:', 'ORM2' in content)
print('contains Pendente:', 'Pendente' in content or '⏳' in content or 'PENDING' in content)
