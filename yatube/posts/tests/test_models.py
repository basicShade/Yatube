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
        obj_field_values = (
            (self.post.author, self.post.author.username),
            (self.post, self.post.text[:15]),
            (self.group, self.group.title),
        )

        for object, expected_value in obj_field_values:
            with self.subTest(object=object):
                self.assertEqual(str(object), expected_value)

    def test_verbose_name(self):
        """Проверяем verbose в модели Post."""
        verbose_names = (
            ('text', 'Текст поста'),
            ('pub_date', 'Дата публикации поста'),
            ('author', 'Автор поста'),
            ('group', 'Группа'),
        )

        for verbose, expected_verb in verbose_names:
            with self.subTest(verbose=verbose):
                self.assertEqual(
                    self.post._meta.get_field(verbose).verbose_name,
                    expected_verb,
                )

    def test_help_text(self):
        """Проверяем helptext в модели Post."""
        help_texts = (
            ('text', 'Введите текст поста'),
            ('group', 'Группа, к которой будет относиться пост'),
        )

        for help_text, expected_text in help_texts:
            with self.subTest(help_text=help_text):
                self.assertEqual(
                    self.post._meta.get_field(help_text).help_text,
                    expected_text,
                )
