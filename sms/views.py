from http.client import HTTPResponse
from re import template
from django.shortcuts import render
from .services import Kavenegar

# Create your views here.
def send_message(request):
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

    receptor = request.GET.get('phone_number', '09384918664')
    print(receptor + " " + template + " " + token1)

    Kavenegar._raw_send(template, receptor, tokens)

    return HTTPResponse("success")
