from django.db import models
from django.shortcuts import HttpResponse, render
from Posts.models import *

# Create your views here.
def authorHome(request):
    template_name = 'LinkedSpace/Author/author.html'
    return render(request, template_name)

def author(request, author_id):
    return HttpResponse("You're looking at author %s." % author_id)
