from django.http.response import JsonResponse

def TrackUrlHistory(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        '''
        track history url if user is not in /account/* pages, and if it is in /account/*
        ignore it
        '''
        if (
            not request.path.startswith('/account/') and\
            # check request is not ajax
            not request.is_ajax() and\
            not request.path.startswith('/ajax/') and\
            not request.path.startswith('/app/api/') and\
            # check request is not for file
            not '.' in request.path and\
            request.method == 'GET'):
            request.session['next'] = request.path
        response = get_response(request)
        return response
    return middleware