from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserUpdateForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib.auth.decorators import login_required
import sweetify
from carts.models import Cart, CartProduct
from carts.views import _session_id
from orders.models import Order
from django.contrib import messages
import os

# Verification mail
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
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data['email']
            username = (first_name+ ' '+last_name).lower()
            password = form.cleaned_data['password']
            user = Account.object.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone = phone
            user.is_active = True
            user.save()
            sweetify.success(request, 'You successfully registered')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'account/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_session_id(request))
                is_any_cart_product_exists = CartProduct.objects.filter(cart=cart).exists()
                print(is_any_cart_product_exists)
                if is_any_cart_product_exists:
                    cart_products = CartProduct.objects.filter(cart=cart)
                    print(cart_products)
                    for product in cart_products:
                        product.user = user
                        product.save()
            except:
                print('enters into except block')
            auth.login(request, user)
            sweetify.success(request, 'Logged In successfully')

            return redirect('dashboard')
        else:
            sweetify.error(request, 'Invalid login credentials')
    return render(request, 'account/login.html')


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    sweetify.success(request, 'You are logged out!')
    return redirect('login')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.object.filter(email=email).exists():
            user = Account.object.get(email__iexact=email)

            # RESETTING PASSWORD MAIL
            mail_subject = 'Reset your password'
            message = render_to_string('account/reset_password_email.html', {
                'user': user,
                'domain': get_current_site(request),
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()
            
            sweetify.success(request, 'Password reset email has been sent to your email address')
            return redirect('login')

        else:
            sweetify.error(request, 'Account does not exist')
            return redirect('forgot-password')
    return render(request, 'account/forgot_password.html')


def validate_reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        # 'uid' will be saved to session only when we are coming through validation email, Otherwise
        # direct access to reset_password doesn't actually work, since session won't be having a 'uid'
        request.session['uid'] = uid
        sweetify.info(request, 'Please reset your password')
        return redirect('reset-password')
    else:
        sweetify.error(request, 'The link has been expired')
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        conf_new_password = request.POST['conf_new_password']

        if new_password == conf_new_password:
             uid = request.session.get('uid')
             user = Account.object.get(pk=uid)
             user.set_password(new_password)
             user.save()
             sweetify.success(request, 'Password changed successfully.')
             return redirect('login')

        else:
            sweetify.error(request, 'Password does not match')
            return redirect('reset-password')
    return render(request, 'account/reset_password.html')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('ordered_at').filter(user=request.user, is_ordered=True)
    context = {
        'orders_count': orders.count()
    }
    return render(request, 'account/dashboard.html', context)


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.order_by('-ordered_at').filter(user=request.user, is_ordered=True)
    new = 'badge-warning'
    accepted = 'badge-info'
    completed = 'badge-success'
    cancelled = 'badge-danger'
    context = {
        'orders': orders,
        'new': new,
        'accepted': accepted,
        'completed': completed,
        'cancelled': cancelled
    }
    return render(request, 'account/my_orders.html', context)
    

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = new_user
            profile.save()
            sweetify.success(request, 'Your profile has been updated')
            redirect('edit_profile')

    else:
        # We are passing instance to see the existing data inside the form
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile
    }
    return render(request, 'account/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.object.get(username__exact=request.user.username)

        if new_password == confirm_password:
            # check_password() built in django method checks if user.password = current_password
            success = user.check_password(current_password)
            print(success)
            if success:
                user.set_password(new_password)
                user.save()
                # # To logout after changing password
                # auth.logout(request)
                sweetify.success(request, 'Password updated successfully')
                return redirect('change_password')
            else:
                sweetify.error(request, 'Invalid current_password')
        else:
            sweetify.error(request, 'Password does not match')
            return redirect('change_password')

    return render(request, 'account/change_password.html')