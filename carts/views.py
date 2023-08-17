import sweetify
from django.http import HttpResponse
from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartProduct
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create Views Here


def _session_id(request):
    session = request.session.session_key
    if not session:
        session = request.session.create()
    return session


def add_to_cart(request, pk):
    current_user = request.user
    # Getting the product Here
    product = Product.objects.get(pk=pk)

    # if user is authenticated
    if current_user.is_authenticated:
        # to store different variations of same product
        product_variation = []
        if request.method == 'POST':
            size = request.POST['size']
            # Getting the Product Variation Here
            try:
                variation = Variation.objects.get(product=product, size=size)
                product_variation.append(variation)
                print('product_variation', product_variation)
            except:
                pass

        # checks if any cart_products exists within the above cart
        is_cart_product_exists = CartProduct.objects.filter(product=product, user=current_user).exists()
        # if is_cart_product_exists returns True :-
        if is_cart_product_exists:
            # then get the list of that cart_products in that cart :-
            cart_product = CartProduct.objects.filter(product=product, user=current_user)
            # stores all the variations of cart_products
            existing_variation_list = []
            id = []
            for i in cart_product:
                variation_per_product = i.variation.all()
                print('variation_per_product', variation_per_product)
                existing_variation_list.append(list(variation_per_product))
                id.append(i.id)
            print('existing_variation_list', existing_variation_list)
            print(id)

            # We are checking if the current variation is inside the existing variation_list
            if product_variation in existing_variation_list:
                # to get the index of specific product_variation from existing_variation_list
                product_variation_index = existing_variation_list.index(product_variation)
                # using that index we can get the "id" of the cart_product by passing the index to list "id".
                cart_product_id = id[product_variation_index]
                item = CartProduct.objects.get(product=product, id=cart_product_id)
                item.qty += 1
                item.save()
            else:
                item = CartProduct.objects.create(product=product, qty=1, user=current_user)
                # checks for any variations exists:-
                if len(product_variation) > 0:
                    item.variation.clear()
                    # adding all the product_variations using *
                    item.variation.add(*product_variation)
                item.save()

        else:
            cart_product = CartProduct.objects.create(
                product=product,
                qty=1,
                user=current_user
            )
            if len(product_variation) > 0:
                cart_product.variation.clear()
                cart_product.variation.add(*product_variation)
            cart_product.save()
        return redirect('shopping-cart')

    # If user is not authenticated
    else:
        # to store different variations of same product
        product_variation = []
        if request.method == 'POST':
            size = request.POST['size']
            # Getting the Product Variation Here
            try:
                variation = Variation.objects.get(product=product, size=size)
                product_variation.append(variation)
                print('product_variation', product_variation)
            except:
                pass

        # Getting the Cart Here
        try:
            cart = Cart.objects.get(cart_id=_session_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_session_id(request)
            )
        cart.save()

        # checks if any cart_products exists within the above cart
        is_cart_product_exists = CartProduct.objects.filter(product=product, cart=cart).exists()
        # if is_cart_product_exists returns True :-
        if is_cart_product_exists:
            # then get the list of that cart_products in that cart :-
            cart_product = CartProduct.objects.filter(product=product, cart=cart)
            # stores all the variations of cart_products
            existing_variation_list = []
            id = []
            for i in cart_product:
                variation_per_product = i.variation.all()
                print('variation_per_product', variation_per_product)
                existing_variation_list.append(list(variation_per_product))
                id.append(i.id)
            print('existing_variation_list', existing_variation_list)
            print(id)

            # We are checking if the current variation is inside the existing variation_list
            if product_variation in existing_variation_list:
                # to get the index of specific product_variation from existing_variation_list
                product_variation_index = existing_variation_list.index(product_variation)
                # using that index we can get the "id" of the cart_product by passing the index to list "id".
                cart_product_id = id[product_variation_index]
                item = CartProduct.objects.get(product=product, id=cart_product_id)
                item.qty += 1
                item.save()
            else:
                item = CartProduct.objects.create(product=product, qty=1, cart=cart)
                # checks for any variations exists:-
                if len(product_variation) > 0:
                    item.variation.clear()
                    # adding all the product_variations using *
                    item.variation.add(*product_variation)
                item.save()

        else:
            cart_product = CartProduct.objects.create(
                cart=cart,
                product=product,
                qty=1
            )
            if len(product_variation) > 0:
                cart_product.variation.clear()
                cart_product.variation.add(*product_variation)
            cart_product.save()

    return redirect('shopping-cart')


def decrement_cart(request, pk, cart_product_id):
    product = Product.objects.get(pk=pk)

    try:
        if request.user.is_authenticated:
            cart_product = CartProduct.objects.get(user=request.user, product=product, id=cart_product_id)
        else:
            cart = Cart.objects.get(cart_id=_session_id(request))
            cart_product = CartProduct.objects.get(cart=cart, product=product, id=cart_product_id)
        if cart_product.qty > 1:
            cart_product.qty -= 1
            cart_product.save()
        else:
            cart_product.delete()
    except:
        pass
    return redirect('shopping-cart')


def remove_cart_product(request, pk, cart_product_id):
    product = Product.objects.get(pk=pk)

    if request.user.is_authenticated:
        cart_product = CartProduct.objects.get(user=request.user, product=product, id=cart_product_id)
    else:
        cart = Cart.objects.get(cart_id=_session_id(request))
        cart_product = CartProduct.objects.get(cart=cart, product=product, id=cart_product_id)

    cart_product.delete()
    return redirect('shopping-cart')


def cart(request, total=0, quantity=0, cart_products=None, final_amount=0, tax=0):
    try:
        if request.user.is_authenticated:
            cart_products = CartProduct.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_session_id(request))
            cart_products = CartProduct.objects.filter(cart=cart, is_active=True)

        for cart_product in cart_products:
            total += (cart_product.qty * cart_product.product.discount_price)
        tax = (3 * total) / 100   
        final_amount = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_products': cart_products,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'final_amount': final_amount
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_products=None):
    try:
        tax = 0
        final_amount = 0
        if request.user.is_authenticated:
            cart_products = CartProduct.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_session_id(request))
            cart_products = CartProduct.objects.filter(cart=cart, is_active=True)

        for cart_product in cart_products:
            total += (cart_product.qty * cart_product.product.discount_price)
            quantity += cart_product.qty
        tax = (3 * total) / 100
        final_amount = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_products': cart_products,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'final_amount': final_amount
    }
    return render(request, 'store/checkout.html', context)

