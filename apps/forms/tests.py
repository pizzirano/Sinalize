from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from catalog.models import Categoria, Classificacao, Dominio, Subcategoria, Termo, Video


def image_file(name='categoria.gif'):
    return SimpleUploadedFile(
        name,
        b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
        content_type='image/gif',
    )


def video_file(name='sinal.mp4'):
    return SimpleUploadedFile(name, b'video-content', content_type='video/mp4')


class SignalFormFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass12345')
        self.client.force_login(self.user)
        self.dominio = Dominio.objects.create(nome_dominio='Turismo')
        self.categoria = Categoria.objects.create(
            nome_categoria='Praias',
            dominio=self.dominio,
            c_imagem=image_file('praias.gif'),
            status='APPROVED',
        )
        self.subcategoria = Subcategoria.objects.create(
            nome_subcategoria='Litoral',
            categoria=self.categoria,
            status='APPROVED',
        )

    def post_data(self, **overrides):
        data = {
            'dominio': self.dominio.pk,
            'categoria': self.categoria.pk,
            'subcategoria': self.subcategoria.pk,
            'nome_termo': 'Praia Central',
            'descricao': 'Descricao do termo no card',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-titulo': 'Sinal principal',
            'form-0-tipo_video': 'Sinal',
            'form-0-descricao': 'Descricao propria do video',
        }
        data.update(overrides)
        return data

    def test_existing_category_does_not_require_new_image(self):
        response = self.client.post(
            reverse('forms:cadastrar_termo'),
            data={**self.post_data(), 'form-0-video': video_file()},
        )

        self.assertRedirects(response, reverse('forms:my_submissions'))
        termo = Termo.objects.get(nome_termo='Praia Central')
        self.assertEqual(termo.descricao, 'Descricao do termo no card')
        self.assertEqual(termo.get_categorias().get(), self.categoria)

    def test_new_category_requires_image(self):
        response = self.client.post(
            reverse('forms:cadastrar_termo'),
            data={
                **self.post_data(
                    nao_encontrei_categoria='on',
                    nova_categoria='Categoria sem imagem',
                ),
                'form-0-video': video_file(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A imagem')
        self.assertFalse(Categoria.objects.filter(nome_categoria='Categoria sem imagem').exists())

    def test_term_description_appears_on_category_listing_card(self):
        termo = Termo.objects.create(
            nome_termo='Termo aprovado',
            descricao='Descricao visivel na listagem',
            status='APPROVED',
            created_by=self.user,
        )
        Classificacao.objects.create(termo=termo, subcategoria=self.subcategoria)

        response = self.client.get(
            reverse('catalog:termo_list', args=[self.categoria.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Descricao visivel na listagem')

    def test_video_detail_uses_video_description(self):
        termo = Termo.objects.create(
            nome_termo='Termo com video',
            descricao='Descricao do termo nao deve aparecer',
            status='APPROVED',
            created_by=self.user,
        )
        video = Video.objects.create(
            titulo='Video detalhado',
            tipo_video='Sinal',
            descricao='Descricao especifica do video',
            termo=termo,
            video=video_file(),
            status='APPROVED',
            uploaded_by=self.user,
        )

        response = self.client.get(
            reverse('catalog:video_detail', args=[video.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Descricao especifica do video')
        self.assertNotContains(response, 'Descricao do termo nao deve aparecer')

    def test_multiple_videos_keep_independent_descriptions(self):
        response = self.client.post(
            reverse('forms:cadastrar_termo'),
            data={
                **self.post_data(
                    **{
                        'form-TOTAL_FORMS': '2',
                        'form-0-descricao': 'Descricao do video 1',
                        'form-1-titulo': 'Sinal secundario',
                        'form-1-tipo_video': 'Datilologia',
                        'form-1-descricao': 'Descricao do video 2',
                    }
                ),
                'form-0-video': video_file('video1.mp4'),
                'form-1-video': video_file('video2.mp4'),
            },
        )

        self.assertRedirects(response, reverse('forms:my_submissions'))
        termo = Termo.objects.get(nome_termo='Praia Central')
        descricoes = list(termo.videos.order_by('titulo').values_list('descricao', flat=True))
        self.assertEqual(
            descricoes,
            ['Descricao do video 1', 'Descricao do video 2'],
        )

    def test_edit_video_description(self):
        termo = Termo.objects.create(
            nome_termo='Termo editavel',
            descricao='Descricao original',
            status='PENDING',
            created_by=self.user,
        )
        Classificacao.objects.create(termo=termo, subcategoria=self.subcategoria)
        video = Video.objects.create(
            titulo='Video editavel',
            tipo_video='Sinal',
            descricao='Descricao antiga',
            termo=termo,
            video=video_file(),
            status='PENDING',
            uploaded_by=self.user,
        )

        response = self.client.post(
            reverse('forms:editar_termo', args=[termo.pk]),
            data={
                'dominio': self.dominio.pk,
                'categoria': self.categoria.pk,
                'subcategoria': self.subcategoria.pk,
                'nome_termo': 'Termo editavel',
                'descricao': 'Descricao editada',
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '1',
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
                'form-0-id_video': video.pk,
                'form-0-titulo': 'Video editavel',
                'form-0-tipo_video': 'Sinal',
                'form-0-descricao': 'Descricao nova do video',
            },
        )

        self.assertRedirects(response, reverse('forms:my_submissions'))
        video.refresh_from_db()
        self.assertEqual(video.descricao, 'Descricao nova do video')
