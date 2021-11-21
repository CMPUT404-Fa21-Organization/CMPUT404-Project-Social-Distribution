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
        author = Author.objects.create_user(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        self.assertTrue(Author.objects.filter(pk=author.auth_pk))
        return

    def test_author_str_(self):
        test_email = 'testauthor@email.com'
        Author.objects.all().delete()
        author = Author.objects.create_user(email=test_email, displayName='Test Author', password='testauthorpassw0rd')
        self.assertEqual(str(author.email), test_email)

    # def test_duplicate_author(self):
        # Author.objects.all().delete()
        # test_email = 'duplicateauthors@email.com'
        # author = Author.objects.create_user(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        # dup_author = Author.objects.create_user(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        # print(Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd'))
        # self.assertRaisesRegex(IntegrityError, 'UNIQUE constraint failed: Author_author.email',Author.objects.create(email='testauthor@email.com', displayName='Duplicate Author', password='duplicatepassw0rd'))

    # def test_create_author_invalid_password(self):
    #     return
        
    def test_create_author_not_admin(self):
        Author.objects.all().delete()
        author = Author.objects.create_user(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
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

    # def test_duplicate_author(self):
    #     Author.objects.all().delete()
    #     request = self.client.post('/register/', self.test_author, format='json')
    #     duplicate_req = self.client.post('/register/', self.test_author, format='json')
    #     print(duplicate_req.status_code)

    def test_author_login_endpoint(self):
        Author.objects.all().delete()
        Author.objects.create_user(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        request = self.client.post('/login/', self.test_author, format='json')
        self.assertTrue(request.status_code == 200)

    def test_login_invalid_credentials(self):
        Author.objects.all().delete()
        Author.objects.create_user(email='testauthor@email.com', displayName='Test Author', password='testwrongpassw0rd')
        request = self.client.post('/login/', self.test_author, format='json')
        self.assertTrue(request.status_code == 401)

    def test_author_updated(self):
        Author.objects.all().delete()
        payload = {
            'email':'updated@email.com',
            'displayName':'Updated Test Author'
        }
        author = Author.objects.create(email='testauthor@email.com', displayName='Test Author', password='testpassw0rd')
        self.client.post(f'/author/{author.auth_pk}/', payload)
        updated_author = Author.objects.get(pk=author.auth_pk)
        self.assertNotEqual(updated_author.email, payload['email']) # author email not changed
        self.assertEqual(updated_author.displayName, 'Updated Test Author') # author displayName changed