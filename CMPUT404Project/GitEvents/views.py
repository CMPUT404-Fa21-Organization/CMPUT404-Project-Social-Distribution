from django.http import JsonResponse, HttpResponse
import requests
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound

# https://raybesiga.com/basic-django-app-github-api/
# https://docs.github.com/en/rest/reference/activity

# Create your views here.
@login_required
@api_view(['GET'])
def GithubEventsView(request):
    try:
        if request.user.is_authenticated:
            git_username = request.user.github
            response = requests.get(f'https://api.github.com/users/{git_username}/events/public')
            data = response.json()
            return HttpResponse(data, status=status.HTTP_200_OK)
            # return JsonResponse(context, safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        raise NotFound(e)
    