import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Follow, Group, Post
from .shortcuts import TestCaseExtended

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCaseExtended):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test_group_slug1',
            description='Тестовое описание группы1'
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_group_slug2',
            description='Тестовое описание группы2'
        )

        cls.user1 = User.objects.create_user(username='noname1')
        cls.user2 = User.objects.create_user(username='noname2')

        cls.auth_client1 = Client()
        cls.auth_client2 = Client()

    def setUp(self):
        self.auth_client1.force_login(self.user1)
        self.auth_client2.force_login(self.user2)

        self.generate_bulk_test_posts_data()
        self.post = Post.objects.first()
        self.post.text = 'Последний пост'
        self.post.author = self.user1
        self.post.group = self.group1
        self.post.image = self.get_image()
        self.post.save()

        self.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=self.post,
            author=self.user2,
        )
        Follow.objects.create(
            user=self.user2,
            author=self.user1,
        )
        Follow.objects.create(
            user=self.user1,
            author=self.user2,
        )
        self.get_views(self.post, self.user1, self.group1)
        self.other_group_view = reverse(
            'posts:group_list',
            args=[self.group2.slug],
        )


        self.multiple_post_views = (
            self.index_view,
            self.group_list_view,
            self.profile_view,
            self.follow_index_view,
        )
        self.single_post_views = (
            self.post_create_view,
            self.post_edit_view,
            self.post_detail_view,
        )
        self.all_views_tested = (
            *self.single_post_views,
            *self.multiple_post_views,
        )

    def tearDown(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_view_names_refer_correct_templates(self):
        """Соответствие view names и html templates."""
        for url, html, redirect in self.all_views_tested:
            with self.subTest(url=url):
                response = self.auth_client1.get(url)
                self.assertTemplateUsed(response, html)

    def test_ten_posts_per_page(self):
        """Страницы содержат не более 10 объектов постов."""
        for url, html, redirect in self.multiple_post_views:
            with self.subTest(url=url):
                response = self.auth_client1.get(url + '?page=1')
                page = response.context.get('page_obj')
                self.assertEqual(len(page), 10)

    def test_group_list_page_context(self):
        """
        Страница постов сообщества содержит посты только выбраной группы.
        """
        response = self.auth_client1.get(
            self.group_list_view[0] + '?page=1'
        )
        page = response.context.get('page_obj')
        db = Post.objects.filter(group=self.group1)[:len(page)]

        for page_post, db_post in zip(page, db):
            self.assertEqual(page_post.group, self.group1)
            self.assert_equal_posts(page_post, db_post)

    def test_profile_page_context(self):
        """
        Страница profile пользователя не содержит постов другого пользователя.
        """
        response = self.auth_client1.get(self.profile_view[0])
        page = response.context.get('page_obj')
        db = Post.objects.filter(author=self.user1)[:len(page)]

        for page_post, db_post in zip(page, db):
            self.assertEqual(page_post.author, self.user1)
            self.assert_equal_posts(page_post, db_post)

    def test_post_detail_context(self):
        """Страница post_detail содержит единственный пост с требуемым id."""
        response = self.auth_client1.get(self.post_detail_view[0])
        post = response.context.get('post')

        self.assertIsInstance(post, Post)
        self.assert_equal_posts(post, self.post)

    def test_post_detail_context_comments_section(self):
        """
        Страница post_detail содержит форму для комментария и комменты.
        """
        response = self.auth_client1.get(self.post_detail_view[0])

        form = response.context.get('add_comment_form')
        comments = response.context.get('comments')

        self.assertIsInstance(form, CommentForm)
        self.assertFalse(form.initial)
        self.assertIn(self.comment, comments)

    def test_post_edit_context(self):
        """
        Страница post/<post_id>/edit содержит форму поста с требуемым id.
        """
        response = self.auth_client1.post(self.post_edit_view[0])
        form = response.context.get('form')

        self.assertIsInstance(form, PostForm)
        self.assertEqual(self.post.text, form.initial['text'])
        self.assertEqual(self.post.group.id, form.initial['group'])
        self.assertEqual(self.post, form.instance)

    def test_post_create_context(self):
        """Страница post/create содержит пустую форму поста."""
        response = self.auth_client1.post(self.post_create_view[0])
        form = response.context.get('form')

        self.assertIsInstance(form, PostForm)
        self.assertFalse(form.initial)

    def test_post_appears_in_index_group_list_profile_followings(self):
        """
        Пост с группой фигурирует на страницах группы, польз., подписок.
        """
        for url, html, redirect in self.multiple_post_views:
            with self.subTest(url=url):
                response = self.auth_client2.get(url)

                self.assertIn(
                    self.post,
                    response.context.get('page_obj')
                )

    def test_post_not_appears_other_group_list_and_followings(self):
        """
        Пост с группой не фигурирует в других сообществах и подписках.
        """
        for url in (self.other_group_view, self.follow_index_view[0]):
            with self.subTest(url=url):
                response = self.auth_client1.get(url)
                self.assertNotIn(
                    self.post,
                    response.context.get('page_obj'),
                )
    def test_duplicate_follow_request_ignored(self):
        """Подписаться на пользователя можно только один раз."""
        follow_count = Follow.objects.count()
        self.auth_client2.get(self.follow_view[0])

        self.assertEqual(follow_count, Follow.objects.count())

    def test_post_image_appears_in_multiple_post_views_context(self):
        """
        Изображение передается на страницы index, group_list, profile.
        """
        for url, html, redirect in self.multiple_post_views:
            with self.subTest(url=url):
                response = self.auth_client2.get(url)
                page = response.context.get('page_obj')
                image_post_index = page.index(self.post)

                self.assertEqual(
                    page[image_post_index].image,
                    self.post.image,
                )

    def test_post_image_appears_in_post_detail_context(self):
        """
        Изображение передается на страницу post_detail.
        """
        response = self.auth_client1.get(self.post_detail_view[0])

        self.assertEqual(
            response.context.get('post').image,
            self.post.image,
        )

    def test_index_page_cached(self):
        response = self.auth_client1.get(self.index_view[0])
        cached_content = response.content

        self.post.delete()
        cached_response = self.auth_client1.get(self.index_view[0])
        self.assertEqual(cached_response.content, cached_content)

        cache.clear()
        db_response = self.auth_client1.get(self.index_view[0])
        self.assertNotEqual(db_response.content, cached_content)
