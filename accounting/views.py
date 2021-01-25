from io import BytesIO
from tokenize import group
from nakhll_market.models import Profile, Shop
from django.http import HttpResponse
from xlsxwriter.workbook import Workbook
from django.views import View
from braces.views import GroupRequiredMixin
# Create your views here.


class ShopManagersInformation(GroupRequiredMixin, View):
    group_required = u"accounting"

    def get(self, request):
        filename = 'shop_managers_info.xlsx'
        shops = Shop.objects.all()
        with BytesIO() as output:
            workbook = Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet(filename)
            # set factor filed
            worksheet.write_row(0, 0,
                            ['نام حجره دار',
                            'نام خانوادگی حجره دار',
                            'کدملی حجره دار',
                            'استان حجره دار',
                            'شهرستان حجره دار',
                            'شهر حجره دار',
                            'نشانی حجره دار',
                            'استان حجره',
                            'شهرستان حجره',
                            'شهر حجره',
                            'نشانی حجره',
                            ]
                )
            for row, shop in enumerate(shops):
                user = shop.FK_ShopManager
                if user:
                    first_name = user.first_name
                    last_name = user.last_name
                else:
                    first_name = None
                    last_name = None
                try:
                    profile = Profile.objects.get(FK_User=user)
                    national_code = profile.NationalCode
                    profile_state = profile.State
                    profile_big_city = profile.BigCity
                    profile_city = profile.City
                    profile_location = profile.Location
                except:
                    national_code = None
                    profile_state = None
                    profile_big_city = None
                    profile_city = None
                    profile_location = None
                
                worksheet.write_row(row+1, 0,
                [
                    first_name,
                    last_name,
                    national_code,
                    profile_state,
                    profile_big_city,
                    profile_city,
                    profile_location,
                    shop.State,
                    shop.BigCity,
                    shop.City,
                    shop.Location,
                ])

            workbook.close()

            output.seek(0)

            response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename = " + filename

            output.close()

        return response
        

class ShopManagersInformationV2(GroupRequiredMixin, View):
    group_required = u"accounting"