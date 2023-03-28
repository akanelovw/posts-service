from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_created_user_exists(self):
        tasks_count = User.objects.count()
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'TestUser',
            'password1': 'FrniHzE4',
            'password2': 'FrniHzE4',
            'email': 'testmail@mail.ru',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), tasks_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name=form_data['first_name'],
                last_name=form_data['last_name'],
                email=form_data['email'],
                username=form_data['username'],
            ).exists()
        )
