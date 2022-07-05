from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client

from ..models import Group, Post
from .shortcuts import TestCaseExtended

User = get_user_model()


class PostsURLTests(TestCaseExtended):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group_slug',
            description='Тестовое описание группы'
        )

        cls.user = User.objects.create_user(username='writer')
        cls.user_noauthor = User.objects.create_user(username='noauthor')

        cls.guest_client = Client()
        cls.auth_client = Client()
        cls.auth_client_noauthor = Client()

    def setUp(self):
        self.auth_client.force_login(self.user)
        self.auth_client_noauthor.force_login(self.user_noauthor)

        self.post = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user,
        )

        self.get_views(self.post, self.user, self.group)

        self.public_urls = (
            self.index_view,
            self.profile_view,
            self.post_detail_view,
            self.group_list_view,
        )
        self.private_urls = (
            self.post_create_view,
            self.post_edit_view,
            self.add_comment_view,
            self.follow_index_view,
            self.follow_view,
            self.unfollow_view,
        )
        self.all_urls_tested = (
            *self.public_urls,
            *self.private_urls,
        )

    def tearDown(self):
        cache.clear()

    def test_urls_has_correct_templates(self):
        """Тестируем соответствие templates и urls."""
        for url, html, redirect in self.all_urls_tested:
            if html:
                with self.subTest(url=url):
                    response = self.auth_client.get(url)
                    self.assertTemplateUsed(response, html)

    def test_post_lists_pages_accessed_by_guest(self):
        """Страницы с постами и списками постов доступны неавтор. польз."""
        for url, html, redirect in self.public_urls:
            with self.subTest(url=url):
                guest_response = self.guest_client.get(url)
                self.assertEqual(guest_response.status_code, HTTPStatus.OK)

    def test_all_posts_namespace_pages_accessed_by_auth_user(self):
        """
        Все страницы namespace posts доступны авториз. польз.
        """
        for url, html, redirect in self.all_urls_tested:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                if html:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_guest_redirected_by_post_edit_comment_follow_pages(self):
        """
        Гость перенаправл. на авториз. при взаимод. с постами и подписками
        """
        for url, html, redirect in self.private_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect)

    def test_post_edit_ignores_random_user(self):
        """Страница /post/id/edit/ проигнорирует авторизованого неавтора."""
        response = self.auth_client_noauthor.get(
            self.post_edit_view[0],
        )
        self.assertRedirects(response, self.post_detail_view[0])

    def test_random_url_retuns_404(self):
        """Страница /random_page/ возвращает 404."""
        response = self.guest_client.get(self.random_page_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
