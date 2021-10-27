from django.http import JsonResponse, HttpResponse
from django.views.generic.list import ListView
from django.shortcuts import render
from rest_framework.response import Response
import requests
import json
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from .serializers import ActivitySerializer

# https://raybesiga.com/basic-django-app-github-api/
# https://docs.github.com/en/rest/reference/activity

# Create your views here.
@login_required
@api_view(['GET'])
def GithubEventsView(request):
    template_name = 'LinkedSpace/GitHub/github.html'

    try:
        if request.user.is_authenticated:
            git_username = request.user.github
            response = requests.get(f'https://api.github.com/users/{git_username}/events/public')

            activities = []
            data = response.json() # list

            """Successful request will return 30 most recent public activities.
               Activities are then parsed, and Event Objects are created.
               Subsequently serialized and returned to the user to optionally 'Share'
               with to their Stream.
               IDEA: shared events should be converted into a Post and sent to My Stream.
                     To prevent duplicate GitHub activities from being shared, a github_activity
                     field could be added to posts model. 
                     github_activity field would reference the id of the event_object. This can 
                     be checked against the database every time the activities are loaded.
            """
            for event in data:
                    actor_dict = event['actor']
                    github_actor = actor_dict['display_login']
                    repo_dict = event['repo']

                    timestamp = event['created_at']
                    event_id = event['id']
                    event_type = event['type']
                    repo = repo_dict['name']
                    url = repo_dict['url']

                    event_object = {
                        "actor": github_actor,
                        "timestamp": timestamp,
                        "id": event_id,
                        "type": event_type,
                        "repo": repo,
                    }
                    activities.append(event_object)

            serializer = ActivitySerializer(activities, many=True)
            context = {'activities': serializer.data}

            # django REST framework API view
            # return Response(context, status=status.HTTP_200_OK)
            print(context)

            # context needs to be json()
            return render(request, 'LinkedSpace/GitHub/github.html', context, status=status.HTTP_200_OK)

            # pretty_json = json.dumps(response.json(), indent=4, sort_keys=True)
            # save_fp = 'pretty.json'
            # with open(file=save_fp, mode='w') as output_file:
            #     json.dump(response.json(), output_file, indent=4, sort_keys=True)
            # print(pretty_json)
            # data = response.json()

            # return HttpResponse(activities, status=status.HTTP_200_OK)
            # return JsonResponse(context, safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        raise NotFound(e)
    