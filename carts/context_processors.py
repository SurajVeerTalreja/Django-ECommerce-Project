from .models import Cart, CartItem
from .views import _cart_id

def cart_counter(request):
    cart_count = 0

    if 'admin' in request.path:
        {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1]) # In case of many carts in the system, it returns the most latest one ONLY!
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)   