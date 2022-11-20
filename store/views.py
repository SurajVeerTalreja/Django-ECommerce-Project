from django.shortcuts import get_object_or_404, render
from carts.models import CartItem
from .models import Product
from category.models import Category
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

# Create your views here.
def store_page(request, category_slug=None):

    categories = None
    products = None

    if category_slug != None:
        # creating an instance of Category class with only desired slug attibute
        categories = get_object_or_404(Category, slug=category_slug)

        # creating an instance of Product class with only selected slug attributes from Category class
        products = Product.objects.filter(category=categories, is_available=True)

        # Once we have all the desired range of products, let's start pagination
        # Pass the object and number of items you want to show
        paginator = Paginator(products, 2)

        # Request URL with page number
        page = request.GET.get('page')

        # Show products only for that page you requested.
        products_on_that_page = paginator.get_page(page)

        product_count = products.count()    # Alternative of checking total products
    
    else:
        products = Product.objects.all().filter(is_available=True)

        # Once we have all the desired range of products, let's start pagination
        # Pass the object and number of items you want to show
        paginator = Paginator(products, 3)

        # Request URL with page number
        page = request.GET.get('page')

        # Show products only for that page you requested.
        products_on_that_page = paginator.get_page(page)

        product_count = len(products)

    context = {
        'products': products_on_that_page,
        'product_count': product_count
    }

    return render(request, 'store/store.html', context=context)


def product_detail(request, category_slug, product_slug):

    try:
        # creating an instance of Product class with only selected slug attributes from Category class
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug, is_available=True)

        # Checking if this single product is added to th cart. Returns True or False
        product_in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    
    except Exception as e:
        raise e

    context = {
        'product': single_product,
        'product_in_cart': product_in_cart,
    }

    return render(request, 'store/product_detail.html', context=context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.filter(Q(product_name__icontains=keyword) | Q(product_description__icontains=keyword) )
            product_count = products.count()
        
    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context=context)