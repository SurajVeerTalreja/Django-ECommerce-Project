from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
# Create your views here.
 
# Private function to retreive session Key of specific Cart
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id) # Get the specific product (without variations attached to it)
    product_with_variation = [] # All the variations of this product will lie in this list.

    if request.method == 'POST':
        for item in request.POST:  # every key-value paid after '?' in the URL
            key = item
            value = request.POST[key]

            # At the beginning, there are no variations record in our database with such attributes.
            # Therefore, we should use this code:
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_with_variation.append(variation)
                # This list above contains color-value object and size-value object
            except Variation.DoesNotExist:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # Get the specific cart using session id
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    # Now that we have cart and product, try adding that product from that cart into the database.
    # Check first if product already exixts in the cart.
    # Then check if product with same variations already exists in the cart
    # Two similar sessions of adding this product to cart will be checked
    # First, if user is authenticated, products will be fetched which belongs to current user
    # If User is not logged in, products will be fetched which belongs to current cart session
    if request.user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(product=product, user=request.user).exists()  # e.g. Does ATX-Jeans already exists in this cart?
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=request.user) # Get ATX-Jeans from this cart with all different variations

            # Check if existing variations matches with product variations.
            ex_var_list = []
            id_of_item = []
            for item in cart_item:  # Looping via single product with all different variations in the cart 
                existing_variation = item.variations.all()  # e.g. first ATX-Jeans with color:Black and Size:Medium and so on.
                ex_var_list.append(list(existing_variation)) # existing_variation is a QuerySet. Converting it to a List
                id_of_item.append(item.id)  # After this loop completes, we have now all ATX-Jeans with different variations along with their IDs.

            if product_with_variation in ex_var_list:
                # Increase the cart quantity only
                index = ex_var_list.index(product_with_variation)
                item_id = id_of_item[index]
                item = CartItem.objects.get(product=product, id=item_id)    # Check Later if we need the ID at all, since w are working on one product at a time while adding it to the Cart.
                item.quantity += 1  # All we are doing here is increasing the quantity. Item was already saved in DB when we hit Add to Cart button.
                item.save()

            else:
                # Add a New cart item
                item = CartItem.objects.create(product=product, quantity=1, user=request.user)
                if len(product_with_variation) > 0: # i.e, if variations are available for this product
                    item.variations.clear() 
                    item.variations.add(*product_with_variation)  # * adds all the variations
                        # add() Adds the specified model objects to the related object set.
                        # Associating Variations --> (Model) 'item' -->(object) with CartItem 'cart_item
                        # For e.g. Color-Black and Size-Small getting associated with ATX-Jeans i.e., current single product  
                item.save()
        
        # What if Cart is empty? What will we add to the database now?
        # First we will add 1st product inside the cart.
        # Hence, new cart_item instance will be created
        # Now that we have product inside the cart, we fetch it, and save it to te database.
        else:
            cart_item = CartItem.objects.create(
                user = request.user,
                product = product,
                quantity = 1,
            )
            if len(product_with_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_with_variation)  # Associating Variations 'item' with CartItem 'cart_item
            cart_item.save()
    
    # If user is not logged in and adding items to the cart
    else:
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()  # e.g. Does ATX-Jeans already exists in this cart?
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart) # Get ATX-Jeans from this cart with all different variations

            # Check if existing variations matches with product variations.
            ex_var_list = []
            id_of_item = []
            for item in cart_item:  # Looping via single product with all different variations in the cart 
                existing_variation = item.variations.all()  # e.g. first ATX-Jeans with color:Black and Size:Medium and so on.
                ex_var_list.append(list(existing_variation)) # existing_variation is a QuerySet. Converting it to a List
                id_of_item.append(item.id)  # After this loop completes, we have now all ATX-Jeans with different variations along with their IDs.

            if product_with_variation in ex_var_list:
                # Increase the cart quantity only
                index = ex_var_list.index(product_with_variation)
                item_id = id_of_item[index]
                item = CartItem.objects.get(product=product, id=item_id)    # Check Later if we need the ID at all, since w are working on one product at a time while adding it to the Cart.
                item.quantity += 1  # All we are doing here is increasing the quantity. Item was already saved in DB when we hit Add to Cart button.
                item.save()

            else:
                # Add a New cart item
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_with_variation) > 0: # i.e, if variations are available for this product
                    item.variations.clear() 
                    item.variations.add(*product_with_variation)  # * adds all the variations
                        # add() Adds the specified model objects to the related object set.
                        # Associating Variations --> (Model) 'item' -->(object) with CartItem 'cart_item
                        # For e.g. Color-Black and Size-Small getting associated with ATX-Jeans i.e., current single product  
                item.save()
        
        # What if Cart is empty? What will we add to the database now?
        # First we will add 1st product inside the cart.
        # Hence, new cart_item instance will be created
        # Now that we have product inside the cart, we fetch it, and save it to te database.
        else:
            cart_item = CartItem.objects.create(
                cart = cart,
                product = product,
                quantity = 1,
            )
            if len(product_with_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_with_variation)  # Associating Variations 'item' with CartItem 'cart_item
            cart_item.save()
    return redirect('cart')


def decrement_cart(request, product_id, cart_item_id):
    # Remember: Product has different variations.
    # Hence, cart_item_id is specific product with specific variation
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    
    except:
        pass
    return redirect('cart')



def delete_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)

    cart_item.delete()
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        # Show cart items for logged-in USERS
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        # Else fetch all the cart items for non logged-in session
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True) # Getting all items of this cart

        for cart_item in cart_items:
            # Addition of Total price of each individual item = total price of all items
            total += (cart_item.quantity * cart_item.product.price) 
            # Addition of Total quantity of each product = Total quantity of all products
            quantity += cart_item.quantity  

        tax = (2 * total)/100
        grand_total = total + tax

    except Cart.DoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,   # Remember each single product has their own variations now
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context=context)


@login_required(login_url= 'login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        # Show cart items for logged-in USERS
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        # Else fetch all the cart items for non logged-in session
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True) # Getting all items of this cart

        for cart_item in cart_items:
            # Addition of Total price of each individual item = total price of all items
            total += (cart_item.quantity * cart_item.product.price) 
            # Addition of Total quantity of each product = Total quantity of all products
            quantity += cart_item.quantity  

        tax = (2 * total)/100
        grand_total = total + tax

    except Cart.DoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,   # Remember each single product has their own variations now
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context=context)