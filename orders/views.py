from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
from random import randint
from django.contrib import messages
from store.models import Product

# Create your views here.
def payments(request):
    if request.method == 'POST':
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=request.POST['order_ID'])
        user = request.user
        grand_total = request.POST['grand_total']
        trans_ID = request.POST['trans_ID']
        status = request.POST['status']
        payment_method = 'Credit Card'

        payment = Payment(
            user=user,
            payment_id=trans_ID,
            payment_method=payment_method,
            amount_paid=grand_total,
            status=status,
        )

        payment.save()

        # After payment is saved. Associate with it current order & changed ordered status to True
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Once it is associated with order, associate it with ORDERED Product
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            ordered_product = OrderProduct()
            # order.id because id is the attribute of Order model itself & not a foreign Key.
            ordered_product.order_id = order.id 
            ordered_product.payment = payment
            ordered_product.user_id = request.user.id

            # Behind the scenes, Django appends "_id" to the field name to create its database column name.
            # For example, the database table for the CartItem model will have a product_id column.
            # That's why ID of 'foreign key attribute' is fetched as '_id' and not '.id' which might raise an error.
            ordered_product.product_id = item.product_id
            ordered_product.quantity = item.quantity
            ordered_product.product_price = item.product.price
            ordered_product.ordered = True
            ordered_product.save()

            # Now we will fetch all the Variations associated to the product
            # We did not do in in previous step because Variations is ManytoMany field
            
            # Getting each product from cart and its variations
            cart_item = CartItem.objects.get(id=item.id)
            product_variations = cart_item.variations.all()
            print(product_variations)

            # ordered_product saved in previous step
            ordered_product = OrderProduct.objects.get(id=ordered_product.id)
            # For many-to-many relationships set() accepts a list of either model instances or field values
            # [<Variation: ATX Jeans with color Blue>, <Variation: ATX Jeans with size Medium>]
            # List of Variations instances as above
            ordered_product.variations.set(product_variations)
            ordered_product.save()
            

            # Reduce Stock quantity of Product
            product = Product.objects.get(id=item.product_id) # Try to understand why .filter was raising error?
            product.stock -= item.quantity
            product.save()
        
        # Remove Cart Items after those are being Ordered successfully
        CartItem.objects.filter(user=request.user).delete()


        messages.success(request, 'Your order is placed successfully! Please Continue Shopping.')
        return redirect('store')
        
    return render(request, 'orders/payments.html')



def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If there are no cart items, redirect user back to store.
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        return redirect('store')
    
    tax = 0
    grand_total = 0
    for cart_item in cart_items:
        # Addition of Total price of each individual item = total price of all items
        total += (cart_item.quantity * cart_item.product.price) 
        # Addition of Total quantity of each product = Total quantity of all products
        quantity += cart_item.quantity  

        tax = (2 * total)/100
        grand_total = total + tax

    # Proceed with the order if cart items are present
    if request.method == 'POST':
        # Send POST request parameters inside this form.
        # Note that this form is exact duplicate of HTML form we have created
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the Billing data inside Order DB
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax

            # Fetch USER IP
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Now that we have saved the data, it has created a PK inside DB
            # which now we will access to generate Unique Order Number
            year = int(datetime.date.today().strftime('%Y'))
            date = int(datetime.date.today().strftime('%d'))
            month = int(datetime.date.today().strftime('%m'))

            date = datetime.date(year,month,date)
            current_date = date.strftime('%Y%m%d')

            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Generate trans_ID 
            random = str(randint(1,1000))
            trans_ID = current_date + random

            # Now that order details are saved, call the order object and pass it to the payments
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'trans_ID': trans_ID,
            }

            return render(request, 'orders/payments.html', context=context)
        
        # Really helpful
        else:
            print(form.errors)
    
    else:      
        return redirect('home')
