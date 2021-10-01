from django.shortcuts import render

# Create your views here.
def homeView(request):
    template_name = 'LinkedSpace/home.html'
    return render(request, template_name)

def loginView(request):
    template_name = 'LinkedSpace/login.html'
    return render(request, template_name)

def authorsView(request):
    template_name = 'LinkedSpace/authors.html'
    return render(request, template_name)
