from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.another_user = User.objects.create_user(username='not_auth')
        cls.public_urls = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
        )
        cls.private_urls = (
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{cls.post.id}/edit/', 'posts/create_post.html')
        )
        cls.post_create_url = '/create/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_public_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        for address, template in self.public_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_private_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.private_urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_existent_page(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        for address in (self.public_urls, self.private_urls):
            with self.subTest(address=address):
                response = self.guest_client.get(address)
            if address not in (self.public_urls, self.private_urls):
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location(self):
        """Проверяю доступность общих страниц."""
        for adress, template in self.public_urls:
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK, template)

    def test_urls_create_exist_at_desired_location_authorized(self):
        """Cтраница создания поста для авторизованных."""
        response = self.guest_client.get(self.post_create_url)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(self.post_create_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_edit_post_exist_at_desired_location_author(self):
        """Редактирование только для автора поста."""
        response = self.guest_client.get(self.post_edit_url)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(self.post_edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.authorized_client.force_login(self.another_user)
        response = self.authorized_client.get(self.post_edit_url)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def test_urls_create_and_edit_redirect_anonymous(self):
        """Перенаправление неавторизованных."""
        for adress in (self.post_create_url, self.post_edit_url):
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
