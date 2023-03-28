from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class ErrorPagesURLTests(TestCase):
    def setUp(self):
        self.guest_user = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/unexisting-page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_user.get(address)
                self.assertTemplateUsed(response, template)
