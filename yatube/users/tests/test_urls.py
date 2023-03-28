from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client(enforce_csrf_checks=True)
        self.authorized_client.force_login(self.user)
        self.token = default_token_generator.make_token(user=self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user))

    def test_urls_exist_at_desired_location_for_guest_user(self):
        """Страницы доступны любому пользователю."""
        urls_dict = {
            'signup': '/auth/signup/',
            'login': '/auth/login/',
            'password_reset': '/auth/password_reset/',
            'password_reset_done': '/auth/password_reset/done',
            'reset_confirm': f'/auth/reset/{self.uid}/{self.token}/',
            'reset_done': '/auth/reset/done/'
        }
        for url in urls_dict.values():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exist_at_desired_location_for_auth_user(self):
        """Страницы доступны авторизированному пользователю."""
        urls_dict = {
            'password_change': '/auth/password_change/',
            'password_change_done': '/auth/password_change/done/',
            'logout': '/auth/logout/',
        }
        for url in urls_dict.values():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_guest_redirect(self):
        """Проверяем редирект неавторизированного пользователя."""
        urls_dict = {
            '/auth/password_change/': (
                '/auth/login/?next=/auth/password_change/'
            ),
            '/auth/password_change/done': (
                '/auth/login/?next=/auth/password_change/done'
            ),
        }
        for url, redirect in urls_dict.items():
            with self.subTest(redirect=redirect):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response, (redirect)
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/password_reset/': 'users/password_reset_form.html',
            # '/auth/password_reset/done/': 'users/password_reset_done.html',
            f'/auth/reset/{self.uid}/{self.token}/': (
                'users/password_reset_confirm.html'
            ),
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_change/': 'users/password_change_form.html',
            # '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_not_found(self):
        """Запрос к несуществующей странице."""
        response = self.authorized_client.get('/auth/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
