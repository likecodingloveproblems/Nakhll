from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from url_redirector.models import Url

# Create your views here.


class Redirector(RedirectView):
    """The main view which gets the URL code and redirects to the destination URL.

    In case the URL code is not found in the database, the user is redirected to the homepage.
    """

    def get_redirect_url(self, *args, **kwargs):
        url_code = kwargs.get('url_code')
        url_object = get_object_or_404(Url, url_code=url_code)
        if url_object.destination_url:
            if not url_object.destination_url.endswith('/'):
                url_object.destination_url += '/'
            return url_object.destination_url
        return 'https://nakhll.com/'
