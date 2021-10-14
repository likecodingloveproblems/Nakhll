from django.contrib import admin
from url_redirector.models import Url

# Register your models here.

@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display=('id','destination_url', 'get_new_address', 'creator', 'description')
    ordering=['id']
    exclude = ('created_at', 'updated_at', 'creator', 'url_code')
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set creator during the first save.
            obj.creator = request.user
        super().save_model(request, obj, form, change)

