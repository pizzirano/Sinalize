#!/bin/sh
# Login
curl -s -c /tmp/cookies 'http://127.0.0.1:8000/forms/login/' -o /tmp/login.html
TOKEN=$(grep -o "name='csrfmiddlewaretoken' value='[^']*'" /tmp/login.html | sed "s/.*value='\([^']*\)'.*/\1/")
echo TOKEN1:$TOKEN
curl -s -b /tmp/cookies -c /tmp/cookies -X POST -d "username=edit_test_user&password=pass&csrfmiddlewaretoken=${TOKEN}" -H "Referer: http://127.0.0.1:8000/forms/login/" http://127.0.0.1:8000/forms/login/ -o /tmp/login_resp.html

# GET edit page
curl -s -b /tmp/cookies 'http://127.0.0.1:8000/forms/editar-termo/6/' -o /tmp/edit.html
TOKEN2=$(grep -o "name='csrfmiddlewaretoken' value='[^']*'" /tmp/edit.html | sed "s/.*value='\([^']*\)'.*/\1/")
TOTAL=$(grep -o "name='form-TOTAL_FORMS' value='[0-9]*'" /tmp/edit.html | sed "s/.*value='\([0-9]*\)'.*/\1/")
echo TOKEN2:$TOKEN2
echo TOTAL:$TOTAL

# POST edit
curl -s -b /tmp/cookies -X POST -d "nome_termo=Termo6+curl&descricao=desc&categoria=Cat&subcategoria=Sub&carrossel=on&csrfmiddlewaretoken=${TOKEN2}&form-TOTAL_FORMS=${TOTAL}&form-INITIAL_FORMS=0&form-MIN_NUM_FORMS=0&form-MAX_NUM_FORMS=1000" -H "Referer: http://127.0.0.1:8000/forms/editar-termo/6/" http://127.0.0.1:8000/forms/editar-termo/6/ -i -o /tmp/post_resp.html

cat /tmp/post_resp.html | head -c 1000
