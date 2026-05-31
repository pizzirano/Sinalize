# Scripts de Teste e Debug — Sinalize PR3

Scripts utilitários criados durante o desenvolvimento da PR3.
Execute sempre com: docker compose exec projeto python manage.py shell < tests/<script>.py

## Scripts disponíveis
- create_orm_videos.py — Cria um `Termo` e dois `Video` via ORM para testes locais (usuário `orquestrador_test`).
- curl_edit.sh — Script `curl` para login e submissão de edição de termo (útil para testes HTTP simples).
- http_edit_post.py — Usa `requests` para efetuar login e postar uma edição de termo (teste de fluxo HTTP programático).
- moderation_check.py — Usa `django.test.Client` para verificar se a página de moderação exibe os termos/vídeos esperados.
- pending_report_and_moderation_check.py — Verifica contagens de termos/vídeos PENDING e testa se a página de moderação mostra os itens pendentes.
- trigger_edit_post.py — Usa `django.test.Client` para forçar um POST de edição no termo 6 (gera logs/erros para debug).
- validate_consistency.py — Varre o banco procurando `Termo` APPROVED que ainda tenham `Video` PENDING.
