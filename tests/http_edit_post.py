import re
import requests

BASE = 'http://127.0.0.1:8000'
LOGIN_URL = BASE + '/forms/login/'
EDIT_URL = BASE + '/forms/editar-termo/6/'

s = requests.Session()
# get login page to extract csrf
r = s.get(LOGIN_URL)
csrftoken = re.search(r"name='csrfmiddlewaretoken' value='(.+?)'", r.text)
if csrftoken:
    token = csrftoken.group(1)
else:
    print('no csrf token on login page')
    token = ''

login_data = {
    'username': 'edit_test_user',
    'password': 'pass',
    'csrfmiddlewaretoken': token,
}
headers = {'Referer': LOGIN_URL}
resp = s.post(LOGIN_URL, data=login_data, headers=headers)
print('login status', resp.status_code)

# GET edit page to obtain management form fields
r2 = s.get(EDIT_URL)
print('edit GET status', r2.status_code)
# find management form fields if present
m_total = re.search(r"name=['\"]form-TOTAL_FORMS['\"] value=['\"](\d+)['\"]", r2.text)
m_initial = re.search(r"name=['\"]form-INITIAL_FORMS['\"] value=['\"](\d+)['\"]", r2.text)
# prepare post data
post_data = {
    'nome_termo': 'Termo6 edited via HTTP',
    'descricao': 'edited desc',
    'categoria': 'CatTest',
    'subcategoria': 'SubTest',
    'carrossel': 'on',
    'csrfmiddlewaretoken': re.search(r"name='csrfmiddlewaretoken' value='(.+?)'", r2.text).group(1) if re.search(r"name='csrfmiddlewaretoken' value='(.+?)'", r2.text) else '',
}
if m_total:
    post_data['form-TOTAL_FORMS'] = m_total.group(1)
else:
    post_data['form-TOTAL_FORMS'] = '0'
if m_initial:
    post_data['form-INITIAL_FORMS'] = m_initial.group(1)
else:
    post_data['form-INITIAL_FORMS'] = '0'
post_data['form-MIN_NUM_FORMS'] = '0'
post_data['form-MAX_NUM_FORMS'] = '1000'

resp2 = s.post(EDIT_URL, data=post_data, headers={'Referer': EDIT_URL})
print('edit POST status', resp2.status_code)
print('edit POST redirected?', resp2.history)
print('response length', len(resp2.text))
