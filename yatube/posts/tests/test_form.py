import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post
from .shortcuts import TestCaseExtended

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCaseExtended):

    def setUp(self):
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        self.auth_client = Client()
        self.user = User.objects.create_user(username='noname')
        self.auth_client.force_login(self.user)

        self.post = Post.objects.create(
            text='тестовый пост',
            group=self.group,
            author=self.user,
        )

        self.comment = Comment.objects.create(
            text='тестовый комментарий',
            post=self.post,
            author=self.user,
        )

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create_form_creates_post_in_database(self):
        """Валидная форма создает запись в Posts"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'пост с картинкой',
            'group': self.group.id,
            'image': self.get_image(),
        }

        self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        posts = Post.objects.all()
        created_post = posts.first()

        self.assertEqual(posts.count(), posts_count + 1)
        self.assert_equal_post_to_form_data(created_post, **form_data)

    def test_post_edit_form_updates_post_in_database(self):
        """Валидная форма обновляет запись в Posts"""
        form_data = {
            'text': 'update_test_post',
            'group': self.post.group.id,
            'image': self.get_image(),
        }

        self.auth_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        updated_post = Post.objects.get(id=self.post.id)

        self.assert_equal_post_to_form_data(updated_post, **form_data)

    def test_post_add_comment_form_updates_comments_in_database(self):
        """
        Валидная форма публикации комментария создает запись в Comments
        """
        comments_count = self.post.comment.count()
        form_data = {'text': 'тестовый комментарий'}

        self.auth_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        comments = self.post.comment.all()
        new_comment = comments.first()

        self.assertEqual(comments.count(), comments_count + 1)
        self.assertEqual(new_comment.text, form_data['text'])
        self.assertEqual(new_comment.author, self.user)
        self.assertEqual(new_comment.post, self.post)
