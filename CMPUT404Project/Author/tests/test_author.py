from django.test import TestCase
from Author.models import Author

from rest_framework import status
from rest_framework.test import APIClient
from django.db import IntegrityError

""" Command line examples for executing tests
Run specified module: python3 manage.py test Author | python3 manage.py test Author.tests
Run specified class: python3 manage.py test Author.tests.AuthorTest
Run specified method: python3 manage.py test Author.tests.models.test_create_author
"""

# Create your tests here.
class AuthorTest(TestCase):
    def test_create_author(self):
        Author.objects.all().delete()
        author = Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        self.assertTrue(Author.objects.filter(pk=author.auth_pk))
        return

    def test_author_str_(self):
        test_email = 'testauthor@email.com'
        Author.objects.all().delete()
        author = Author.objects.create(email=test_email, displayName='Test Author', password='testauthorpassw0rd')
        self.assertEqual(str(author.email), test_email)

    # def test_duplicate_author(self):
        # test_email = 'duplicateauthors@email.com'
        # Author.objects.all().delete()
        # author = Author.objects.create(email=test_email, displayName='Test Author', password='testpassw0rd')
        # dup_author = Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        # print(Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd'))
        # self.assertRaises(IntegrityError, Author.objects.create(email=test_email, displayName='Duplicate Author', password='duplicatepassw0rd'))

    # def test_create_author_invalid_password(self):
    #     return
        
    def test_create_author_not_admin(self):
        Author.objects.all().delete()
        author = Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        self.assertFalse(author.is_staff)
        self.assertFalse(author.is_superuser)
        self.assertFalse(author.is_admin_approved)
        
class AuthorAPITest(TestCase):

    client = APIClient()
    test_author = {
        'email':'testauthor@email.com',
        'displayName':'Test Author',
        'password':'testpassw0rd',
    }

    def test_author_register_endpoint(self):
        Author.objects.all().delete()
        request = self.client.post('/register/', self.test_author, format='json')
        self.assertTrue(request.status_code == 200)

    def test_author_login_endpoint(self):
        Author.objects.all().delete()
        Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        request = self.client.post('/login/', self.test_author, format='json')
        self.assertTrue(request.status_code == 200)

    # def test_login_invalid_credentials(self):
    #     Author.objects.all().delete()
    #     Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testwrongpassw0rd')
    #     request = self.client.post('/login/', self.test_author, format='json')
        # self.assertTrue(request.status_code == 401)

    # def test_author_token_not_recycled(self):
    #     return

    # def test_author_display_name_updated(self):
    #     Author.objects.all().delete()
    #     payload = {
    #         'email':'testauthor@email.com',
    #         'displayName':'Updated Test Author'
    #     }
    #     author = Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
    #     print(author.auth_pk)
    #     self.client.force_authenticate(user=author)
    #     request_update = self.client.post(f'/author/{author.auth_pk}/edit', payload)
    #     print(request_update.status_code)
    #     self.assertEqual(author.displayName, 'Updated Test Author')

    # def test_author_email_not_updated(self):
    #     return