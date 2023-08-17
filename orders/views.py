from datetime import datetime, date

import sweetify
from django.http import JsonResponse
from django.shortcuts import redirect, render
from carts.models import CartProduct, Cart
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .forms import OrderForm
from .models import Order, Payment, ProductOrdered
import json
from store.models import Product
from django.contrib.auth.decorators import login_required


# Create your views here.


def payments(request):
    # accessing the payment details passed from front end
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user=request.user, order_number=body['orderID'], is_ordered=False)

    # assigning those payment details to the payment object in the backend
    payment = Payment(
        user=request.user,
        payment_id=body['transactionID'],
        payment_method=body['payment_method'],
        amount=order.total,
        payment_status=body['payment_status']
    )

    # this payment objects will be recorded in the db.
    payment.save()
    # update our order model's field called payment after creating new payment obj.
    order.payment = payment
    # then we update the status of order to 'True' after assigning the payment obj to order obj.
    order.is_ordered = True
    order.save()

    # Move the ordered cart_products to Product_Ordered table
    cart_products = CartProduct.objects.filter(user=request.user)

    for single_cart_product in cart_products:
        # created an obj of ProductOrdered
        order_product = ProductOrdered()
        # assigning values to each fields of ProductOrdered
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = single_cart_product.product_id
        order_product.qty = single_cart_product.qty
        order_product.price = single_cart_product.product.discount_price
        order_product.ordered = True
        order_product.save()

        cart_product = CartProduct.objects.get(id=single_cart_product.id)
        product_variations = cart_product.variation.all()
        # We are getting the saved order_product instance.
        orderproduct = ProductOrdered.objects.get(id=order_product.id)
        # setting the list of variations to the orderproduct
        orderproduct.variation.set(product_variations)
        orderproduct.save()

        # Reduce the no.of stock in Product table
        product = Product.objects.get(id=single_cart_product.product_id)
        product.stock -= orderproduct.qty
        product.save()

    # Once order is finished, Clear the Cart
    CartProduct.objects.filter(user=request.user).delete()

    # Send Order received email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_mail = EmailMessage(mail_subject, message, to=[to_email])
    sweetify.success(request,'Check your inbox for order details')
    send_mail.send()

    # Sending back our transactionID and order_number to sendData() method via JsonResponse
    # after assigning them to payment instance.
    data = {
        'order_number': order.order_number,
        'transactionID': payment.payment_id,
    }
    return JsonResponse(data)


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
    tax = (10 * total) / 100
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


def order_successful(request):
    order_number = request.GET.get('order_number')
    transactionID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        products_ordered = ProductOrdered.objects.filter(order=order)

        subtotal = 0
        for i in products_ordered:
            subtotal += (i.product.discount_price * i.qty)   

        payment = Payment.objects.get(payment_id=transactionID)

        context = {
            'order': order,
            'products_ordered': products_ordered,
            'payment': payment,
            'subtotal': subtotal,
        }

        return render(request, 'orders/order_successful.html', context)

    # means if somebody puts wrong payment_id or order_number in the url
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')


@login_required(login_url='login')
def order_detail(request, order_id):
    # products_ordered contains payment details and more
    ordered_products = ProductOrdered.objects.filter(order__order_number=order_id)
    # order contains order details and much more
    order = Order.objects.get(order_number=order_id)

    subtotal = 0
    for i in ordered_products:
        subtotal += (i.product.discount_price * i.qty)  

    context = {
        'ordered_products': ordered_products,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'orders/order_detail.html', context)