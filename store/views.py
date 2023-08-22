from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from category.models import Club
from django.views.generic import DetailView

from .models import Product, ProductReview, Variation, WishListProduct, UserWishList, ProductImage
from carts.models import Cart, CartProduct
from carts.views import _session_id
from django.core.paginator import Paginator
from .forms import ProductReviewForm
import sweetify
from django.shortcuts import get_object_or_404

from orders.models import ProductOrdered


# Create your views here.


def store(request, club_slug=None, maradona_slug=None):
    club = None
    product = None
    if club_slug is not None:
        try:
            club = Club.objects.get(slug=club_slug)
        except Club.DoesNotExist:
            raise Http404('Given club not found')
        products = Product.objects.filter(club=club, is_available=True)
        paginator = Paginator(products, 6)
        page_number = request.GET.get('page')
        page_products = paginator.get_page(page_number)
        products_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_products = paginator.get_page(page_number)
        products_count = products.count()

    context = {
        'products': page_products,
        'products_count': products_count,
    }
    return render(request, 'store/store.html', context)


def category(request, size):
    vars = Variation.objects.values('size').distinct()
    sizes = [i['size'] for i in vars]
    variation_products = Variation.objects.all()

    variations = Variation.objects.all().filter(size=size)
    context = {
        'sizes': sizes,
        'variation_products': variation_products,
        'variations': variations
    }
    return render(request, 'store/variation.html', context)


def retro_store(request):
    retro = Product.objects.all().filter(type='retro' or 'iconic', is_available=True).order_by('?')
    iconic = Product .objects.all().filter(type='iconic', is_available=True).order_by('?')
    retro_products = retro | iconic

    paginator = Paginator(retro_products, 9)
    page_number = request.GET.get('page')
    page_products = paginator.get_page(page_number)

    products_count = retro_products.count()
    context = {
        'retro_products': page_products,
        'products_count': products_count,
    }
    return render(request, 'store/retro_store.html', context)


def maradona_products(request):
    maradona = 'maradona'
    products = Product.objects.filter(slug__contains=maradona).order_by('?')
    context = {
        'products': products
    }
    return render(request, 'store/maradona.html', context)


def product_details(request, pid):

    single_product = Product.objects.get(pk=pid)
    in_cart = CartProduct.objects.filter(cart__cart_id=_session_id(request), product=single_product).exists()
    print(request.META.get('REMOTE_ADDR'))
    print('ID', single_product.id)

    if request.user.is_authenticated:

        # To check whether Log In user purchased this product
        try:
            ordered_product = ProductOrdered.objects.filter(user=request.user, product_id=single_product.id).exists()
        except ProductOrdered.DoesNotExist:
            ordered_product = None
    else:
        ordered_product = None

    # Getting Product gallery
    product_gallery = ProductImage.objects.filter(product_id=single_product.id)

    # Showing reviews, we set status because if admin wants to hide some reviews, he can put status=False
    reviews = ProductReview.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'ordered_product': ordered_product,
        'product_gallery': product_gallery,
        'reviews': reviews
    }
    return render(request, 'store/product_details.html', context)


def submit_review(request, pid):
    url = request.META.get('REMOTE_ADDR')
    if request.method == 'POST':
        review = ProductReview.objects.filter(user_id=request.user.id, product__id=pid)
        if review.exists():
            # We are passing instance because, if there is already a review by this user for this particular product
            # then, we need to update that particular review instead of creating a new one.
            form = ProductReviewForm(request.POST, instance=review)
            form.save()
            sweetify.success(request, 'Thank you! Your review has been updated.')
            # Since we must redirect to that particular product page, we use page_url
            return redirect('store')

        # If there is no Review posted by requested user
        else:
            form = ProductReviewForm(request.POST)
            if form.is_valid():
                data = ProductReview()
                data.rating = form.cleaned_data['rating']
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = pid
                data.user_id = request.user.id

                data.save()
                print(data)
                sweetify.success(request, 'Thank you! Your review has been saved.')
                return redirect('store')


def add_to_wishlist(request, pk):
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
        is_product_exists = WishListProduct.objects.filter(product=product, user=current_user).exists()
        # if is_cart_product_exists returns True :-
        if is_product_exists:
            # then get the list of that cart_products in that cart :-
            wishlist_product = WishListProduct.objects.filter(product=product, user=current_user)
            # stores all the variations of cart_products
            existing_variation_list = []
            id = []
            for i in wishlist_product:
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
                wishlist_product_id = id[product_variation_index]
                if WishListProduct.objects.get(product=product, id=wishlist_product_id).exists():
                    sweetify.info(request, 'Product already present in wishlist')
            else:
                item = WishListProduct.objects.create(product=product, user=current_user)
                # checks for any variations exists:-
                if len(product_variation) > 0:
                    item.variation.clear()
                    # adding all the product_variations using *
                    item.variation.add(*product_variation)
                item.save()

        else:
            wishlist_product = WishListProduct.objects.create(
                product=product,
                user=current_user
            )
            if len(product_variation) > 0:
                wishlist_product.variation.clear()
                wishlist_product.variation.add(*product_variation)
            wishlist_product.save()
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
            wishlist = UserWishList.objects.get(wishlist_id=_session_id(request))
        except UserWishList.DoesNotExist:
            wishlist = UserWishList.objects.create(
                wishlist_id=_session_id(request)
            )
        wishlist.save()

        # checks if any cart_products exists within the above cart
        is_product_exists = CartProduct.objects.filter(product=product, wishlist=wishlist).exists()
        # if is_cart_product_exists returns True :-
        if is_product_exists:
            # then get the list of that cart_products in that cart :-
            wishlist_product = WishListProduct.objects.filter(product=product, wishlist=wishlist)
            # stores all the variations of cart_products
            existing_variation_list = []
            id = []
            for i in wishlist_product:
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
                wishlist_product_id = id[product_variation_index]
                if WishListProduct.objects.get(product=product, id=wishlist_product_id).exists():
                    sweetify.info(request, 'Product already present in wishlist')
            else:
                item = WishListProduct.objects.create(product=product, wishlist=wishlist)
                # checks for any variations exists:-
                if len(product_variation) > 0:
                    item.variation.clear()
                    # adding all the product_variations using *
                    item.variation.add(*product_variation)
                item.save()

        else:
            wishlist_product = WishListProduct.objects.create(
                wishlist=wishlist,
                product=product,
            )
            if len(product_variation) > 0:
                wishlist_product.variation.clear()
                wishlist_product.variation.add(*product_variation)
            wishlist_product.save()

    return redirect('shopping-cart')


def users_wishlist(request, wishlist_products=None):
    try:
        if request.user.is_authenticated:
            wishlist_products = WishListProduct.objects.filter(user=request.user, is_active=True)
        else:
            wishlist = UserWishList.objects.get(wishlist_id=_session_id(request))
            wishlist_products = WishListProduct.objects.filter(wishlist=wishlist, is_active=True)

    except ObjectDoesNotExist:
        pass
    context = {
        'wishlist_products': wishlist_products,
    }
    return render(request, 'account/user_wishlist.html', context)

