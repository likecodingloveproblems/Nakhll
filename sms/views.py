"""Views for sms module"""
from http.client import HTTPResponse
from .services import Kavenegar


def send_message(request):
    """Send sms using Kavenegar API with parameters from request

        Args:
            request (HttpRequest): HttpRequest object which contains these
            parameters:
                phone_number (str): Phone number of receiver
                template (str): Template of sms which is defined in Kavenegar
                token1 (str): First token of sms, can be empty
                token2 (str): Second token of sms, can be empty
                token3 (str): Third token of sms, can be empty

        Returns:
            HTTPResponse: HTTPResponse object
    """
    template = request.GET.get('template', '')
    token1 = request.GET.get('token', '')
    token2 = request.GET.get('token2', '')
    token3 = request.GET.get('token3', '')
    tokens = {}
    if token1:
        tokens['token'] = token1
    if token2:
        tokens['token2'] = token2
    if token3:
        tokens['token3'] = token3

    receptor = request.GET.get('phone_number', '')
    Kavenegar._raw_send(template, receptor, tokens)
    return HTTPResponse("success")
