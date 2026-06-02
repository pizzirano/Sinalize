from django.test import Client
from django.contrib.auth.models import User
from catalog.models import Termo, Video, Dominio

u, _ = User.objects.get_or_create(username='edit_test_user')
# ensure password
u.set_password('pass')
u.save()

# ensure dominio
if not Dominio.objects.filter(pk=1).exists():
    Dominio.objects.create(pk=1, nome_dominio='Turismo')

# ensure termo 6
if not Termo.objects.filter(id_termo=6).exists():
    Termo.objects.create(id_termo=6, nome_termo='Termo6', descricao='desc', status='PENDING', created_by=u)

c = Client()
c.force_login(u)

# Prepare minimal POST data to trigger validation and logs
# Use same field names as in template/form
post_data = {
    'nome_termo': 'Termo6 edited',
    'descricao': 'edited desc',
    'categoria': 'CatTest',
    'subcategoria': 'SubTest',
    'carrossel': 'on',
    # formset management fields (no forms)
    'form-TOTAL_FORMS': '0',
    'form-INITIAL_FORMS': '0',
    'form-MIN_NUM_FORMS': '0',
    'form-MAX_NUM_FORMS': '1000',
}

resp = c.post('/forms/editar-termo/6/', post_data, follow=True)
print('POST status', resp.status_code)
print('redirect chain', resp.redirect_chain)
if hasattr(resp, 'context') and resp.context:
    termo_form = resp.context.get('termo_form')
    formset = resp.context.get('formset')
    print('termo_form errors:', termo_form.errors)
    print('formset errors:', formset.errors)
else:
    print('No context')
