from rest_framework import serializers


def get_params_are_numeric(params):
    '''Decorator to check if params are numeric'''
    def wrapper(func):
        def inner(self, *args):
            for param in params:
                if not self.request.GET.get(param).isdigit():
                    raise serializers.ValidationError(
                        f'{param} is not a number')
            return func(self, *args)
        return inner
    return wrapper
