## Objetivo
Fornecer instruções concisas e específicas que ajudem agentes de código a serem produtivos rapidamente neste repositório Django.

## Visão geral rápida (big picture)
- Projeto: monolito Django (apps `catalog` e `forms`) com templates em `base_templates`, `catalog/templates` e `forms/templates`.
- Entrypoint: `manage.py` e configuração principal em `projeto/settings.py` (usa `python-decouple` -> variáveis em `.env`).
- Banco: PostgreSQL (configurado via `DB_*` no `.env`). Dependências principais em `requirements.txt` (Django 5.2.3, djangorestframework, pillow, psycopg2).

## Componentes e fluxos de dados importantes
- `catalog/models.py` — modelos centrais: `Termo`, `Categoria`, `Subcategoria`, `Video`. Observe o padrão de chaves primárias com prefixo `id_` (ex.: `id_termo`).
- Uploads e conversão: `Video.save()` chama `catalog.utils.convert_video_to_mp4` para garantir `.mp4` (usa `ffmpeg` via subprocess). Não remova/altere essa lógica sem checar `catalog/utils.py`.
- Relações: `Classificacao` e `Pertence` usam `UniqueConstraint` para evitar duplicações.
- Views: `catalog/views.py` e `forms/views.py` usam renderização de templates e `modelformset_factory` para uploads de múltiplos vídeos.

## Convenções do projeto (específicas)
- Nomes de campos primários seguem `id_<modelo>` em vez de `id` ou `pk` padrão. Ao escrever queries prefira `get(pk=...)` somente quando souber que `pk` mapeia ao campo default; caso contrário use `id_termo`, `id_categoria` explicitamente.
- Muitas views capturam Exception de forma ampla e retornam `HttpResponse` com a mensagem; mantenha esse padrão ao adicionar novas views para consistência de erro (embora melhorar o tratamento seja uma boa tarefa futura).
- Template dirs são declaradas em `TEMPLATES['DIRS']` (veja `projeto/settings.py`); sempre inserir templates nesses caminhos para serem localizados.
- Variáveis de contexto comuns: `termos_carrossel`, `categorias_galeria`, `is_detail_page` — observe estes nomes ao modificar templates.

## Dependências externas / integração
- `python-decouple`: variáveis de ambiente em `.env` (ex.: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
- `ffmpeg`: necessário em PATH para conversão de vídeos (`catalog/utils.py` usa `subprocess.run(['ffmpeg', ...])`).

## Comandos úteis (desenvolvimento local — PowerShell no Windows)
```powershell
# criar virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# configurar .env (exemplo mínimo)
# SECRET_KEY=troque_isto
# DEBUG=True
# DB_NAME=... DB_USER=... DB_PASSWORD=... DB_HOST=localhost DB_PORT=5432

# migrar e rodar servidor
python manage.py migrate
python manage.py runserver

# testes
python manage.py test
```

## Pontos de atenção (gotchas)
- Não remover a conversão de vídeo sem validar `ffmpeg` e entender que `catalog/utils.py` pode remover o arquivo original após gerar o `.mp4`.
- `projeto/settings.py` espera `decouple.config` — builds/CI precisam fornecer variáveis de ambiente equivalentes.
- Algumas views e formulários assumem que um `Dominio` com `pk=1` existe (veja `forms/views.py`), então crie dados iniciais ou trate esse caso ao testar.

## Exemplos rápidos (onde olhar)
- Conversão de vídeo: `catalog/models.py` + `catalog/utils.py` (ffmpeg via subprocess). 
- Rotas principais: `projeto/urls.py` (inclui `catalog.urls` e `forms.urls`).
- Templates base: `base_templates/` e `base_static/` para CSS/JS globais.

## O que o agente pode fazer agora
- Produzir/atualizar alterações pequenas: correções em templates, views e forms seguindo as convenções acima.
- Para mudanças que alteram upload/armazenamento de mídia, confirme `MEDIA_ROOT`/`MEDIA_URL` em `projeto/settings.py` e considere impactos em `catalog/utils.py`.

Se algo ficou vago ou você quer que eu inclua exemplos adicionais (trechos de código para padrões específicos), diga quais áreas priorizar e eu ajusto o arquivo.
