from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

# User Verification imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name =  form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            # create a User
            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, username=username,email=email, password=password
            )
            user.phone_number = phone_number
            user.save()

            # User verification
            current_site = get_current_site(request)    # Get current domain
            mail_subject = 'Please verify your account'
            email_body = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })

            # Send Email to the user
            to_email = email
            send_email = EmailMessage(mail_subject, email_body, to=[to_email])
            send_email.send()
            
            # messages.success(request, 'Registration Successful. Please Login In !!')

            # send the URL in following manner to catch if command = verification
            return redirect('/account/login/?command=verification&email='+email)
            

    else:        
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context=context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Check if user is valid i.e., available in DB
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Session id is different when user logs in.
            # Hence, if user adds products in cart and after that logs in, all items will disappear since session id would now be different
            # Hence we will check if there are cart items already and assign those to user before logging them in.
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)

                    # Get the variations of products present in the cart and save it in list
                    product_variation = []
                    for item in cart_items:
                        variations = item.variations.all()
                        product_variation.append(list(variations))
                    
                    # Now get all the variations of products already been assigned to the USER
                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    ids_of_item = []
                    for item in cart_items:  # Looping via single product with all different variations in the cart 
                        existing_variation = item.variations.all()  # e.g. first ATX-Jeans with color:Black and Size:Medium and so on.
                        ex_var_list.append(list(existing_variation)) # existing_variation is a QuerySet. Converting it to a List
                        ids_of_item.append(item.id)
                    
                    # Now that we have items from both ends, lets match if variations already exists or not
                    for variation in product_variation:
                        if variation in ex_var_list:
                            # Get the index of variation that matches
                            index = ex_var_list.index(variation)
                            # Get the product id using the index whose variation matched with currently added product
                            item_id = ids_of_item[index]
                            # Get that product and group them together
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                            
                        else:
                            # if there is no product with same variation then:
                            # Fetch all the items in the cart and just assign those to the user we get above
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user = user
                                item.save()
            except:
                pass
            
            # Once all the items are transferred to user, now we log them in.
            auth.login(request, user)
            messages.success(request, 'You are now Logged In...')

            # Fetch the previous URL (i.e., login page after hitting checkout button)
            url = request.META.get('HTTP_REFERER')
            try:
                # If a user is not logged in and checking out, the system will require them to log in first
                # Beacuse of login required functionality
                # Hence we are checking if that is the case, then user should be taken to checkout page directly
                # Otherwise to the dashboard if logging in normally
                query = requests.utils.urlparse(url).query  # next=/cart/checkout
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid User. Please Try Again.')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have been Logged out successfully!!!')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        # Decode Uid and get the primary key of user
        uid = urlsafe_base64_decode(uidb64).decode()

        # Get the user now that you have decoded the PK
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Make User's is_active status to True
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for verifying your account!')
        return redirect('login')
    
    else:
        messages.error(request, 'Invalid Activation Link')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        # Check if account already exists?
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            # Reset Password Email 
            current_site = get_current_site(request)    # Get current domain
            mail_subject = 'Please Reset your Password'
            email_body = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })

            # Send Email to the user
            to_email = email
            send_email = EmailMessage(mail_subject, email_body, to=[to_email])
            send_email.send()

            messages.success(request, 'Password Reset link has been sent to your email address.')
            return redirect('login')
        
        else:
            messages.error(request, 'Sorry!! Account does not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        # Decode Uid and get the primary key of user
        uid = urlsafe_base64_decode(uidb64).decode()

        # Get the user now that you have decoded the PK
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Save the uid from the current session
        request.session['uid'] = uid
        messages.success(request, 'Please Reset Your Password')
        return redirect('resetPassword')
    
    else:
        messages.error(request, 'This link has been expired.')
        return redirect('forgotPassword')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            # Get the Uid we have saved in the session inside 'resetpassword_validate' method
            uid = request.session.get('uid')

            # Capture the user from its Uid
            user = Account.objects.get(pk=uid)

            # Set/overwrite the New password using Django's built-in method 'set_password()
            user.set_password(password)
            user.save()

            messages.success(request, 'Your password have been changed successfully!!')
            return redirect('login')

        else:
            messages.error(request, 'Passwords do not match!! Try Again.')
            return redirect('resetPassword')
    return render(request, 'accounts/resetPassword.html')