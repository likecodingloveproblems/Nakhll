from cart.managers import CartManager

def get_user_or_guest(request):
    user = request.user if request.user.is_authenticated else None
    guid = request.query_params.get('guid')
    if user and guid:
        CartManager.convert_guest_to_user_cart(user, guid)
    # TODO: Since the current version of adding product to cart did 
    # not use guid and use sessions instead, I should check for 
    # sessions and get and set them for now, till nextjs full deploy
    if not user and not guid:
        if not request.session or not request.session.session_key:
            request.session.save()
        guid = request.session.session_key
    return user, guid
