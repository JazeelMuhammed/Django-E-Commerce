from .models import Cart, CartProduct
from .views import _session_id

def total_cart_count(request, cart_count=0):
        try:
            if request.user.is_authenticated:
                # returns cart_products assigned with the logged in user
                cart_products = CartProduct.objects.all().filter(user=request.user)
            else:
                # returns the cart_products present in 1st cart
                cart = Cart.objects.get(cart_id=_session_id(request))
                cart_products = CartProduct.objects.all().filter(cart=cart)

            for cart_product in cart_products:
                cart_count += cart_product.qty
        except Cart.DoesNotExist:
            cart_count = 0
        return dict(cart_count=cart_count)

