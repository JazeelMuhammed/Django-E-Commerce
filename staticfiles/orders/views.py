from datetime import datetime, date

import sweetify
from django.shortcuts import redirect, render
from carts.models import CartProduct, Cart
from .forms import OrderForm
from .models import Order

# Create your views here.


def payments(request):
    return render(request, 'orders/payments.html')


def place_order(request, quantity=0, total=0):
    current_user = request.user

    # if the cart count is <= 0, then redirect back to store
    cart_products = CartProduct.objects.filter(user=current_user)
    cart_count = cart_products.count()
    if cart_count <= 0:
        return redirect('store')

    for cart_product in cart_products:
        total += (cart_product.qty * cart_product.product.discount_price)
        quantity += cart_product.qty
    tax = (3 * total) / 100
    final_amount = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the shipping info to the Order model.
            order_obj = Order()
            order_obj.user = current_user
            order_obj.first_name = form.cleaned_data.get('first_name')
            order_obj.last_name = form.cleaned_data.get('last_name')
            order_obj.email = form.cleaned_data.get('email')
            order_obj.phone = form.cleaned_data.get('phone')
            order_obj.address_1 = form.cleaned_data.get('address_1')
            order_obj.address_2 = form.cleaned_data.get('address_2')
            order_obj.country = form.cleaned_data.get('country')
            order_obj.state = form.cleaned_data.get('state')
            order_obj.city = form.cleaned_data.get('city')
            order_obj.message = form.cleaned_data.get('message')
            order_obj.total = final_amount
            order_obj.tax = tax
            order_obj.ip_address = request.META.get('REMOTE_ADDR')
            # we save here because 'id' of a model instance will only get after saving it to database
            order_obj.save()

            # Generate order number
            year = int(datetime.today().strftime('%Y'))
            d = int(datetime.today().strftime('%d'))
            month = int(datetime.today().strftime('%m'))
            dt = date(year, month, d)
            current_date = dt.strftime('%Y%m%d')
            order_number = current_date + str(order_obj.pk)
            order_obj.order_number = order_number
            order_obj.save()
            sweetify.success(request, 'Order placed successfully!')

            order = Order.objects.get(user=current_user, order_number=order_number, is_ordered=False)
            context = {
                'order': order,
                'cart_products': cart_products,
                'total': total,
                'tax': tax,
                'final_amount': final_amount
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')

