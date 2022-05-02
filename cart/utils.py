from cart.managers import CartManager


def get_user_or_guest(request):
    """Return user if there is one logged in, otherwise return guest id

    If user is logged in and also guid is in the request, we convert the
        guest cart to user cart, which may require merging the carts if
        there is a cart with items in it for logged in user.

    Args:
        request (HttpRequest): django request object

    Returns:
        tuple(user, guid): each can be None, or both can contain value

    """
    user = request.user if request.user.is_authenticated else None
    guid = request.COOKIES.get('guest_unique_id')
    if user and guid:
        CartManager.convert_guest_to_user_cart(user, guid)
    return user, guid
