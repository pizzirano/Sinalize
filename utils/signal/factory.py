from faker import Faker

fake = Faker()

def gerar_dominios(qtd=6):
    return [{'id': i, 'nome': fake.word().title()} for i in range(1, qtd + 1)]

def gerar_categorias(dominio_id, qtd=5):
    return [{'id': i, 'nome': fake.word().title(), 'dominio_id': dominio_id} for i in range(1, qtd + 1)]

def gerar_subcategorias(categoria_id, qtd=4):
    return [{'id': i, 'nome': fake.word().title(), 'categoria_id': categoria_id} for i in range(1, qtd + 1)]

def gerar_termos(subcategoria_id, qtd=5):
    return [{
        'id': i,
        'nome': fake.word().title(),
        'descricao': fake.sentence(),
        'video_url': f"https://placehold.co/320x320/269fe6/ffffff?text=Termo+{i}",
        'subcategoria_id': subcategoria_id
    } for i in range(1, qtd + 1)]

def gerar_termo_detail(termo_id, dominio_id, categoria_id, subcategoria_id):
    return {
        'id': termo_id,
        'nome': fake.word().title(),
        'descricao': fake.text(),
        'video': {'url': f"https://placehold.co/640x360/333/fff?text=Vídeo+{termo_id}"},
        'autor': {'nome': fake.first_name(), 'sobrenome': fake.last_name()},
        'data_criacao': fake.date_time(),
        'dominio_id': dominio_id,
        'dominio_nome': fake.word().title(),
        'categoria_id': categoria_id,
        'categoria_nome': fake.word().title(),
        'subcategoria_id': subcategoria_id,
        'subcategoria_nome': fake.word().title(),
    }

# Testar no terminal com:
if _name_ == '_main_':
    from pprint import pprint
    pprint(gerar_termo_detail(1, 1, 1, 1))