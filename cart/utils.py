from cart.managers import CartManager

def get_user_or_guest(request):
    user = request.user if request.user.is_authenticated else None
    guid = request.COOKIES.get('guest_unique_id')
    if user and guid:
        CartManager.convert_guest_to_user_cart(user, guid)
    return user, guid
