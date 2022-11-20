from django.shortcuts import render
from django.http import HttpResponse

# Create your Project Level views here
def home(request):
    return render(request, 'index.html')