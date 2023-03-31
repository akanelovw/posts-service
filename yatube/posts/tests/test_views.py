from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()
FIRST_PAGE_EXPECTED_POSTS = 10
SECOND_PAGE_EXPECTED_POSTS = 3
PAGES_TEST_POSTS_CREATE = 13


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.post.group.slug}
            ): ('posts/group_list.html'),
            reverse('posts:post_create'): (
                'posts/create_post.html'
            ),
            reverse('posts:profile', kwargs={'username': self.user}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_posts_context_object(
        self,
        response,
        context,
        one_object=True
    ):
        if one_object:
            first_object = response.context[context][0]
        else:
            first_object = response.context[context]
        post_text_0 = first_object.text
        group_slug_0 = first_object.group.slug
        group = first_object.group
        author = first_object.author
        image = first_object.image
        context_dict = {
            post_text_0: self.post.text,
            group_slug_0: self.post.group.slug,
            group: self.post.group,
            author: self.post.author,
            image: self.post.image
        }
        for value, expected in context_dict.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:index')
        ))
        self.check_posts_context_object(
            response=response,
            context='page_obj'
        )

    def test_group_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.post.group.slug})
        ))
        self.check_posts_context_object(
            response=response,
            context='page_obj'
        )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        ))
        self.check_posts_context_object(
            response=response,
            context='page_obj'
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        ))
        self.check_posts_context_object(
            response=response,
            context='post',
            one_object=False
        )

    def test_post_edit_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        urls_dict = {
            'post_create': reverse('posts:post_create'),
            'post_edit': (
                reverse('posts:post_edit', kwargs={'post_id': self.post.id})
            )
        }
        for url in urls_dict.values():
            response = self.authorized_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        post_list = []
        for i in range(PAGES_TEST_POSTS_CREATE):
            post_list.append(Post(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group)
            )
        Post.objects.bulk_create(post_list)

    def first_page_contains_records(self, url):
        response = self.client.get(url)
        self.assertEqual(len(response.context['page_obj']),
                         FIRST_PAGE_EXPECTED_POSTS)

    def second_page_contains_records(self, url):
        response = self.client.get(url + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         SECOND_PAGE_EXPECTED_POSTS)

    def test_paginator_pages(self):
        urls_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for url in urls_list:
            self.first_page_contains_records(url=url)
            self.second_page_contains_records(url=url)


class PostCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_empty = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-empty',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_created_correctly_index(self):
        response = self.client.get(reverse('posts:index'))
        container = response.context['page_obj']
        self.assertIn(self.post, container, 'поста нет на главной странице')

    def test_post_created_correctly_group_posts(self):
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.post.group.slug}
        ))
        response_empty_group = self.client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group_empty.slug}
        ))
        container = response.context['page_obj']
        container_empty_group = response_empty_group.context['page_obj']
        self.assertIn(self.post, container, (
            'поста нет на странице выбранной группы'
        ))
        self.assertNotIn(self.post, container_empty_group, (
            'пост на странице другой группы'
        ))

    def test_post_created_correctly_profile(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        container = response.context['page_obj']
        self.assertIn(self.post, container, 'поста нет на главной странице')


class FollowingTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_user_follow(self):
        count = Follow.objects.count()
        test_user = User.objects.create_user(username='test')
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=(test_user.username,)),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.count(), count + 1)
        follow = Follow.objects.last()
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, test_user)

    def test_authorized_user_unfollow(self):
        test_user = User.objects.create_user(username='test')
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(test_user.username,)),
            follow=True
        )
        count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(test_user.username,)),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Follow.objects.count(), count - 1)

    def test_follow(self):
        response = self.authorized_client.get(reverse(
            'posts:follow_index',)
        )
        container = response.context['page_obj']
        self.assertNotIn(self.post, container, 'пост есть в избранных')
        follow = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.author}),
            follow=True
        )
        container2 = follow.context['page_obj']
        self.assertIn(self.post, container2, 'поста нет в избранных')


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        self.assertNotEqual(response_2.content, response_3.content)
