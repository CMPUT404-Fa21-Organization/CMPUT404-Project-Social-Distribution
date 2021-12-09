from django.conf import settings
from django.core import serializers
from django.utils import timezone
from django.shortcuts import redirect, render
from Posts.models import Post, Author
import requests
import json
import uuid
import re
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from .serializers import ActivitySerializer
from django.core.paginator import Paginator

# https://raybesiga.com/basic-django-app-github-api/
# https://docs.github.com/en/rest/reference/activity

# Create your views here.
@login_required
@api_view(['GET'])
def GithubEventsView(request):
    template_name = 'LinkedSpace/GitHub/github.html'

    try:

        if request.user.is_authenticated:
            git_url = request.user.github
            git_username = git_url.replace("http://github.com/", "")
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

            page_number = request.GET.get('page')
            if 'size' in request.GET:
                page_size = request.GET.get('size')
            else:
                page_size = 5

            paginator = Paginator(activities, page_size)
            page_obj = paginator.get_page(page_number)

            serializer = ActivitySerializer(page_obj, many=True)
            context = {'pages': page_obj, 'activities': serializer.data}

            # django REST framework API view
            # return Response(context, status=status.HTTP_200_OK)
            # print(context)

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
        # raise (e)
        print(e, "==============================")
        return render(request, 'LinkedSpace/GitHub/github_404.html', status=status.HTTP_404_NOT_FOUND)

def gitPost(request, event_id):
    if request.user.is_authenticated:
        git_url = request.user.github
        git_username = git_url.replace("http://github.com/", "")
        response = requests.get(f'https://api.github.com/users/{git_username}/events/public')

        data = response.json() # list
        for event in data:
            if event['id'] == event_id:
                break

        title = "Shared GitHub Activity: " + event['type']
        descirption = "GitHub event from " + event['created_at']
        categories = ['GitHub']
        visibility = 'Public'
        unlisted = False
        contentType = 'text/plain'
        # print(type(event['actor']['display_login']))
        # print(event["repo"], type(event["repo"]))

        content = event['actor']['display_login'] + " made changes to " + event["repo"]['name']
        source = settings.SERVER_URL + "/"
        origin = settings.SERVER_URL + "/"

        author_id = Author.objects.get(pk=request.user.pk)
        id = author_id.url
        author = json.loads(serializers.serialize('json', Author.objects.filter(pk=request.user.pk), fields=('type', 'id', 'host', 'displayName', 'url', 'github',)))[0]['fields']

        r_uid = uuid.uuid4().hex
        uid = re.sub('-', '', r_uid)
        id = id + '/posts/' + uid + "/"
        comments_id = id + "comments/"

        published = timezone.now()

        posts = Post(pk=uid, id=id, author_id=author_id, author=author, title=title, source=source, origin=origin, description=descirption, contentType=contentType, count=0, size=10, categories=categories,visibility=visibility, unlisted=unlisted, published=published, content=content, comments=comments_id)
        posts.save()
        return redirect(GithubEventsView)
