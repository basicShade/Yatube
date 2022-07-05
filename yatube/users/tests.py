"""
Содержит пару тестов для страницы авторизации.
TBD
"""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='writer',
            password='pwd',
        )
        self.client = Client()

    def test_auth_login_redirect(self):
        """Страница /auth/login/ перенаправляет на / после авторизации."""
        response = self.client.post(
            '/auth/login/',
            {'username': 'writer', 'password': 'pwd'},
            follow=True,
        )
        self.assertRedirects(response, '/')

    def test_auth_login_error(self):
        """Страница /auth/login/ возвращает форму с ошибкой ввода."""
        response = self.client.post(
            '/auth/login/',
            {'username': '', 'password': 'pwd'},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertIsNotNone(response.context.get('form')._errors)
