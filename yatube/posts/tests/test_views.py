from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Group, Post, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='not_auth')
        cls.user_3 = User.objects.create_user(username='never_auth')
        cls.test_follow = Follow.objects.create(
            user=cls.user_2,
            author=cls.user
        )
        cls.TEST_AMOUMT_POST = 5
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.index_url = '/', 'posts/index.html'
        cls.group_url = f'/group/{cls.group.slug}/', 'posts/group_list.html'
        cls.profile_url = (f'/profile/{cls.user.username}/',
                           'posts/profile.html')
        cls.post_url = f'/posts/{cls.post.id}/', 'posts/post_detail.html'
        cls.new_post_url = '/create/', 'posts/create_post.html'
        cls.edit_post_url = (f'/posts/{cls.post.id}/edit/',
                             'posts/create_post.html')
        cls.profile_follow = (f'profile/{cls.user.username}/follow/',
                              'posts/follow_index.html')
        cls.paginated_urls = (
            cls.index_url,
            cls.group_url,
            cls.profile_url
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(PostPagesTests.user_2)
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(PostPagesTests.user_3)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates = (self.index_url, self.group_url, self.profile_url,
                     self.post_url, self.new_post_url, self.edit_post_url)
        for reverse_name, template in templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, self.post.text)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        group_title_0 = first_object.group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(group_title_0, self.group.title)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        author_0 = first_object.author
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(author_0, self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('detail_obj'), self.post)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_only_in_one_group(self):
        """Посту присваивается только одна группа."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug}))
        self.assertNotEqual(response.context.get('page_obj'), self.group_2)

    def test_cache_index(self):
        """Проверка кеширования главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        index_content_1 = response.content
        form_data = {'text': 'text'}
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        index_content_2 = response.content
        self.assertTrue(index_content_1 == index_content_2)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        index_content_2 = response.content
        self.assertTrue(index_content_1 != index_content_2)

    def test_auth_user_follow_author(self):
        """Возможность подписываться на других авторов."""
        for i in range(self.TEST_AMOUMT_POST):
            self.post = Post.objects.create(
                author=self.user,
                text='test_post_№' + str(i)
            )
        follow_count_before = Follow.objects.count()
        self.authorized_client_3.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user.username}))
        follow_count_after = Follow.objects.count()
        self.assertEqual(follow_count_before + 1, follow_count_after)

    def test_auth_user_unfollow_author(self):
        """Возможность отменить подписку на других авторов."""
        for i in range(self.TEST_AMOUMT_POST):
            self.post = Post.objects.create(
                author=self.user,
                text='test_post_№' + str(i)
            )
        follow_count_before = Follow.objects.count()
        self.authorized_client_2.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user.username}))
        follow_count_after = Follow.objects.count()
        self.assertEqual(follow_count_before, follow_count_after + 1)

    def test_cant_follow_himself(self):
        """Невозможность подписаться на себя."""
        follow_count_before = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user.username}))
        follow_count_after = Follow.objects.count()
        self.assertEqual(follow_count_before, follow_count_after)

    def test_new_post_appears_in_desired_feed(self):
        """Новый пост только в ленте подписчиков."""
        self.authorized_client_2.get(reverse('posts:profile_follow',
                                     kwargs={'username': self.user.username}))
        response_user_2 = self.authorized_client_2.get(
            reverse('posts:follow_index'))
        self.assertEqual(
            len(response_user_2.context['page_obj']), 1)
        cache.clear()
        response_user_3 = self.authorized_client_3.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response_user_3.context['page_obj']), 0)
        cache.clear()
        post_data = {'text': 'Новый пост', }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_data,
            follow=True
        )
        response_user_2 = self.authorized_client_2.get(
            reverse('posts:follow_index'))
        self.assertEqual(
            len(response_user_2.context['page_obj']), 2)
        cache.clear()
        response_user_3 = self.authorized_client_3.get(reverse(
            'posts:follow_index'))
        self.assertEqual(len(response_user_3.context['page_obj']), 0)
