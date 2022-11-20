from .models import Category

# Define your context_processors below:
# Context processors then can be passed inside any template (without passing it as a variable) 
# Pass it into settings must.

def category_slug_links(request):
    links = Category.objects.all()
    return dict(links=links)