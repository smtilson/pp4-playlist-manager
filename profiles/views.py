from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def test(request):
    """
    Test view, to load templates properly.
    """
    
    return render(request, "profiles/index.html")