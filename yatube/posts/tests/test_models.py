from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        values = (
            (group.title, str(group)),
            (post.text[:15], str(post)),
        )
        for value, expected_value in values:
            with self.subTest(value=value):
                self.assertEqual(value, expected_value)

    def test_post_text_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст поста')

    def test_post_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст поста')

    def test_group_label(self):
        """verbose_name поля text совпадает с ожидаемым."""
        group = PostModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Группа')

    def test_group_help_text(self):
        """verbose_name поля text совпадает с ожидаемым."""
        group = PostModelTest.group
        help_text = group._meta.get_field('title').help_text
        self.assertEqual(help_text, 'Выберите группу')
