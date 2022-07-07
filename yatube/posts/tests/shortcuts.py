from typing import Any, Tuple

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from ..models import Post


class TestCaseExtended(TestCase):
    """
    Дополняет класс шаблонами view-фикстур для тестов.
    Добавляет вспомогательные функции.
    """
    # переменные для views-фикстур
    index_view: Tuple[Any]
    group_list_view: Tuple[Any]
    profile_view: Tuple[Any]
    post_detail_view: Tuple[Any]
    post_create_view: Tuple[Any]
    post_edit_view: Tuple[Any]
    random_page_url: str

    def get_views(self, post, user, group):
        """Создание view-фикстур"""

        self.index_view = (
            reverse('posts:index'),
            'posts/index.html',
            None,
        )
        self.follow_index_view = (
            reverse('posts:follow_index'),
            'posts/follow.html',
            '/auth/login/?next=/follow/',
        )
        self.group_list_view = (
            reverse('posts:group_list', args=[group.slug]),
            'posts/group_list.html',
            None,
        )
        self.profile_view = (
            reverse('posts:profile', args=[user.username]),
            'posts/profile.html',
            None,
        )
        self.follow_view = (
            reverse('posts:profile_follow', args=[user.username]),
            None,
            f'/auth/login/?next=/profile/{user.username}/follow/',
        )
        self.unfollow_view = (
            reverse('posts:profile_unfollow', args=[user.username]),
            None,
            f'/auth/login/?next=/profile/{user.username}/unfollow/',
        )
        self.post_detail_view = (
            reverse('posts:post_detail', args=[post.id]),
            'posts/post_detail.html',
            None,
        )
        self.post_create_view = (
            reverse('posts:post_create'),
            'posts/create_post.html',
            '/auth/login/?next=/create/',
        )
        self.post_edit_view = (
            reverse('posts:post_edit', args=[post.id]),
            'posts/create_post.html',
            f'/auth/login/?next=/posts/{post.id}/edit/',
        )
        self.add_comment_view = (
            reverse('posts:add_comment', args=[self.post.id]),
            None,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        self.random_page_url = '/random_page/'

    def create_multiple_test_posts(self, user, group, quantity):
        """Создает несколько постов одного польз. и группы."""
        for i in range(quantity):
            Post.objects.create(
                text=f'Текст поста {i+1} от {user} для {group}',
                group=group,
                author=user,
            )

    def generate_bulk_test_posts_data(self):
        """Наполняет тестовую базу типовыми постами."""
        self.create_multiple_test_posts(self.user1, self.group1, 7)
        self.create_multiple_test_posts(self.user1, self.group2, 4)
        self.create_multiple_test_posts(self.user2, self.group1, 7)
        self.create_multiple_test_posts(self.user2, self.group2, 4)
        self.create_multiple_test_posts(self.user1, None, 2)
        self.create_multiple_test_posts(self.user2, None, 2)

    def assert_equal_posts(self, post1, post2):
        """Сравнение полей постов."""
        self.assertEqual(post1.text, post2.text)
        self.assertEqual(post1.group, post2.group)
        self.assertEqual(post1.author, post2.author)
        self.assertEqual(post1.image, post2.image)

    def assert_equal_post_to_form_data(self, post, text, group, image):
        """Сравнение полей формы с постом."""
        self.assertEqual(text, post.text)
        self.assertEqual(group, post.group.id)
        self.assertIn(image.name, post.image.name)

    def get_image(self):
        """Возвращает картику."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        return SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
