from rest_framework import authentication, permissions
from Node.models import Node
import base64

class AccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')

        decoded_credentials = base64.b64decode(credentials).decode("utf-8").split(':')

        try:
            node = Node.objects.get(id=decoded_credentials[0])
            stored = f'{node.id}:{node.password}'
            expected = base64.b64encode(bytes(stored, 'UTF-8')).decode()
        except:
            expected = base64.b64encode(b':').decode()

        if token_type == 'Basic' and credentials == expected:
            return True
        else:
            return False

class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_type, _, credentials = auth_header.partition(' ')

        decoded_credentials = base64.b64decode(credentials).decode("utf-8").split(':')

        try:
            node = Node.objects.get(id=decoded_credentials[0])
            stored = f'{node.id}:{node.password}'
            expected = base64.b64encode(bytes(stored, 'UTF-8')).decode()
        except:
            expected = base64.b64encode(b':').decode()

        # expected = base64.b64encode(b'socialdistribution_t14:c404t14').decode()
        if token_type == 'Basic' and credentials == expected:
            return (True, None)
        else:
            return None

    def authenticate_header(self, request):
        return '{"username" : <username>, "password" : <password>}'