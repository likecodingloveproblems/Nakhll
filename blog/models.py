from django.utils.deconstruct import deconstructible
import random, string, os

@deconstructible
class PathAndRename():
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        rand_strings = ''.join( random.choice(string.ascii_letters+string.digits) for i in range(6))
        filename = '{}.{}'.format(rand_strings, ext)

        return os.path.join(self.path, filename)