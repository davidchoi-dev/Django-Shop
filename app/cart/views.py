from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .models import Cart, CartItem
from shop.models import Product


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, __ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_item, is_created = CartItem.objects.get_or_create(
        product=product,
        cart=cart,
        defaults={
            'quantity': '1',
        },
    )

    if not is_created and cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart:cart_detail')


def cart_detail(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'counter': counter,
    }

    return render(request, 'cart.html', context)


def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(
        product=product,
        cart=cart,
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart:cart_detail')


def full_remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(
        product=product,
        cart=cart,
    )

    cart_item.delete()

    return redirect('cart:cart_detail')
